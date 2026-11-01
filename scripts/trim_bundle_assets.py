# -*- coding: utf-8 -*-
"""发布形态裁剪：产物内只保留 core 闭包动画素材（-SlimAssets 的实现）。

删的是 **产物**（dist-onedir\<name>\_internal\assets\characters\<角色>\{frameseq,
videos}\{events,random}），不是源码树——源码保持全量，随时能重建全量形态，
不用重转素材。events/random 段由角色包市场（设置 → 桌宠 → 角色与素材）
在线按需安装，与官方发布同形态。

为什么是独立脚本而不是写在 build_onedir.ps1 里：帧序列目录名
（``<clip>.g<hash>\frame_XXXX.webp``）叠上产物路径会超 ``MAX_PATH``，
PowerShell 5.1 的 Remove-Item 对 ``\\?\`` 前缀支持不稳；Python 的
shutil.rmtree 配 ``\\?\`` 前缀在任何 Windows 上都可靠。零第三方依赖。
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

TREES = ("frameseq", "videos")
EXTRAS = ("events", "random")


def _long(path: Path) -> str:
    """Windows 长路径前缀（其他平台原样返回字符串）。"""
    text = str(path)
    if sys.platform == "win32" and not text.startswith("\\\\?\\"):
        return "\\\\?\\" + text
    return text


def trim(app_dir: Path, *, trees: tuple[str, ...], extras: tuple[str, ...]) -> dict:
    characters_root = app_dir / "_internal" / "assets" / "characters"
    if not characters_root.is_dir():
        raise SystemExit(
            f"[assets] bundle characters dir missing: {characters_root}")
    removed: list[str] = []
    freed = 0
    for character in sorted(p for p in characters_root.iterdir() if p.is_dir()):
        for tree in trees:
            for extra in extras:
                target = character / tree / extra
                if not target.is_dir():
                    continue
                for p in target.rglob("*"):
                    if p.is_file():
                        try:
                            freed += p.stat().st_size
                        except OSError:
                            pass
                shutil.rmtree(_long(target))
                removed.append(target.relative_to(app_dir).as_posix())
    return {"removed": removed, "freed_bytes": freed}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-dir", required=True, help="onedir 产物目录（含 _internal）")
    parser.add_argument("--trees", default=",".join(TREES), help=f"素材树，默认 {TREES}")
    parser.add_argument("--extras", default=",".join(EXTRAS), help=f"要移除的目录，默认 {EXTRAS}")
    args = parser.parse_args()

    result = trim(
        Path(args.app_dir),
        trees=tuple(t for t in args.trees.split(",") if t),
        extras=tuple(e for e in args.extras.split(",") if e),
    )
    print(json.dumps({
        "mode": "core-closure",
        "removed": result["removed"],
        "freed_bytes": result["freed_bytes"],
        "freed_mb": round(result["freed_bytes"] / 1024 / 1024, 1),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
