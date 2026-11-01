# -*- coding: utf-8 -*-
"""可信网络下载的共用判据（角色包市场 / 清单拉取的唯一网络出口）。

历史：这些函数原住在 ``pet/updater.py``（在线更新器），本仓库转为个人版本、
远程更新功能移除后，角色包市场（``pet/pack_download.py`` / ``pet/character_packs_page.py``）
仍在复用这套白名单 + 逐跳校验，故独立成模块，行为与迁移前逐位一致。

安全契约：

- 只允许白名单里的 https 域名（GitHub / jsdelivr 三镜像 / GitHub 加速镜像）；
- 重定向逐跳校验：初始 URL 过白名单不够——重定向目标也必须 https + 白名单
  主机，不许被跳板带到别的源（镜像 host 进白名单后，这条就是防“镜像当跳板”
  的闸；内容身份由下载侧 sha256 校验兜底，镜像本身不需要可信——投毒只会
  摘要不过、换下一条）。
"""

from __future__ import annotations

import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO = 'MerZlin/dsh-pet-indesktop'
REPO_URL = f'https://github.com/{REPO}'

_TRUSTED_ASSET_HOSTS = {
    'github.com',
    'objects.githubusercontent.com',
    'github-releases.githubusercontent.com',
    'release-assets.githubusercontent.com',
    'cdn.jsdelivr.net',
    'fastly.jsdelivr.net',
    'gcore.jsdelivr.net',
    # GitHub 加速镜像（分件下载的回退线路；内容身份由 sha256 校验兜底，
    # 镜像本身不需要可信——投毒只会摘要不过、换下一条）
    'gh-proxy.com',
    'mirror.ghproxy.com',
}


class _TrustedRedirect(urllib.request.HTTPRedirectHandler):
    """逐跳校验重定向：重定向目标不在可信白名单内即中断。"""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not trusted_https_url(newurl):
            raise urllib.error.HTTPError(
                req.full_url, code, f"重定向目标不在可信白名单: {newurl}", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def trusted_urlopen(req_or_url, *, timeout: float):
    """带**逐跳重定向校验**的 urlopen（角色包清单与分件下载的统一出口）。"""
    return urllib.request.build_opener(_TrustedRedirect()).open(req_or_url, timeout=timeout)


def trusted_https_url(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(str(url))
    except ValueError:
        return False
    if parsed.scheme.lower() != 'https' or not parsed.hostname:
        return False
    host = parsed.hostname.lower().rstrip('.')
    if host in _TRUSTED_ASSET_HOSTS:
        if host.endswith('github.com') and host == 'github.com':
            return f'/{REPO}/' in parsed.path or parsed.path.startswith(f'/{REPO}/releases/')
        return True
    return False


def safe_filename(name: str) -> str:
    """把远端文件名净化成可落地的安全文件名（防路径穿越/非法字符）。"""
    value = Path(str(name)).name
    value = re.sub(r'[^A-Za-z0-9._() -]+', '_', value).strip(' .')
    return value or 'pack-part'
