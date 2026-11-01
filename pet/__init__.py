# -*- coding: utf-8 -*-
"""dsh-pet 独立桌宠（不依赖 DSH 运行时的 Windows 桌面宠物）。"""

# 版本号唯一来源：安装包版本与「关于/角色包兼容」均从这里读取。
# 个人版基线 1.0（2026-11-01）：自上游 v4.4.0 分叉，远程更新功能已移除。
__version__ = '1.0'

# 上游基线：素材/角色包管线仍与上游这一版同世代（white-v6 lossless）。
# 角色包市场的 ``app_min`` 按它判——个人版号 1.0 只是自有编号，低于上游
# 包的 app_min 不代表管线不兼容（pet/character_packs_page.app_supports）。
UPSTREAM_BASELINE = '4.4.0'
