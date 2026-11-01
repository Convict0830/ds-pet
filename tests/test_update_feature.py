# -*- coding: utf-8 -*-
"""自动更新功能的 UI/进程接线回归。

2026-11-01 晚起：设置窗的「更新」域移除（检查更新是一次性命令，按
docs/SETTINGS-CHANGE-GATES.md 准入本就不该进设置页），检查/下载/安装收进
独立小对话框 `pet/update_settings.py` 的 `UpdateDialog`，由右键菜单
「检查更新」的链路（`pet/app.py` 的 `_UpdateBridge`）弹出。
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")


def _qapp():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


def test_settings_has_version_footer_and_no_update_page(tmp_path, monkeypatch):
    import pet.modern_settings_dialog as settings_mod
    from pet.config import Config

    _qapp()
    monkeypatch.setattr(settings_mod.autostart_mod, "is_enabled", lambda: False)
    dialog = settings_mod.ModernSettingsDialog(Config(tmp_path), include_ai=False)
    try:
        labels = [dialog.sidebar.item(i).text() for i in range(dialog.sidebar.count())]
        # 「更新」域已移除：侧栏末位是「文件识别」，更新入口只剩独立对话框。
        assert "更新" not in labels
        assert labels[-1] == "文件识别"
        assert dialog.version_footer.objectName() == "settingsVersion"
        assert dialog.version_footer.text().startswith("版本 v")
        assert not hasattr(dialog, "update_page")
        assert dialog.select_page("更新") is False
    finally:
        dialog.close()


def test_update_dialog_preloads_release_and_does_not_write_config(tmp_path, monkeypatch):
    from pet.config import Config
    from pet.update_settings import UpdateDialog

    _qapp()
    config = Config(tmp_path)
    before = config.path.read_bytes() if config.path.exists() else None
    dialog = UpdateDialog(config, include_chat=False)
    # 模拟版本必须比当前 __version__ 新（版本号会随发布上涨，写死必腐坏）
    from pet import __version__ as _cur
    _parts = [int(x) for x in _cur.split(".")]
    _parts[-1] += 1
    newer = ".".join(str(x) for x in _parts)
    release = {
        "version": newer,
        "notes": "notes",
        "assets": {},
        "asset_details": {},
        "html_url": "https://github.com/Convict0830/ds-pet/releases",
    }
    dialog._on_check_finished(release)
    assert dialog.status_label.text().startswith(f"发现 v{newer}")
    after = config.path.read_bytes() if config.path.exists() else None
    assert after == before
    dialog.close()


def test_menu_check_opens_update_dialog_with_build_capability(tmp_path):
    """菜单链路发现新版本 → 弹独立 UpdateDialog；include_chat 吃构建变体真值
    （chat 模块关≠纯桌宠构建，astra 盲审 P1-2 的口径不变）。"""
    from PySide6.QtWidgets import QWidget

    from pet.app import AppShell
    from pet.config import Config

    app = _qapp()

    class _Instance:
        win = QWidget()

    shell = AppShell.__new__(AppShell)
    shell.config = Config(tmp_path)
    shell.instance = _Instance()
    shell._chat_build_capable = True
    release = {"version": "9.9.9", "notes": "n", "assets": {}, "asset_details": {}}
    try:
        shell._open_update_dialog(release)
        dialog = shell._update_dialog
        assert dialog.include_chat is True  # 模块关不送纯桌宠安装包
        assert dialog.release is release
        assert dialog.status_label.text().startswith("发现 v9.9.9")
    finally:
        dlg = getattr(shell, "_update_dialog", None)
        if dlg is not None:
            dlg.close()
            dlg.deleteLater()
        shell.instance.win.close()
        app.processEvents()


def test_settings_process_page_deep_link_is_passed(tmp_path, monkeypatch):
    from pet.app import AppShell
    from pet.config import Config

    shell = AppShell.__new__(AppShell)
    shell.config = Config(tmp_path)
    shell._settings_process_running = lambda: False
    shell._settings_launch_pending = lambda: False
    shell._install_config_watcher = lambda: None
    shell._mark_settings_child = lambda active: None
    calls = []
    monkeypatch.setattr(
        shell,
        "_launch_settings_process",
        lambda instance=None, *, page=None: calls.append((instance, page)) or True,
    )
    instance = object()
    assert shell.open_settings_process(instance, page="常规") is True
    assert calls == [(instance, "常规")]
