# -*- coding: utf-8 -*-
"""便携包打包（build_onedir.ps1 的 [2/3] 步实现，替代 Compress-Archive）。

为什么不用 ``Compress-Archive``（2026-11-01 实机故障）：
1. 它"枚举 → 压缩"两步之间不重试——枚举之后、打开写入之前文件被短暂占用
   （杀毒软件扫描刚落盘的产物是典型场景）就以 ``PermissionDenied/FileNotFound``
   中止整个打包；实测同一棵树时好时坏。
2. PS 5.1 的 ZipArchive 对超长路径与中文条目名的标志位处理不稳。

本脚本：stdlib ``zipfile``，逐文件打开（``\\?\\`` 长路径前缀）、瞬时占用重试
（3 次 × 0.5s，重试耗尽才失败，绝不静默跳过）、条目名 UTF-8 标志位（zipfile
对非 ASCII 名自动置位，解压端不再猜码页）、结构 = 产物目录内容平铺在 zip 根
（与 Compress-Archive ``-Path dir\*`` 同构，官方便携包同布局）。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import zipfile
from pathlib import Path

RETRIES = 3
RETRY_DELAY_S = 0.5


def _long(path: Path) -> Path:
    """Windows 长路径前缀（幂等：已带前缀的不重复加；其他平台原样）。"""
    text = str(path)
    if sys.platform == "win32" and not text.startswith("\\\\?\\"):
        return Path("\\\\?\\" + text)
    return path


def _read_bytes(path: Path) -> bytes:
    last_error: OSError | None = None
    for attempt in range(RETRIES):
        try:
            return _long(path).read_bytes()
        except OSError as exc:  # 瞬时占用（AV 扫描/索引）重试，耗尽才抛
            last_error = exc
            time.sleep(RETRY_DELAY_S)
    raise last_error  # type: ignore[misc]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-dir", required=True, help="要打包的 onedir 产物目录")
    parser.add_argument("--out", required=True, help="目标 zip（存在先删）")
    parser.add_argument("--level", type=int, default=6,
                        help="deflate 级别 0-9，默认 6（约等于 Optimal 的性价比）")
    args = parser.parse_args()

    app_dir = Path(args.app_dir)
    if not app_dir.is_dir():
        raise SystemExit(f"[zip] app dir missing: {app_dir}")
    out = Path(args.out)
    out.unlink(missing_ok=True)

    files = sorted(p for p in _long(app_dir).rglob("*") if p.is_file())
    total_in = 0
    with zipfile.ZipFile(_long(out), "w", zipfile.ZIP_DEFLATED, compresslevel=args.level) as zf:
        for index, path in enumerate(files, 1):
            arcname = Path(path).relative_to(_long(app_dir)).as_posix()
            data = _read_bytes(path)
            zf.writestr(arcname, data)
            total_in += len(data)
            if index % 2000 == 0:
                print(f"[zip] {index}/{len(files)} files...", flush=True)

    print(json.dumps({
        "files": len(files),
        "uncompressed_mb": round(total_in / 1024 / 1024, 1),
        "zip_mb": round(out.stat().st_size / 1024 / 1024, 1),
        "zip": str(out),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
