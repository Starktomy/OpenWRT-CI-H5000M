<div align="center">

# 🚀 H5000M · ImmortalWrt 定制固件

**基于 ImmortalWrt 主线源码 · 专为 Hiveton H5000M 5G CPE 打造的自动化云编译生态**

[![ImmortalWrt Master](https://img.shields.io/badge/ImmortalWrt-master%20(Mainline)-brightgreen?logo=openwrt&logoColor=white&style=flat-square)](https://github.com/immortalwrt/immortalwrt)
[![MediaTek Filogic](https://img.shields.io/badge/Platform-MediaTek%20Filogic-FF6B35?style=flat-square)](#-一-硬件支持与固件矩阵)
[![Cellular QModem](https://img.shields.io/badge/Modem-QModem%20%7C%20Modem%20Pro-8b5cf6?style=flat-square)](#-二-模组方案对比与选型)
[![CI Build](https://img.shields.io/github/actions/workflow/status/Starktomy/OpenWRT-CI-H5000M/WRT-BUILD.yml?branch=main&label=CI%20Build&style=flat-square&logo=githubactions&logoColor=white)](https://github.com/Starktomy/OpenWRT-CI-H5000M/actions)
[![License](https://img.shields.io/badge/License-GPL--3.0-blue?style=flat-square&logo=gnu&logoColor=white)](LICENSE)

<p align="center">
  <b>适配 Hiveton H5000M（MT7987A + MT7996E + MT5700M）</b><br>
  集成 QModem Next、经典 QModem、Modem Pro、MT5700 与 MT5700M 五套独立方案，提供统一 OTA 版本选择与配置保留控制
</p>

</div>

---

## 🌟 核心特性亮点

- ⚡ **纯正官方主线与定制分支融合**：QModem 全系配置直接对接 [immortalwrt/immortalwrt](https://github.com/immortalwrt/immortalwrt) 官方 `master` 主线分支；Modem Pro 方案则基于成熟稳定的 [VIKINGYFY/immortalwrt](https://github.com/VIKINGYFY/immortalwrt) `owrt` 分支构建。
- 📶 **QModem 双前端架构**：
  - **`*-qmodem-next`（现代版）**：采用全响应式 JavaScript 现代前端，集成 `sms-forwarder-next` 短信转发中心，交互丝滑。
  - **`*-qmodem`（传统版）**：经典 LuCI 架构与深度汉化界面，配合 `sms-tool` 原生命令行工具，稳定高效。
- 🛰️ **Modem Pro 统一模组方案**：提供 `H5000M-modem-pro` 独立配置，引入 [modem-pro-unified](https://github.com/LianXia233/modem-pro-unified) 栈——由 Rust 守护进程 `modemd` 原生接管 QMI/MBIM 拨号，搭配 ucode 世代 LuCI 界面，彻底剥离 QModem 冗余组件。
- 🔄 **硬件级在线 OTA 升级 (`luci-app-online-upgrade`)**：固件内置设备特征唯一锚点，自动识别并匹配对应 Release，同驱动同方案可选保留配置，跨驱动或方案强制清空，内置国内加速镜像。
- ❄️ **CPE 专属硬件控制套件**：集成 CPU + 基带双温区风扇 PWM 阶梯调速、网络模式秒级切换与双链路故障倒换。

---

## 🎯 一、 硬件支持与固件矩阵

| 目标机型 | 平台架构 / 核心 SoC | 硬件形态与特性 | Wi-Fi 驱动栈 | 源码基线与分支 |
| :--- | :--- | :--- | :---: | :--- |
| **`H5000M`** | MediaTek Filogic (MT7987A + MT7996E) | Hiveton H5000M 5G CPE（鼎桥 MT5700M） | ✅ Wi-Fi 7 (BE) | QModem: `immortalwrt` (`master`)<br>Modem Pro / MT5700 / MT5700M: `VIKINGYFY` (`owrt`) |

### 固件产物命名规则

Release 产物统一按 `机型-模组插件-编译日期[-镜像类型].扩展名` 命名：
`机型-模组插件` 即编译配置名 `WRT_CONFIG`（如 `H5000M-qmodem-next`），
编译日期取构建当天 `YYYYMMDD`（`Asia/Shanghai`）。仅凭文件名即可分辨同机型的
QModem Next / QModem / Modem Pro / MT5700 / MT5700M 五套方案，无需再对照 Release 标签。

**Release 只发布可直接刷写的完整固件**，命名示例：

| 产物 | 文件名示例 |
| :--- | :--- |
| MTK sysupgrade 固件（Next） | `H5000M-qmodem-next-20261109-sysupgrade.bin` |
| MTK sysupgrade 固件（传统版） | `H5000M-qmodem-20261109-sysupgrade.bin` |
| MTK sysupgrade 固件（Modem Pro） | `H5000M-modem-pro-20261109-sysupgrade.bin` |
| MTK sysupgrade 固件（MT5700） | `H5000M-mt5700-20261116-sysupgrade.bin` |
| MTK sysupgrade 固件（MT5700M） | `H5000M-mt5700m-20261116-sysupgrade.bin` |

- 镜像类型后缀区分 `sysupgrade` 与 `factory`；
- 源码仓库、分支、`wifi-yes` 与精确到秒的时间戳不再塞进文件名，仍完整保留在
  Release 标签与描述中；
- Release 标签格式不变：`<配置名>-<源码owner>-<分支>-<YY.MM.DD-HH.MM.SS>`。

#### 非固件文件过滤

`Package Firmware` 按镜像类型白名单精确挑选，**以下文件只留在构建机、不进 Release**：

| 类别 | 典型文件 | 不发布的原因 |
| :--- | :--- | :--- |
| 文本元数据 | `*.manifest`、`*.config.txt`、`*.buildinfo`、`*.json`、`sha256sums` | 构建期已把内核版本 / 插件列表写进 Release 描述，无需再附文件 |
| 内核 / 根文件系统散件 | `*-kernel.bin`、`*-rootfs.img.gz`、`*-rootfs.tar.gz`、`*-targz-rootfs.tar.gz` | 单独不可刷写，仅供开发者二次拼包 |
| 引导辅助小 bin | `mt798x-ram-*-bl2.bin` 等 DDR 训练辅助镜像 | 不可直接刷写；旧的「<2MB 即非固件」体积启发式会漏掉大体积辅助文件、误删小体积合法固件 |

CI 另有两道闸门兜底：打包结束前自检 `upload/` 非空且每个文件都命中固件文件名
白名单，不满足即构建失败；`softprops/action-gh-release` 的 `files` 也只列白名单
glob。删除 manifest 之前已把内核版本与插件列表写入 `GITHUB_ENV`，Release 描述不受影响。

---

## ⚙️ 默认出厂网络配置

系统出厂参数由 [`Config/OWRT-DEFAULT.txt`](./Config/OWRT-DEFAULT.txt) 声明管理，可在编译时直接读取注入：

| 配置项 | 默认出厂值 | 说明 |
| :--- | :--- | :--- |
| **后台管理地址** | `192.168.10.1` | Web 管理页面 IPv4 入口 |
| **管理登录账号/密码** | `root` / **空（无密码）** | 首次进入后建议设置强密码 |
| **系统主机名** | `OWRT` | 本地局域网主机标识符 |
| **默认 Wi-Fi SSID** | `OWRT` | 2.4G 与 5G 双频合一名称 |
| **默认 Wi-Fi 密钥** | `12345678` | WPA/WPA2 混合加密 |
| **频宽规格（WiFi 7 · H5000M）** | 2.4G `40MHz` · 5G `160MHz` | 802.11be（EHT），双频设备 5G 上限 160MHz |
| **时区与国家代码** | `CST-8` (`Asia/Shanghai`) / `CN` | 保证时钟对齐与合规无线信道 |

---

## 🧩 二、 模组方案对比与选型

针对不同用户的操作习惯与架构偏好，项目提供五套并列互斥的固件方案：

| 配置 | 模组管理 | 风扇来源 | 定时构建源码 |
|---|---|---|---|
| `H5000M-qmodem-next` | QModem Next | LianXia233 Rust 新版 | immortalwrt/master |
| `H5000M-qmodem` | 传统 QModem | FAN789 原版 | immortalwrt/master |
| `H5000M-modem-pro` | Modem Pro | FAN789 原版 | VIKINGYFY/owrt |
| `H5000M-mt5700` | LianXia233/luci-app-mt5700 | LianXia233 Rust 新版 | VIKINGYFY/owrt |
| `H5000M-mt5700m` | FAN789/luci-app-mt5700m | FAN789 原版 | VIKINGYFY/owrt |

每份固件只包含一套模组管理，避免抢占同一 AT 串口。选择 MT5700/MT5700M 指的是
两套管理插件，均用于 MT5700M 模组。QModem Next 只更换风扇插件，保留 QModem 管理。
Modem Pro 的模组管理与风扇均沿用原方案。


### 1. QModem 方案对比 (`*-qmodem-next` vs `*-qmodem`)

| 评估维度 | `*-qmodem-next`（现代版） | `*-qmodem`（传统版） |
| :--- | :--- | :--- |
| **前端架构** | 响应式现代化 JavaScript 组件，UI 流畅无重载刷新 | 经典 LuCI CBI / JS 表单页面 |
| **短消息生态** | 深度整合 `sms-forwarder-next` 现代转发中心 | 配合 `sms-tool` 与 `sms-tool_q` 基础管理 |
| **本地化方案** | 现代化模块原生国际化设计 | 完整匹配 `luci-i18n-qmodem-zh-cn` 语言包 |
| **共用核心** | 统一搭载 `qmodem` 核心引擎、`ubus-at-daemon` 与通用 QMI 驱动栈 | 同左 |
| **隔离策略** | 锁定 `kmod-usb-net-qmi-wwan`，两套前端在固件中绝不交叉混编 | 同左 |

### 2. Modem Pro 统一模组方案 (`H5000M-modem-pro`)

`H5000M-modem-pro` 是独立演进的第五套方案，完全剥离 QModem：

| 评估维度 | `*-modem-pro` 方案特征 |
| :--- | :--- |
| **支持机型** | `H5000M-modem-pro`（MT7987A） |
| **源码分支** | 基于 `VIKINGYFY/immortalwrt` 的 `owrt` 稳定分支构建 |
| **拨号与管控栈** | [modem-pro-unified](https://github.com/LianXia233/modem-pro-unified) 统一栈，单一顶层包 `modem-pro` |
| **后端引擎** | **Rust 守护进程 `modemd`**，原生处理 QMI / MBIM 协议拨号，经 netifd 协议纳管 |
| **前端交互** | ucode / JS 现代 LuCI 前端（菜单：**移动网络 → 5G 终端**），由 `modemd` 提供高性能 ubus 接口 |
| **与 QModem 关系** | **彻底剔除 QModem**：Next 前端、传统前端、通用界面与 `qmodem` 底层全数移除，零代码冗余 |
| **编译机制** | 宿主 rustup 直编（`MODEM_PRO_HOST_RUST=1`），跳过 feeds 源码编译 rust/host，秒级构建 |

---

### 3. MT5700 / MT5700M 独立方案

提供以下两套独立管理插件：

- **MT5700**：[LianXia233/luci-app-mt5700](https://github.com/LianXia233/luci-app-mt5700)，
  LuCI 与 Rust/Tokio 后端单包交付，使用新版 Rust 风扇。风扇经后端本地 RPC 获取
  模组温度，保持后端独占串口。
- **MT5700M**：[FAN789/luci-app-mt5700m](https://github.com/FAN789/luci-app-mt5700m)，
  LuCI 与原生 C 传输程序 `mt5700m-transport`，使用原版风扇。

两套均排除 QModem 与 Modem Pro；CI 检查主包、中文翻译、串口传输依赖和互斥关系。
新版风扇与 MT5700 后端先交叉编译为 aarch64 静态程序，再交给 LuCI 打包；构建时校验
架构、静态链接及安装路径，避免漏装后端或打入宿主机程序。

---

## 🛠️ 三、 核心专属套件详解

### 1. 固件在线 OTA 升级 (`luci-app-online-upgrade`)

H5000M 五套配置内置 [H5000M-OTA](https://github.com/Starktomy/H5000M-OTA) 的定制客户端，基于 LianXia233/gooyjq 的 Rust 2.6.10 版。

- **统一选择版本**：在设备 OTA 页选择开源 mt76 或厂商 SDK mt_wifi7、五套模组方案、日常/稳定通道和历史构建。目录与稳定版由 H5000M-OTA 维护。
- **同组可选保留配置**：驱动和模组方案完全相同，更新到新日期版本可选择保留；默认清空。跨驱动或跨方案必须清空，旧固件身份未知也必须清空。
- **后端执行策略**：CI 将真实驱动与方案写入 `/usr/share/h5000m/firmware.json`。刷写前再次核对目标来源；清空模式固定 `sysupgrade -n`，不恢复旧包；同组保留模式先成功备份再使用 `sysupgrade -f`。
- **持续校验**：SHA256、机型与镜像预检不因切换旧版本或重装而跳过。客户端随固件更新，禁用上游插件自升级与旧包自动重装。
- **国内下载加速**：保留代理节点和多线程分段下载调优。

[统一下载页面](https://starktomy.github.io/H5000M-OTA/) · [稳定版发布方法](https://github.com/Starktomy/H5000M-OTA#发布与保留)

已有旧固件首次迁移时，请手动下载带新 OTA 客户端的 sysupgrade，取消“保留配置”后刷入。此前发布的镜像不包含本次改造。

Rust 后端用**官方 Rust SDK**（rustup stable + `aarch64-unknown-linux-musl`）交叉编译，
链接交给 OpenWrt 工具链的交叉 `gcc`，不经过 OpenWrt SDK 自带的 rust 构建链。
H5000M 显式使用 `-C target-cpu=cortex-a53`；产物为 aarch64 静态 musl ELF，
安装路径与包 Makefile 期望的 `/usr/bin/online-upgrade` 一致。
构建期通过 `file` 检查目标架构与静态链接方式。

两种编译方式的差异（取舍已固定，不做隐式变更）：

| 维度 | 官方 Rust SDK（当前） | OpenWrt SDK 自带 rust |
| :--- | :--- | :--- |
| C 运行库 | `*-unknown-linux-musl` + OpenWrt musl sysroot，静态链接 | 同为 musl 静态链接 |
| rustc 版本 | rustup stable（随官方发布滚动） | 与 SDK 内 rust 版本绑定，通常落后 |
| panic 策略 | 由包内 `Cargo.toml` 固定 `panic = "abort"`，两条路径一致 | 同上 |
| 符号与体积 | profile 固定 `opt-level=z` / `lto` / `codegen-units=1` / `strip` | 同上 |
| 构建耗时 | 约 2~6 分钟（含依赖编译），命中缓存后增量 | 需先构建 buildroot 的 rust/host，小时级 |

因此运行时行为（ABI、静态链接、panic=abort）与原来一致，差异只在 rustc 版本
与构建耗时；不引入 glibc 依赖，也不改变安装路径与文件名。


### 2. 硬件风扇温控与多网切换
- **双温区联动风扇控制 (`luci-app-h5000m-fancontrol`)**：定时轮询 CPU 与模组硬件传感器，通过阶梯 PWM 曲线实现静音与强效散热平衡；
- **多网络智能切换 (`luci-app-h5000m-netmode`)**：支持“纯 5G”、“纯 WAN 有线”及“主备热备 / 负载均衡”三档模式，配合 `mwan3` 探针实现毫秒级容灾切流；

---

## 🚀 四、 自动化云编译指南

依托 GitHub Actions 提供全套自动化矩阵编排，无需本地交叉编译环境：

### 工作流矩阵一览

| 工作流文件 | 调度策略 | 核心职责 |
| :--- | :--- | :--- |
| **`WRT-BUILD.yml`** | 手动 `workflow_dispatch` | 自定义按需编译：选择 H5000M 模组方案（Next / 传统版 / Modem Pro / MT5700 / MT5700M），支持 `TEST=true` 生成并检查配置 |
| **`MTK-AUTO.yml`** | 双数日 05:00 清理后 / 手动 | 自动构建并并行发布 H5000M 的全部五方案固件 |
| **`Auto-Clean.yml`** | 每月双数日 05:00（北京时间） | 每种驱动 × 每套方案保留最近 3 版，清理超额 Release / Tag 和 30 天以前的 Actions 日志；支持只预览 |
| **`Cache-Clean.yml`** | 手动 | 回收 Actions 编译缓存 |

> 所有作业统一运行在 `ubuntu-26.04`。`ubuntu-latest` 自 2026-10-19 起滚动迁移到
> Ubuntu 26.04（迁移期内仍可能落到 24.04），因此显式锁定标签。上游
> `init_build_environment.sh` 仅识别到 `noble`，初始化步骤会注入兼容补丁把脚本内
> 代号映射为 `noble`，复用已验证的 GCC 13 / LLVM 23 工具链参数集，避免
> `Unsupported OS` 直接退出。

### 固件历史保留

每种无线驱动（mt76 / mt_wifi7）、每套模组方案各保留最近 **3** 个完整固件 Release，按发布时间排序；同一驱动的不同源码共用名额。当前默认矩阵为 mt76 五套，正常保留至多 15 个日常构建版本；SDK 仓库独立保留另外五套。

北京时间每月双数日（2、4、6…30 日）05:00 定时清理，成功后构建开源五套方案；SDK 仓库在单数日同一时间构建。每次固件发布成功后也执行轮换。失败构建、草稿、未完成上传和无法识别的标签不淘汰已有固件。手动运行 Auto-Clean 可勾选 `dry_run` 预览计划；手动清理不会触发整套编译，定时清理成功后继续联动 MTK-AUTO。

调度使用 `timezone: Asia/Shanghai`，按北京时间的每月日期划分单双数，不按 UTC 日期或固定 48 小时间隔；31 日与次月 1 日都由 SDK 构建。计划执行时间可能受 GitHub Actions 排队影响。

稳定版长期发布到 [Starktomy/H5000M-OTA](https://github.com/Starktomy/H5000M-OTA/releases)，固件文件和 SHA256 复制到该仓库独立保存。统一目录同时列出稳定版和两个编译仓库各组最近 3 个日常版本。

### 手动构建步骤指引

1. 登录 GitHub，进入仓库 **Actions** 页面；
2. 在左侧工作流列表选择 **`WRT-BUILD`**，点击右侧 **`Run workflow`**；
3. 选择 H5000M 模组方案配置（Next、传统版、Modem Pro、MT5700 或 MT5700M）；
4. 选择源码仓库，流水线自动匹配分支；
5. 如需输出正式固件，将 **`TEST`** 参数改为 **`false`** 即可。

---

## 📂 仓库项目结构

```text
OpenWRT-CI-H5000M/
├── .github/workflows/          # GitHub Actions 云编译流水线
│   ├── WRT-CORE.yml            # 核心编译执行引擎
│   ├── WRT-BUILD.yml           # 手动触发定制编译
│   ├── MTK-AUTO.yml            # MTK 架构定时自动发版
│   ├── Auto-Clean.yml          # 历史制品与日志轮换清理
│   └── Cache-Clean.yml         # 构建缓存回收
├── Config/                     # 模块化 Kconfig 配置文件片段
│   ├── OWRT-DEFAULT.txt        # 集中化出厂默认网络与无线参数
│   ├── GENERAL.txt             # 通用内核优化与基础插件
│   ├── QMODEM-NEXT.txt         # QModem Next 现代化前端依赖
│   ├── QMODEM.txt              # 传统 QModem 前端依赖
│   ├── MODEM-PRO.txt           # Modem Pro 统一方案依赖（禁用 QModem）
│   ├── MODEM-STANDALONE.txt    # 独立插件的互斥配置
│   ├── MT5700.txt              # 新版模组管理插件
│   ├── MT5700M.txt             # 原生 C 传输模组管理插件
│   └── H5000M-*.txt            # H5000M 各方案目标配置
├── Scripts/                    # 流水线生命周期钩子脚本
│   ├── H5000M-Profiles.sh      # 五套方案与风扇来源映射
│   ├── Prepare-Device-Packages.sh # 专用插件结构和版本检查
│   ├── Check-Device-Packages.sh   # 专用插件上游测试
│   ├── Prebuild-Device-Backends.sh # Rust 风扇与 MT5700 后端交叉编译
│   ├── Packages.sh             # 第三方 Feed 扩展源同步与锁定
│   ├── Packages-OnlineUpgrade.sh  # 在线升级插件导入（结构断言 + 行尾归一化）
│   ├── OnlineUpgradePreset.sh  # 按机型生成 /etc/config/online-upgrade
│   ├── Handles.sh              # 补丁修补、静态资源预置与依赖注入
│   └── Settings.sh             # 出厂默认 IP、Wi-Fi 与参数配置
├── index.html                  # 现代化固件发布聚合展示落地页
└── README.md                   # 固件说明文档
```

---

## 💖 致敬与鸣谢

* 🐧 **底包源码**：[immortalwrt/immortalwrt](https://github.com/immortalwrt/immortalwrt)（主线路由基石）· [VIKINGYFY/immortalwrt](https://github.com/VIKINGYFY/immortalwrt)（板级专属适配源码）
* 👤 **编译框架**：[VIKINGYFY/OpenWRT-CI](https://github.com/VIKINGYFY/OpenWRT-CI)（优秀的开源自动化云编译框架）
* 👤 **蜂窝模组与 CPE 套件**：
  - [FUjr/QModem](https://github.com/FUjr/QModem)（强大的蜂窝模组管理套件与 Next 前端生态）
  - [FAN789](https://github.com/FAN789)（H5000M 硬件风扇温控与网络模式切换套件原作者）
  - [LianXia233](https://github.com/LianXia233)（[modem-pro-unified](https://github.com/LianXia233/modem-pro-unified) 统一模组管理方案、通用解耦管理界面与在线 OTA 升级套件）

---

> 📜 **许可协议**：本项目基于 [GNU General Public License v3.0 (GPL-3.0)](LICENSE) 协议发布。
