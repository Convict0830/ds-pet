# -*- coding: utf-8 -*-
"""把上游角色包市场的素材镜像到本仓库的 GitHub Release。

个人版（2026-11-02 起）的「角色与素材」市场从本仓库取索引与分件，不再依赖
原作者仓库在线存在；原作者更新素材后，在仓库根目录重跑本脚本即可再镜像一次：

    python scripts/mirror_character_packs.py fetch  [--proxy URL]   下载上游索引与全部分件到 .cache/packs-mirror/，逐件校验 sha256
    python scripts/mirror_character_packs.py index                  由上游索引生成本仓库的 packs-index.json（URL 指向本仓库 Release + 加速镜像）
    python scripts/mirror_character_packs.py upload [--proxy URL]   创建/复用 Release assets-v1，上传分件与 packs-index.json（已存在且大小一致的跳过）
    python scripts/mirror_character_packs.py all    [--proxy URL]   依次 fetch → index → upload

之后把生成的 packs-index.json 提交到 main（jsdelivr 从 main 分支分发索引；
Release 上的同名文件是 GitHub 不可达时的第四条回退）。

凭据：GitHub token 取自 ``git credential fill``（Git Credential Manager 的缓存，
与 git push 用的是同一份），只进请求头，不打印、不落盘。``--proxy`` 只用于
直连失败后的回退，不写进仓库任何文件。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pet import __version__ as APP_VERSION  # noqa: E402
from pet.net_fetch import REPO as TARGET_REPO  # noqa: E402

SOURCE_REPO = 'MerZlin/dsh-pet-indesktop'
RELEASE_TAG = 'assets-v1'
RELEASE_NAME = '角色素材包（assets-v1）'
RELEASE_NOTES = (
    '「角色与素材」市场的在线分件（镜像自上游 MerZlin/dsh-pet-indesktop 的 assets-v1，'
    '内容与摘要逐位一致）。客户端按 packs-index.json 按需下载，每件 sha256 校验。'
)
CACHE_DIR = ROOT / '.cache' / 'packs-mirror'
INDEX_FILE = ROOT / 'packs-index.json'
UPSTREAM_INDEX_CACHE = CACHE_DIR / 'upstream-index.json'
# 与 pet/net_fetch.py 白名单一致的加速镜像（内容身份由 sha256 兜底）
MIRROR_WRAPPERS = ('https://gh-proxy.com/', 'https://mirror.ghproxy.com/')
INDEX_SOURCES = (
    f'https://fastly.jsdelivr.net/gh/{SOURCE_REPO}@main/packs-index.json',
    f'https://gcore.jsdelivr.net/gh/{SOURCE_REPO}@main/packs-index.json',
    f'https://cdn.jsdelivr.net/gh/{SOURCE_REPO}@main/packs-index.json',
    f'https://github.com/{SOURCE_REPO}/releases/download/{RELEASE_TAG}/packs-index.json',
)
API = 'https://api.github.com'
UPLOADS = 'https://uploads.github.com'
USER_AGENT = 'ds-pet-pack-mirror'


# ---------------------------------------------------------------- 网络基础
def _openers(proxy: str | None) -> list[tuple[str, urllib.request.OpenerDirector]]:
    """[直连, 代理]；没给 --proxy 就只有直连（urllib 会尊重环境变量代理）。"""
    chain = [('direct', urllib.request.build_opener())]
    if proxy:
        chain.append(('proxy', urllib.request.build_opener(
            urllib.request.ProxyHandler({'http': proxy, 'https': proxy}))))
    return chain


def _request(url: str, *, method: str = 'GET', headers: dict | None = None,
             body: bytes | None = None) -> urllib.request.Request:
    req = urllib.request.Request(url, method=method, data=body)
    req.add_header('User-Agent', USER_AGENT)
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    return req


def _fetch_json_first(urls, openers, timeout: float = 15.0):
    for url in urls:
        for label, opener in openers:
            try:
                with opener.open(_request(url), timeout=timeout) as resp:
                    return json.loads(resp.read().decode('utf-8'))
            except Exception as exc:  # noqa: BLE001 - 只报类型与主机
                print(f'  index {urllib.parse.urlparse(url).netloc} via {label}: {type(exc).__name__}')
    raise SystemExit('上游索引全部不可达')


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _download_verified(urls, expected_sha: str, expected_bytes: int, dest: Path, openers) -> None:
    """按 URL × 线路顺序尝试，流式写入并校验 sha256；不匹配即丢弃换下一条。"""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + '.part')
    for url in urls:
        for label, opener in openers:
            host = urllib.parse.urlparse(url).netloc
            try:
                digest = hashlib.sha256()
                done = 0
                started = time.time()
                with opener.open(_request(url), timeout=60) as resp, open(tmp, 'wb') as out:
                    for chunk in iter(lambda: resp.read(1 << 20), b''):
                        out.write(chunk)
                        digest.update(chunk)
                        done += len(chunk)
                        if done % (64 << 20) < (1 << 20):
                            print(f'    {done / 1048576:.0f} MB', flush=True)
                if digest.hexdigest() != expected_sha or done != expected_bytes:
                    print(f'  {host} via {label}: 校验不符（{done} bytes），换源')
                    tmp.unlink(missing_ok=True)
                    continue
                tmp.replace(dest)
                print(f'  OK {dest.name} ← {host} via {label}（{done / 1048576:.1f} MB，{time.time() - started:.0f}s）')
                return
            except Exception as exc:  # noqa: BLE001
                print(f'  {host} via {label}: {type(exc).__name__}')
                tmp.unlink(missing_ok=True)
    raise SystemExit(f'分件下载失败：{dest.name}')


# ---------------------------------------------------------------- GitHub API
def _token() -> str:
    env = dict(os.environ, GCM_INTERACTIVE='never', GIT_TERMINAL_PROMPT='0')
    proc = subprocess.run(
        ['git', 'credential', 'fill'],
        input='protocol=https\nhost=github.com\n\n',
        capture_output=True, text=True, timeout=30, env=env, check=False,
    )
    for line in proc.stdout.splitlines():
        if line.startswith('password='):
            return line.split('=', 1)[1]
    raise SystemExit('没有可用的 github.com 凭据（先用 git push 让凭据管理器缓存一次）')


def _api(method: str, url: str, token: str, openers, *, data=None,
         body: bytes | None = None, content_type: str | None = None, timeout: float = 120):
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json'}
    payload = None
    if data is not None:
        payload = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    elif body is not None:
        payload = body
        headers['Content-Type'] = content_type or 'application/octet-stream'
    last = 'unknown'
    for label, opener in openers:
        try:
            with opener.open(_request(url, method=method, headers=headers, body=payload),
                             timeout=timeout) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw[:1] in (b'{', b'[') else None)
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            try:
                return exc.code, json.loads(raw)
            except ValueError:
                return exc.code, None
        except Exception as exc:  # noqa: BLE001
            last = type(exc).__name__
            print(f'  api via {label}: {last}')
    raise SystemExit(f'GitHub API 不可达（{last}）')


def _ensure_release(token, openers) -> dict:
    code, payload = _api('GET', f'{API}/repos/{TARGET_REPO}/releases/tags/{RELEASE_TAG}', token, openers)
    if code == 200:
        print(f'复用 Release {RELEASE_TAG}（id {payload["id"]}）')
        return payload
    code, payload = _api('POST', f'{API}/repos/{TARGET_REPO}/releases', token, openers, data={
        'tag_name': RELEASE_TAG, 'target_commitish': 'main', 'name': RELEASE_NAME,
        'body': RELEASE_NOTES, 'draft': False, 'prerelease': False,
    })
    if code not in (200, 201):
        raise SystemExit(f'创建 Release 失败：HTTP {code} {str(payload)[:200]}')
    print(f'已创建 Release {RELEASE_TAG}（id {payload["id"]}）')
    return payload


def _upload_asset(token, openers, release_id: int, path: Path, existing: dict[str, dict]) -> None:
    size = path.stat().st_size
    old = existing.get(path.name)
    if old is not None:
        if int(old.get('size') or -1) == size:
            print(f'  跳过 {path.name}（已存在，大小一致）')
            return
        code, _ = _api('DELETE', f'{API}/repos/{TARGET_REPO}/releases/assets/{old["id"]}', token, openers)
        print(f'  删除旧资产 {path.name}: HTTP {code}')
    content_type = 'application/zip' if path.suffix == '.zip' else 'application/json'
    started = time.time()
    code, payload = _api(
        'POST',
        f'{UPLOADS}/repos/{TARGET_REPO}/releases/{release_id}/assets?name={urllib.parse.quote(path.name)}',
        token, openers, body=path.read_bytes(), content_type=content_type, timeout=1800,
    )
    if code not in (200, 201):
        raise SystemExit(f'上传失败 {path.name}: HTTP {code} {str(payload)[:200]}')
    remote_sha = str((payload or {}).get('digest') or '').removeprefix('sha256:')
    local_sha = _sha256_file(path)
    tag = 'sha256 一致' if remote_sha == local_sha else f'sha256 不一致！远端 {remote_sha[:12]}'
    print(f'  上传 {path.name}: HTTP {code}，{size / 1048576:.1f} MB，{time.time() - started:.0f}s，{tag}')
    if remote_sha != local_sha:
        raise SystemExit('远端摘要与本地不一致，中止')


# ---------------------------------------------------------------- 子命令
def _load_upstream_index(openers) -> dict:
    if UPSTREAM_INDEX_CACHE.is_file():
        return json.loads(UPSTREAM_INDEX_CACHE.read_text(encoding='utf-8'))
    index = _fetch_json_first(INDEX_SOURCES, openers)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    UPSTREAM_INDEX_CACHE.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return index


def _part_filename(part: dict) -> str:
    return Path(urllib.parse.urlparse(str(part['urls'][0])).path).name


def cmd_fetch(args) -> None:
    openers = _openers(args.proxy)
    index = _fetch_json_first(INDEX_SOURCES, openers)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    UPSTREAM_INDEX_CACHE.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for pack in index.get('packs', []):
        print(f'pack {pack.get("id")} {pack.get("version")}：{len(pack.get("parts", []))} 件')
        for part in pack.get('parts', []):
            dest = CACHE_DIR / _part_filename(part)
            if dest.is_file() and dest.stat().st_size == int(part['bytes']) and _sha256_file(dest) == part['sha256']:
                print(f'  已有 {dest.name}（校验通过）')
                continue
            print(f'  下载 {dest.name}（{int(part["bytes"]) / 1048576:.1f} MB）')
            _download_verified(part['urls'], part['sha256'], int(part['bytes']), dest, openers)


def cmd_index(args) -> None:
    openers = _openers(args.proxy)
    index = _load_upstream_index(openers)
    for pack in index.get('packs', []):
        # 本仓库自己的索引：准入版本按个人版版本号写（客户端另有素材基线兜底）
        pack['app_min'] = APP_VERSION
        for part in pack.get('parts', []):
            primary = f'https://github.com/{TARGET_REPO}/releases/download/{RELEASE_TAG}/{_part_filename(part)}'
            part['urls'] = [primary, *(wrap + primary for wrap in MIRROR_WRAPPERS)]
    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'已生成 {INDEX_FILE.relative_to(ROOT)}（目标仓库 {TARGET_REPO}，{sum(len(p.get("parts", [])) for p in index.get("packs", []))} 件）')


def cmd_upload(args) -> None:
    openers = _openers(args.proxy)
    if not INDEX_FILE.is_file():
        raise SystemExit('先执行 index 生成 packs-index.json')
    token = _token()
    print('token: <hidden>')
    release = _ensure_release(token, openers)
    code, assets = _api('GET', f'{API}/repos/{TARGET_REPO}/releases/{release["id"]}/assets?per_page=100', token, openers)
    existing = {a['name']: a for a in (assets or [])} if code == 200 else {}
    index = json.loads(INDEX_FILE.read_text(encoding='utf-8'))
    for pack in index.get('packs', []):
        for part in pack.get('parts', []):
            path = CACHE_DIR / _part_filename(part)
            if not path.is_file():
                raise SystemExit(f'本地没有 {path.name}，先执行 fetch')
            _upload_asset(token, openers, release['id'], path, existing)
    # 索引本身也挂一份（客户端在 jsdelivr 三镜像之后的第四条回退）；每次都刷新
    if INDEX_FILE.name in existing:
        existing[INDEX_FILE.name]['size'] = -1  # 强制走“删旧传新”
    _upload_asset(token, openers, release['id'], INDEX_FILE, existing)
    print('完成：', release.get('html_url'))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('step', choices=('fetch', 'index', 'upload', 'all'))
    parser.add_argument('--proxy', default=None, help='直连失败后回退使用的 HTTP 代理，如 http://127.0.0.1:7890')
    args = parser.parse_args(argv)
    steps = {'fetch': [cmd_fetch], 'index': [cmd_index], 'upload': [cmd_upload],
             'all': [cmd_fetch, cmd_index, cmd_upload]}[args.step]
    for step in steps:
        step(args)
    return 0


if __name__ == '__main__':
    sys.exit(main())
