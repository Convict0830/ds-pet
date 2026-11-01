# ds-pet

<p align="center">
  <img alt="平台" src="https://img.shields.io/badge/%E5%B9%B3%E5%8F%B0-Windows-8A2BE2">
  <img alt="版本" src="https://img.shields.io/badge/%E7%89%88%E6%9C%AC-%E4%B8%AA%E4%BA%BA%E7%89%88%201.0-blue">
  <img alt="动画素材" src="https://img.shields.io/badge/%E5%8A%A8%E7%94%BB-106%20%E6%AE%B5%20WebM-ff69b4">
  <a href="https://github.com/Convict0830/ds-pet/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/License-MIT-orange"></a>
</p>

一个基于 **Python + PySide6** 的独立桌面宠物：透明无边框、置顶、可拖动、角色切换、动画播放、系统托盘和可选 AI 对话能力。

## 目录

- [本地构建与分发](#本地构建与分发)
- [安装、升级与卸载](#安装升级与卸载)
- [快速开始](#快速开始)
- [功能概览](#功能概览)
- [使用教程](#使用教程)
- [AI 对话使用教程（Chat 版）](#ai-对话使用教程chat-版)
- [动画素材与自定义角色](#动画素材与自定义角色)
- [检查更新与发布新版本](#检查更新与发布新版本)
- [配置、隐私与安全](#配置隐私与安全)
- [已知限制](#已知限制)
- [项目来源与素材声明](#项目来源与素材声明)
- [许可证与致谢](#许可证与致谢)
- [开发者与贡献](#开发者与贡献)

---

## 本地构建与分发

个人版不发布到任何下载页，**产物自己构建**。项目根目录有三个双击即用的构建脚本（共用管线在 `_build_common.bat`）：

| 脚本 | 产物 | 用途 |
|---|---|---|
| `build.bat` | 全量免安装目录 + 便携 zip（约 1.9 GB / 1.66 GB） | 自己用；106 段动画全离线 |
| `build-slim.bat` | 精简免安装目录 + 便携 zip（约 550 MB / 333 MB） | 自己用；核心 11 段动画，其余在线补 |
| `build-setup.bat` | **单文件安装包 setup.exe（约 290 MB）** + 精简 zip | **发给别人** |

说明：

- 首次构建会做一次帧序列素材转换（约 20-40 分钟，一次性），之后命中缓存，重建约 10 分钟。
- 构建前会自动关闭正在运行的同名桌宠（文件占用无法覆盖）；结束后手动重新打开即可。
- 构建链自带全部门禁与冒烟测试（素材完整性、编码自检、包体瘦身、OCR/TTS 模块校验、exe 启动冒烟），失败会停在报错处。
- **精简（slim）形态**与官方发布一致：随包带核心 11 段动画（待机 / 转向 / 移动×3 / 点击回应×5 / 拖拽），其余 95 段在 **设置 → 桌宠 → 角色与素材** 在线下载（素材来自上游公开仓库，免费）。
- 想要"开箱即 106 段全离线"的分发包：把 `build.bat` 产出的全量便携 zip 直接发出去（对方解压双击即用），或自行用 `scripts/build_onedir.ps1 -Variant webm` + Inno Setup 编全量安装包。

产物都在 `dist-onedir\` 下。

## 安装、升级与卸载

### Windows：安装包（setup.exe）

1. 双击 `dsh-pet-standalone-webm-setup.exe`。如果出现 Windows SmartScreen 提示，点「更多信息 → 仍要运行」（无代码签名）。
2. 向导默认简体中文；默认安装到 `%LOCALAPPDATA%\Programs\dsh-pet-standalone-webm`（当前用户目录，**不需要管理员权限**），可自选盘符；可选创建桌面快捷方式。
3. 完成后桌宠出现在屏幕右下角，系统托盘出现常驻图标。

**常见问题**：找不到桌宠 → 看系统托盘（可能在「显示隐藏的图标」里），双击托盘图标显示/隐藏。开机自启 → 右键托盘勾选「开机自启」（写当前用户注册表 Run 键，无需管理员）；被安全软件清理时到其"启动项管理"里恢复。

### Windows：绿色版（zip 免安装）

解压到任意可写目录，双击目录里的 `dsh-pet-standalone-webm.exe` 即可运行；删除整个文件夹即卸载。绿色版与安装版是同一套 onedir 产物，行为完全一致。

### 升级

 个人版的升级有两条路：① 在线——发布新版本到本仓库 Releases 后，老版本里点「检查更新」即可自动下载安装（见[检查更新与发布新版本](#检查更新与发布新版本)）；② 本地——改源码后重跑构建脚本，再覆盖安装/覆盖解压。配置与会话在独立数据目录里，不受覆盖影响；重要改动前建议先备份数据目录。

### 卸载

- 安装版：`设置 → 应用 → 已安装的应用` → 找到 `dsh-pet-standalone (WebM)` → 卸载（会顺带清理自启项与联动插件登记）。
- 数据目录（见下）默认保留，需要彻底清除时手动删除。

### 数据目录

设置与聊天会话保存在**按变体独立**的数据目录（重装/覆盖不丢失）：

| 系统 | 数据目录 |
|---|---|
| Windows | `%APPDATA%\dsh-pet-standalone-<变体>/` |

目录名按变体分：Chat 版 `dsh-pet-standalone-webm-chat`、无 Chat 版 `dsh-pet-standalone-webm`、源码运行为 `dsh-pet-standalone`。主要内容：

```text
config.json                      # 全局设置
config-slot-0.json               # 主宠的每宠设置（多宠时另有 config-slot-N.json）
sessions/<character_id>/<session_id>.json      # 主宠会话；其它桌宠为 sessions-slot-N/
characters/                      # 在线角色包的安装位置（跨重装保留）
pet.log
```

## 快速开始

1. 桌宠默认出现在屏幕右下角，播放待机动画。
2. 右键桌宠打开菜单；**左键点击**触发互动动画，**按住拖动**可移动桌宠。
3. 首次使用建议打开「设置」：右键桌宠 → 桌宠设置（或托盘菜单 → 桌宠设置）。设置**关闭即自动保存并立即生效**（直接点 X 也保存）。
4. 让它说话：设置 → 互动 →「自言自语」（定时气泡）与「点击与音效」都在这里；点击、拖动、丢出去、拖文件给它都有不同反应。
5. 多开：右键菜单「生小肥鱼」在**同一进程**内孵出第二只，各自独立的设置、会话与位置。
6. Chat 版额外提供「AI 对话」（右键菜单）与「AI 设置」（**托盘菜单**）入口；无 Chat 版不会显示。

## 功能概览

### 桌宠窗口

- PySide6 透明、无边框、置顶窗口（无边框圆角窗口，窗外无方形背景）。
- 支持点击互动、拖动、拖动惯性、方向转向和系统托盘。
- **锁定位置** / **SHIFT+左键拖动** / **不透明度 10%–100%** 均可在设置中调整。
- 支持角色切换与角色重命名（每宠别名）；角色目录按素材自动发现。
- 右键菜单为**现代菜单**（紧凑分组 + 线性图标 + 半透明表面），主题/字体/密度/圆角可调，内容与层级可在设置里编排。
- 菜单首行彩蛋入口（欧鲸鲸，可配置）与「快捷启动」均可配置；「生小肥鱼」会孵出一只独立配置的新桌宠。
- 右键菜单提供 **DeepSeek Harness** 子菜单（启动并打开页面 / 重启服务 / 停止服务）；详见设置中的「随桌宠启动 dsh 服务」开关。
- 托盘菜单（鼠标穿透 / 开机自启）勾选状态与设置实时同步。

### 新版设置对话框

- 侧边栏 + 卡片式布局，按能力域分 10 页：常规 / 桌宠 / 互动 / 菜单 / 桌面组件 / 功能 / AI 与对话 / 自动化与联动 / 语音 / 文件识别。「桌宠」「互动」等域内再用页内标签切分同级任务。
- **关闭即自动保存并立即生效**；例外（行内写明）：`允许桌宠跨屏` 和 `直播捕获兼容` 要**重启**生效，`帧率采集权限` 要**注销/重启电脑**后生效。
- **Ctrl+F 直接搜**：回车 / ↓ / ↑ 翻命中，自动切页、展开折叠并高亮。
- 深色系统下全界面可读；彩蛋入口、菜单外观、点击音效等集中管理。
- 桌宠显示分组可调「气泡文字大小」（50–300%）。

### 动画播放

- 直接播放透明 WebM，默认素材 640×360、24fps；播放速率 0.5x–4.0x 可调。
- 动画按 `idle`、`turn`、`move`、`click`、`drag`、`random`、`events` 等目录组织。
- 支持相邻非待机动画之间的等待间隔。
- 素材懒加载 + 优先级预热；**桌宠隐藏后暂停动画解码（隐藏时 CPU 接近 0），显示时立即恢复**。

### AI 对话（Chat 版）

- **现代双栏工作台**（会话导航 + 消息画布）；**经典手机式窗口**保留可切换。
- 支持 OpenAI Chat Completions 兼容接口；自定义 API 地址、模型、超时、温度和最大输出 token。
- 支持 SSE 流式输出、多轮上下文裁剪、会话持久化、停止生成、失败重试。
- 消息支持 **Markdown 渲染**（表格、代码块、列表）；会话按角色隔离。
- API Key 优先使用系统钥匙串；钥匙串不可用时按设置回退配置文件。

### 主动识屏陪伴（Chat 版，默认关闭）

- 白名单应用切换时以桌宠口吻冒泡关怀（截图 + 前台窗口上下文 → 视觉模型）。
- 停留时长门限、闲置判定、冷却间隔、每日上限、免费模型优先、dry-run 验证模式。
- 截图仅在内存中处理并直接发送给视觉模型，不写入本地文件。

### Agent 联动（默认关闭）

- 内置 DSH 桥接插件与 Claude hooks 安装器：感知 AI Agent 状态并切换动作（开始干活 / 过程汇报 / 任务完成三种气泡反馈）。
- **DSH 富事件状态**：thinking / working / attention / error / idle 多态呈现，多会话聚合。
- **自定义联动 Agent**：在 `config.json` 的 `agent_link.custom_agents` 里声明任意 Agent，协议见 [`docs/AGENT_LINK_PROTOCOL.md`](docs/AGENT_LINK_PROTOCOL.md)。

### 看看屏幕 / DeepSeek 余额（Chat 版）

- 「看看屏幕」：截屏 + 前台窗口上下文 → 视觉模型回应，结果同步进 AI 对话会话；截图自动压缩、仅内存处理。**每次调用按视觉模型请求计费**，有 4 秒冷却。
- 「DeepSeek 余额」：查官方 `/user/balance` 接口，气泡显示；可开分钟级自动刷新。

### 其他

- **点击音效**：内置合成音，可用数据目录 `sounds/click.wav` 替换。
- **全局快捷键**（设置 → 互动 → 快捷键，默认不绑）：AI 对话 / 看看屏幕 / 截图提问三个动作，系统级组合键。
- **音乐播放器入口**：右键「音乐」子菜单按播放器给入口（网易云 / QQ / 酷狗 / 汽水）；路径可在设置中手填或自动检测。歌词取自系统媒体会话，与这里的路径无关。
- **待办提醒**：面板增删改、到期 + 提前提醒、错过静默盖戳。
- **边缘交互与彩蛋**：黄金回旋、边缘探头（±45° 探屏）、撞飞彩蛋、拖文件模拟吃掉（不真实删除文件）。
- **右键菜单编排**：显隐/移动/别名/图标/分割线可视化编辑 + 实时预览。
- **省电模式**：停止后台动画预热，降低待机 CPU 与内存。
- **单进程多开与共享解码**：多宠同进程、同角色共用一条解码链；隐藏零功耗。
- **多宠设置作用域三档**：每宠档案（角色/缩放/台词/位置…）、整窗（置顶/穿透/不透明度…）、全局（托盘/灵动岛/待办/联动…，任意一只的设置页都能改，行内标注）。
- **高级键**（编辑 `config.json` 后重启生效）：`first_frame_cache_max_mb`（默认 8）、`predict_prewarm_lead_ms`（350）、`ffmpeg_recycle_minutes`（10）。

## 使用教程

### 基本操作

| 操作 | 效果 |
|---|---|
| 左键点击桌宠 | 触发点击互动动画 |
| 按住并拖动 | 移动桌宠；松开后按方向和速度处理转向、移动或惯性；多显示器可拖到任意屏 |
| 右键桌宠 | 上下文菜单（角色 / 动画 / 设置 / 生小肥鱼…） |
| 双击托盘图标 | 显示 / 隐藏桌宠 |
| 右键托盘图标 | 设置、AI 设置、开机自启、DeepSeek Harness、退出等 |

### 换名字

默认名「半岛铁盒」写在 `assets/characters/shenshen/videos/manifest.json` 的 `name` 字段。想给某一只单独起名：右键 → 角色 →「重命名当前角色…」（每宠别名，留空恢复默认）。

### 直播捕获兼容模式

OBS / 直播姬**窗口捕获**列表里找不到桌宠时：设置 → 常规 →「直播捕获（高级）」→ 勾选「直播捕获兼容」→ **保存并重启**。重启后桌宠变为普通顶层窗口（标题「dsh-pet 桌宠」）即可被捕获；多只会先收拢为主宠（清单保留）。注意：分层透明窗口读不到 BitBlt/游戏捕获的画面（黑屏属预期），请用 OBS 的「Windows 10 窗口捕获」模式。

### 切换角色与热加载新角色

角色菜单每次打开都会重新扫描，无需重启。新角色放到外部角色目录即被发现（目录名 = 角色 ID）：

```text
characters/                          ← 外部角色根目录（exe 同目录，或 %APPDATA%\dsh-pet-standalone\characters\）
└── <新角色ID>/
    ├── manifest.json                ← 可选：角色名 / prompt / 主题色 / 动作映射
    └── videos/
        ├── idle/  turn/  move/  click/  drag/  random/ …
```

素材制作方法（绿幕 → 抠像 → 透明 WebM）见 [`docs/ASSET-PIPELINE.md`](docs/ASSET-PIPELINE.md)。

## AI 对话使用教程（Chat 版）

### 零基础快速配置

「设置 → AI 与对话 → 模型与连接」里默认就是 DeepSeek，**只需要填 API Key**：

1. 打开 <https://platform.deepseek.com>，注册 / 登录。
2. 左侧「API Keys」→「创建 API Key」，复制 `sk-` 开头的密钥（只显示一次）。
3. 回到桌宠 → 桌宠设置 → AI 与对话 → 模型与连接 → 粘贴 → 侧栏底部「保存并退出」。
4. 点「测试连接」，显示「连接成功」即可开始聊天。新账号一般有赠送额度；402 = 余额不足去充值，401/403 = Key 抄错。

### 常见错误码

| 状态码 | 含义 | 处理 |
|---|---|---|
| 401 / 403 | Key 无效或无权限 | 重新粘贴 Key |
| 402 | 余额不足 | 开放平台充值 |
| 429 | 限流 | 稍后重试 |
| 5xx | 服务端故障 | 稍后重试 |
| 连接失败 / 超时 | 地址不可达 | 检查网络与代理 |
| SSL CERTIFICATE_VERIFY_FAILED | 证书被代理拦截 | 勾选「跳过 SSL 证书验证」（仅限可信环境） |

### 对话与 system prompt

- 右键 →「AI 对话」；`Enter` 发送、`Shift+Enter` 换行；生成中可停止。
- prompt 优先级：**角色用户自定义 > 角色 manifest 的 `chat.system_prompt` > 全局默认**。
- 会话按角色隔离，支持重命名 / 置顶 / 删除 / 搜索 / 批量管理。

## 动画素材与自定义角色

- 动画源是 `assets/characters/<角色ID>/videos/`（内置角色 `shenshen`，默认显示名「半岛铁盒」，106 段 WebM）。
- **全量构建**（`build.bat`）：106 段全部随包离线可用。
- **精简构建**（`build-slim.bat` / `build-setup.bat`）：随包 11 段核心动画，其余 95 段在 **设置 → 桌宠 → 角色与素材** 在线下载（来自上游公开仓库的分件下载，支持断点续传与 sha256 校验；装完重启生效）。这是官方发布同形态。
- 角色的名称、prompt、主题色与动作映射写在角色目录的 `manifest.json`。
- 想从零做一套素材（AI 绿幕源 → 抠像 → 640×360 透明 WebM）见 [`docs/ASSET-PIPELINE.md`](docs/ASSET-PIPELINE.md)。

## 检查更新与发布新版本

**客户端怎么检查**（`pet/updater.py`，更新源 = `Convict0830/ds-pet`；更新入口只在右键/托盘菜单，设置窗里没有「更新」页——检查更新是命令不是偏好）：

1. 右键菜单或托盘菜单点「检查更新」：先查本仓库 Releases 的 `latest` API；GitHub 不可达时回退 jsdelivr 三镜像上的 `update.json`（可选文件）。
2. 版本比较用 `pet/__init__.py` 的 `__version__`（只有比它新的 tag 才提示）；已是最新则气泡提示一句。
3. 发现新版本 → 自动弹出独立的「检查更新」小窗口（版本说明 + 进度条），点「下载并安装」即下载对应变体的 `*-setup.exe`（**校验字节数 + SHA-256，不通过不装**）→ 静默运行安装器，旧版被覆盖，配置不受影响。

**怎么发一个新版本**（私人发布流程，二选一）：

- **手动**：改 `pet/__init__.py` 的版本号 → 双击 `build-setup.bat` → 在本仓库创建 Release（tag = `v<版本号>`，如 `v1.1`）→ 上传 `dist-onedir\dsh-pet-standalone-webm-setup.exe`（**文件名保持原样**，客户端按名字挑安装包）。装了旧版的用户点「检查更新」即可收到。
- **全自动**：直接推一个 `v*` tag——`.github/workflows/build-windows.yml` 会在 GitHub 上构建并自动创建 Release 上传产物（首次运行要在 CI 上转一次帧序列素材，约 30 分钟；之后有缓存）。推 tag 前记得已把版本号提交进 `pet/__init__.py`。

> 注意：Release 资产名必须是 `dsh-pet-standalone-webm-setup.exe` / `dsh-pet-standalone-webm-chat-setup.exe`；GitHub API 会自动带出文件大小与 sha256 摘要，满足客户端的完整性校验。`update.json` 只是 GitHub API 不可达时的回退清单，手动发布时可以不更（想更就把 version/urls/size/sha256 填好后提交到 main 分支）。

## 配置、隐私与安全

- API Key 不会写入日志；优先存系统钥匙串。
- 会话文件保存在本地，不做云端同步。
- 「看看屏幕」与主动识屏的截图只在内存中处理并发给你配置的模型服务商，不写入本地文件。
- 截图识字的 **OCR 不上云**：模型随包、离线运行；走网络的只有你主动选的「翻译」与「问问肥鱼」。
- **开了代理 / VPN 的用户**：歌词取词可能因系统代理超时，本地服务（TTS、DSH 联动）要求 `localhost;127.*` 绕过。逐条实测见 [`docs/NETWORK-PROXY-AND-VPN-2026-09-22.md`](docs/NETWORK-PROXY-AND-VPN-2026-09-22.md)。

## 已知限制

- 仅支持 Windows；无代码签名，首次运行 SmartScreen 可能提示，需手动放行；杀毒软件可能误报未签名的 exe / ffmpeg 组件。
- AI 对话只实现 OpenAI Chat Completions 兼容协议；不支持编辑历史消息后重发。
- 游戏帧率段（灵动岛 `fps`，默认关）在未授权采集时不显示帧数据；授权方式是设置页一次性把当前账户加入 `Performance Log Users` 组（一次 UAC），**需重新登录生效**。
- 直播捕获兼容模式下 OBS 的 BitBlt/游戏捕获仍会黑屏（分层窗口约束，见上文）。
- 系统通知走应用自绘的右下角提示气泡（未接系统原生弹窗）。
- 全屏应用（浏览器 F11 / 独占全屏游戏）会系统级盖住桌宠，退出全屏自动恢复；资源管理器重启 / DPI 变更等偶发置顶丢失由 30 秒自检自动恢复。
- 鼠标穿透开启期间桌宠不可点击；需要交互时先从托盘菜单关闭穿透。

## 项目来源与素材声明

本项目改自、源于 [PC2005-cloud/dsh-pet](https://github.com/PC2005-cloud/dsh-pet)，并由 [MerZlin/dsh-pet-indesktop](https://github.com/MerZlin/dsh-pet-indesktop) 移植为独立桌面版（本仓库即其后端的个人分叉）。桌宠的基础交互思路、动画链行为模型和部分资源组织方式来自原项目，感谢原作者的开源贡献。

DeepSeek 余额显示（气泡/小部件思路）参考了 [MeteorNOX/DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget)。

当前动画素材为上游同步的高清 WebM 资源（`assets/characters` 共 106 段）。第三方素材、组件**与随包分发的第三方二进制**（如 `resources/presentmon/` 的帧率采集后端、`resources/rapidocr_models/` 的本地 OCR 模型）的授权声明见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

## 许可证与致谢

本项目采用 **MIT License**（见仓库根目录 `LICENSE`），第三方素材与组件授权声明见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

**特别感谢**（上游项目的历史贡献者，完整名单见上游 README 与 [`docs/CHANGELOG-ARCHIVE-2026-10.md`](docs/CHANGELOG-ARCHIVE-2026-10.md)）：

- [PC2005-cloud/dsh-pet](https://github.com/PC2005-cloud/dsh-pet)：参考实现与动画素材基础。
- [MerZlin](https://github.com/MerZlin) 与贡献者 [ushio2026-alt](https://github.com/ushio2026-alt)、[klxxya](https://github.com/klxxya)、[lscatfish123-cell](https://github.com/lscatfish123-cell)、[李玉清](https://github.com/lyq1101871677-dev) 等：现代桌面体验重构、单进程多宠架构、性能与主动陪伴体系等大量主线工作。
- [MeteorNOX/DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget)：余额气泡思路参考。

## 开发者与贡献

### 源码运行

需要 Python 3.10+（上游 CI 用 3.11，实机开发验证覆盖 3.13）：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pet        # 也可直接双击 run.bat（实际执行 pythonw -m pet）
```

### 测试与验证

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
python -m pytest -q
python -m ruff check pet/ tests/ scripts/
```

工程纪律、文档索引与架构红线的权威出处是 [`AGENTS.md`](AGENTS.md) 与 [`docs/INDEX.md`](docs/INDEX.md)；本地运行/打包流程见 [`docs/DEV-HANDOVER.md`](docs/DEV-HANDOVER.md)。

### 构建

日常用根目录的三个脚本（见[本地构建与分发](#本地构建与分发)）。手动调用底层管线：

```powershell
python -m pip install -r requirements.txt pyinstaller
powershell -ExecutionPolicy Bypass -File scripts\build_onedir.ps1 -Variant webm            # 全量
powershell -ExecutionPolicy Bypass -File scripts\build_onedir.ps1 -Variant webm -SlimAssets   # 精简
```

完整的构建门与 Inno Setup 编译命令见 [`docs/ONEDIR_PACKAGING.md`](docs/ONEDIR_PACKAGING.md)。上游各版本的历史发布说明归档在 `docs/RELEASE-*.md` 与 [`docs/CHANGELOG-ARCHIVE-2026-10.md`](docs/CHANGELOG-ARCHIVE-2026-10.md)（个人版自 v1.0 起分叉，历史条目不再续写）。
