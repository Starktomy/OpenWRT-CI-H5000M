## 2026-11-17 — 所有方案移除 Samba4

- 开源及 SDK 五套方案均不再安装 Samba4 服务、客户端、工具、共享库和 LuCI 页面。
- defconfig 后检查全部 Samba4 包，防止额外配置或依赖重新引入。

## 2026-11-16 — 按北京时间单双数日错开自动构建

- 本仓库改为北京时间每月双数日 05:00 清理成功后批量编译五套方案。
- SDK 单数日、开源双数日；直接使用 `Asia/Shanghai` 调度时区，避免 UTC 跨日与月末偏移。
- 支持随时手动构建，发布成功后继续按驱动 × 方案保留最近 3 版。

## 2026-11-16 — 统一 OTA 与配置保留策略

- 从 Starktomy/H5000M-OTA 导入定制客户端子目录，提供驱动、模组方案和历史版本选择。
- 固件内置不可随普通配置备份覆盖的驱动/方案身份。同组更新可选保留，跨驱动或跨方案必须清空。
- 禁用上游插件自升级与旧包自动重装，机型、SHA256 和镜像预检始终生效。
- 日常版本各组最近 3 版；稳定版独立复制到 OTA 仓库长期保存。

# 更新日志

本文件保留 H5000M 与公共构建流程的维护记录，完整历史可查 Git 提交。

## [2026-11-16] 每种驱动、每套模组方案保留最近 3 版

- 定时和手动清理统一保留最近 3 个已发布且含完整 Sysupgrade 镜像的 Release，移除清空全部的选项。
- 按 mt76 / mt_wifi7 与五套模组方案分组；相同驱动的不同源码共用 3 个保留名额，跨分页按发布时间全局排序。
- 新固件发布成功后再次轮换当前方案，避免长期留下 4 版；失败构建不淘汰旧固件。
- 草稿、上传未完成、未知/稳定标签不进入自动删除范围；Release 删除失败时不删除它的 Tag。
- 增加预览模式与轮换回归测试；只有定时清理成功才联动批量构建，手动预览不触发固件编译。

## [2026-11-16] 整合 MT5700 / MT5700M，按方案选择风扇

- 新增 H5000M-mt5700、H5000M-mt5700m 两个独立构建选项，与既有方案合计五套。
- MT5700 接入 LianXia233/luci-app-mt5700；MT5700M 接入 FAN789/luci-app-mt5700m
  与原生 C 传输程序，分别选择中文翻译与必要运行依赖。
- QModem Next 和 MT5700 使用 LianXia233 新版 Rust 风扇；传统 QModem、Modem Pro、
  MT5700M 继续使用 FAN789 原版风扇。QModem Next 保留原模组管理，通过已有缓存读取温度。
- 统一方案映射，克隆和配置均隔离模组管理组件；defconfig 检查主包、翻译、传输依赖及互斥。
- 增加上游插件检查、Rust 后端交叉编译和架构/静态链接/安装路径校验。
- 手动入口、定时矩阵、OTA、清理分组、下载页和文档同步五套方案。
- 本地验证：五套配置合并与互斥、15 组源码/OTA 组合、固件打包及页面过滤均通过；
  风扇 Rust 测试 154 项通过，MT5700 后端 371 项通过、2 项上游忽略，MT5700M 的
  温度缓存与原生串口传输测试通过。预编译接线使用静态 aarch64 测试程序验证安装流程，
  未执行完整固件编译或实机风扇测试。

## [2026-11-16] 仓库聚焦 H5000M

- 构建目标仅保留 H5000M，既有 QModem Next、传统版与 Modem Pro 继续可选。
- 清理其他机型的配置、专用工作流、校准资产、风扇依赖与预编译脚本。
- 构建核心、OTA 和下载页只接入受支持的配置，下载页过滤其他配置的历史 Release。
- 固件只发布 Sysupgrade/Factory，Rust 后端只构建 aarch64 目标。
- 无线默认参数合并为一套 H5000M EHT 配置，文档与维护记录同步清理。
- 发布仓库改为 Starktomy/OpenWRT-CI-H5000M，下载页、OTA 默认源与文档链接同步更新。
- 修正 TEST 参数的布尔值到字符串转换，匹配可复用核心工作流的输入类型。
- 本地验证通过：工作流与脚本语法、源码选择、OTA 预设、无线默认值、固件打包、
  Release 保留分组和下载页过滤；未执行完整固件编译。

## [2026-11-15] 修复官方源 firewall4 补丁上下文漂移

官方源升级 firewall4 到 `2026.11.08~3722eadc` 后，fullcone 补丁首个 hunk
仍引用旧注释上下文，导致 prepare 失败。刷新仓库补丁的首个 hunk，保留功能改动。
WRT-CORE 仅在官方源且源码版本为 `3722eadc088c3ab81389596ca9796112b436583a`
时覆盖补丁，上游升级后自动让位。当时对指定版本的干跑与实际应用均通过。

## [2026-11-14] CI：全面适配 Ubuntu 26.04 runner

### 背景

GitHub 自 2026-10-19 起把 `ubuntu-latest` 滚动迁移到 Ubuntu 26.04（预计 11-19 完成）。
上游 `init_build_environment.sh` 的 `check_system()` 代号白名单只到 `noble`，
26.04（`resolute`）会直接报 `[ERROR] Unsupported OS, use Ubuntu 20.04 instead.`
并退出，导致全部编译作业停在初始化阶段。

### 改动

- 全部 `runs-on` 统一显式指定 `ubuntu-26.04`：迁移期内 `ubuntu-latest` 仍可能落到
  24.04，显式标签才能保证三个仓库行为一致。
- 新增 `.github/scripts/patch-init-env.py`：下载上游脚本后注入兼容补丁，把脚本内
  `VERSION_CODENAME` 由 `resolute` 映射为 `noble`，复用上游已验证的 GCC 13 /
  LLVM 23 / noble PPA 参数集；主 apt 源仍使用 runner 的 26.04 原生配置。
  补丁幂等，上游原生支持 26.04 后自动跳过。
- apt 镜像探测的代号兜底由 `noble` 改为 `resolute`。
- 取代上一条「临时固定 24.04」的方案：不再回避迁移，改为正面适配 26.04。

## [2026-11-14] CI：固定 runner 为 Ubuntu 24.04，修复 ubuntu-latest 迁移至 26.04 后的构建失败

### 背景

2026-11-14 的 定时构建批次（包括 MTK-AUTO run 43538890288）
全部 8 个矩阵作业都在 `Initialization Environment` 阶段失败。日志显示：

```text
[INFO] Checking system info...
[ERROR] Unsupported OS, use Ubuntu 20.04 instead.
```

`ubuntu-latest` 自 2026-10-19 起迁移到 Ubuntu 26.04，而上游
`init_build_environment.sh` 的 `check_system()` 只识别到 `noble`（24.04），
遇到 26.04 的 codename 直接 `exit 1`。两次重试均在同一处失败，构建无法进入
源码克隆与编译阶段。

### 改动

- `.github/workflows/` 4 处 `runs-on: ubuntu-latest` → `ubuntu-24.04`：
  `WRT-CORE.yml`（编译核心）、`WRT-BUILD.yml`（resolve）、
  `Auto-Clean.yml`、`Cache-Clean.yml`。
- 固定到上游脚本明确支持的 noble，避免 `ubuntu-latest` 后续再次漂移；
  后续上游支持新版本时再同步调整。
- `README.md` 工作流矩阵补充固定 runner 版本的说明。

### 生效范围

仅调整 CI 运行环境，源码、配置、产物命名与 Release 流程均未改动；
缓存键不含 runner 版本，已有工具链与下载缓存仍可复用。

## [2026-11-12] CI：GitHub Actions 统一升级至 Node 24 运行时

### 背景

`actions/checkout@v4` 一类引用仍声明 `node20`。GitHub 已于 2026-09-23 从托管 runner 移除 Node 20 运行时，仍声明 `node20` 的 action 会被强制跑在 Node 24 上并打印 `Node.js 20 is deprecated` 告警，属于未验证状态；本次按各 action 的 `action.yml` 逐一核对 `runs.using` 后统一升级。

### 改动

- `.github/workflows/Auto-Clean.yml`、`Cache-Clean.yml`、`WRT-CORE.yml` 共 7 处 `uses:` 升级：
  `actions/checkout@v5` → `v7`、`actions/cache/restore@v5` / `cache/save@v5` → `v6`。
- **仅改 CI 配置**：项目源码、`node-version` / `python-version` / `go-version` 等工具链版本、产物命名与 Release 流程均未改动。告警指的是 action 自身声明的运行时，不是项目构建所用的 Node 版本。
- 升级后全仓复扫 59 个工作流/Action 文件：`node20` / `node16` / `node12` 引用残留为 0，所有 YAML 均可解析。

## [2026-11-10] 优化在线升级校验与下载页资产识别

- 打包后生成固件 SHA256 表并写入 Release 正文，供在线升级按资产名校验。
- OTA tag 同时锚定配置名、源码 owner 和分支；分支中的点转义为正则字面量。
- 生成预设时检查 repo、tag、资产正则与示例产物。
- 下载页按资产名识别配置、变体和编译日期，按白名单选择主固件；增加加载状态、
  失败提示和重试入口，读取上限调整为 100 条。
- 上游版本解析仍可能将标签末尾的构建时间作为展示版本，未改动标签格式。

## [2026-11-10] 过滤 CI 非固件文件，Release 只保留完整固件

### 背景

`Package Firmware` 旧逻辑是「先全搬、再删小的」黑名单：`bin/targets` 里的文件
被兜底命令无差别搬进 `upload/`，再用 `find ./upload/ -iname "*.bin" -size -2M -delete`
按体积删小 bin，最后 `files: ./wrt/upload/*.*` 把带点的文件全部发布。

8 个 Release 共 42 个资产里，24 个不是可直接刷写的完整固件；且「小 = 非固件」
双向不可靠 —— 大体积引导辅助 bin 会漏网，小体积合法固件又会被误删。

### 改动

- 按 `IMG_SLUG` 白名单（`sysupgrade` / `factory` / `combined` / `combined-efi` /
  `image` / `image-efi`）精确挑选，非白名单文件留在 `bin/targets` 随 `make clean` 回收；
- 删除 `.config` 拷贝、兜底无差别搬运与 `<2MB` 体积过滤；
- 新增发布前自检：`upload/` 非空且每个文件命中固件文件名白名单，否则 `exit 1`；
- `softprops/action-gh-release` 的 `files` 改为显式白名单 glob，作为第二道闸门；
- `WRT_KVER` / `WRT_LIST` 仍在删除 manifest 前写入 `GITHUB_ENV`，Release 描述不受影响；
- 落地页移除 `Config` 类展示与内置兜底数据里的旧 Config 链接。

### 生效范围

现有 8 个 Release 的 24 个非固件资产已通过 API 删除，保留 18 个完整固件。
删除后旧下载直链立即失效；`firmware_pattern` 锚定的 `*-sysupgrade.bin` /
`*-combined-efi.img.gz` 未受影响，设备端 OTA 无需改动。

> 上一版（统一产物命名）条目中列出的 `*.manifest` / `*.config.txt` 命名示例
> 自此不再产出，仅作为历史记录保留。

---

## [2026-11-10] 统一 H5000M 固件产物命名

文件名加入完整配置名和上海时区编译日期，直接区分三套方案：

| 方案 | 文件名示例 |
|---|---|
| QModem Next | `H5000M-qmodem-next-20261109-sysupgrade.bin` |
| 传统 QModem | `H5000M-qmodem-20261109-sysupgrade.bin` |
| Modem Pro | `H5000M-modem-pro-20261109-sysupgrade.bin` |

源码、分支和精确到秒的构建时间保留在 Release 标签与正文。
OTA 正则同步锚定配置名和日期。旧固件需手动刷入对应 Sysupgrade 一次，
或调整升级插件的 firmware_pattern，才能匹配新命名。

## [2026-11-08] 接入在线升级 v2，Rust 后端使用官方 SDK 编译

H5000M 三套方案导入 `LianXia233/luci-app-online-upgrade` v2，使用 Rust 后端与 rpcd。
导入脚本在 defconfig 前检查结构、安装路径和自动重装守卫；预设按配置名与源码选择 Release。
后端用 rustup stable 和 `aarch64-unknown-linux-musl` 编译，链接使用 OpenWrt 工具链，
将静态产物安装到 `/usr/bin/online-upgrade`，避免编译完整 rust/host。
沿用包内 profile，指定 Cortex-A53，并缓存 Rust 依赖和编译目录。

## [2026-11-06] 镜像按批量吞吐择优，初始化支持续传重试

小范围下载命中 CDN 缓存时，峰值速度不能代表依赖包的持续吞吐。
镜像探测增加候选与最低持续速率限制；两次初始化之间重新择源、刷新索引。
脚本先下载到文件并检查体积，再通过 `sudo timeout` 限时执行，避免留下占锁的 apt 进程。
失败尝试已经下载的依赖可供下一次继续使用。

## [2026-11-06] 修复初始化阶段被 apt 下载卡死（runner 失联型失败）

### 背景

2026-11-06 的自动构建批次全部失败，包括 MTK-AUTO run 42142974224。失败注解一致：

```
The hosted runner lost communication with the server. Anything in your workflow
that terminates the runner process, starves it for CPU/Memory, or blocks its
network access can cause this error.
```

且全部停在 `Initialization Environment`（第 3 个步骤），后续步骤仍是 `pending`；
job 从 01:18 UTC 起跑了 1 小时 14 分到 3 小时 30 分不等才被判失败。这些 job 的日志
端点返回 `BlobNotFound`——runner 失联时日志没能上传，所以"失联"本身不是脚本报错。

复现与定位：11:17 UTC 重跑 `H5000M-qmodem-next` 一个 job，同样卡在初始化
（正常只需 4~5 分钟，卡了 20 分钟以上）。取消该 job 后日志可以取到，停在 apt 下载：

```
2026-11-06T11:29:34Z 0 upgraded, 303 newly installed, 0 to remove and 0 not upgraded.
2026-11-06T11:29:34Z Need to get 661 MB of archives.
2026-11-06T11:29:37Z Get:2 ... fonts-droid-fallback all 1:6.0.1r16-1.1build1 [1805 kB]
2026-11-06T11:30:23Z Get:3 ... irqbalance amd64 1.9.3-2ubuntu5 [47.5 kB]
2026-11-06T11:31:15Z Get:5 ... libfile-next-perl all 1.18-1 [17.2 kB]
2026-11-06T11:31:21Z Get:9 ... openjdk-21-jre-headless amd64 [46.5 MB]
（11:31:21 之后到 11:38:30 取消，7 分钟无任何进展）
```

47.5 kB 的单包用了 46 秒、17.2 kB 用了 51 秒，是 runner 出口网络严重降速的典型表现。
同一时刻在 `northcentralus` 地域跑一条只做初始化、带超时的诊断任务，同样的
661 MB 依赖在约 2 分钟内下完、整条初始化 5 分钟结束——说明仓库脚本与上游 feed 都正常，
问题在个别 runner（本次卡死那台在 `westus2`）的网络链路上。同一夜 `OpenWRT-CI`、
`OpenWRT-CI-H5000M` 两个仓库也是同样症状，三者共用同一个上游初始化脚本。

### 变更

`.github/workflows/WRT-CORE.yml` 的 `Initialization Environment`：

- 新增 `/etc/apt/apt.conf.d/99-ci-transfer-guard`：`Acquire::http::Timeout` /
  `Acquire::https::Timeout` 20 秒、`Acquire::Retries` 3 次、关闭 HTTP 流水线；
  下载卡住时约一分钟内即非零退出，失败点留在日志里，而不是把 job 拖到平台判失联；
- 仓库自身的 `apt purge / update / install` 全部加 `timeout`（300/300/420 秒）；
- 上游 `init_build_environment.sh` 改为先 `curl --max-time 60 --retry 3` 落盘、
  `wc -c` 校验，再以 `timeout -k 30 1200` 限时执行（原写法 `bash <(curl ...)`
  在网络卡住时会给 bash 喂空脚本，步骤反而"成功"，问题推迟到后面才炸）。

只加超时与重试，未删除任何步骤、未放宽任何校验、未改编译参数与缓存键。

### 验证

- 诊断任务（`diag/init-hang` 分支）在同一套命令下 5 分钟内跑完，退出码全为 0；
- PR 分支上用 `WRT-BUILD` 手动触发一次完整构建（见 PR 描述）。

## [2026-11-04] 修复 runner 根分区空间不足

构建目录和缓存回填共用 runner 根分区，初始化前清理不用的 SDK、工具缓存与
Docker 镜像，保留 swap，并记录磁盘余量以定位后续空间不足。

## [2026-10-31] 默认主题切换为 luci-theme-vantage（Aurora 保留为可选）

### 背景

上游 VIKINGYFY/OpenWRT-CI 已把默认主题从 aurora 改为 `anothaDev/luci-theme-vantage`
（`WRT_THEME: vantage`）。本仓库同步该做法：默认主题改为 vantage，同时**不删除**
Aurora——`luci-theme-aurora` 与 `luci-app-aurora-config` 继续编入固件，只是不再占用
默认样式，用户可在「系统 → 语言和界面」随时切回。

这里有一个与"直接改一行 WRT_THEME"不同的地方：上游切主题时并没有保留旧主题，
本仓库要保留 Aurora，于是多出两个必须显式处理的问题。

1. **配套包名不统一**。原脚本固定拼 `CONFIG_PACKAGE_luci-app-$WRT_THEME-config`，
   对 aurora 成立（`luci-app-aurora-config`），对 vantage 是
   `luci-app-vantage-config`——该包不存在。`.config` 中不存在的符号会被 defconfig
   静默丢弃，随即触发 `Scripts/check_defconfig.py` 的「请求 y 却未生效」硬断言，
   构建在 Verify Config 步骤直接失败。
2. **默认样式并非由集合依赖唯一决定**。脚本开头把
   `feeds/luci/collections/*/Makefile` 里的 `luci-theme-bootstrap` 换成
   `luci-theme-$WRT_THEME`，只能保证「该主题被安装」。真正决定默认样式的是
   `/etc/config/luci` 的 `luci.main.mediaurlbase`，而它是 conffile：sysupgrade 保留
   旧配置时该值仍是 `/luci-static/aurora`。主题包自带的
   `30_luci-theme-*` 脚本只在 `luci.themes.<Name>` 首次注册时才写 mediaurlbase，
   对"升级上来的设备"完全不生效。

### 变更

- `Scripts/Packages.sh`：新增 `UPDATE_PACKAGE "vantage" "anothaDev/luci-theme-vantage"
  "main"`。该仓库根目录不是包，内含 `luci-theme-vantage/`（主题）与
  `luci-app-vantage/`（仪表盘）两个子目录，克隆到 `package/luci-theme-vantage` 后
  由 buildroot 递归扫描注册，与 argon 的多包仓库同一形态。aurora / aurora-config
  两行保持不变。
- `Scripts/Settings.sh`：
  - 主题配套包改为白名单映射（aurora → `luci-app-aurora-config`、
    vantage → `luci-app-vantage`、argon → `luci-app-argon-config`），不再盲拼
    `-config` 后缀，杜绝写出不存在的符号。
  - `WRT_THEME != aurora` 时追加 `luci-theme-aurora` + `luci-app-aurora-config`，
    把 Aurora 作为可选主题保留在固件里。
  - 新增「默认主题种子」段：构建期生成
    `files/etc/uci-defaults/40-luci-default-theme`，其文件名字典序排在
    `30_luci-theme-*` 之后，首启动时把 `luci.main.mediaurlbase` 指向
    `/luci-static/$WRT_THEME`，并以 `luci.main.theme_seeded` 记录已种子的默认主题
    ——同一代主题只种一次，用户此后自选的主题不会被每次升级重置；日后再次更换
    默认主题时该值不等，种子会重新生效。主题目录不存在（未编入）时脚本直接退出，
    不会在配置里留下坏路径。
- `Scripts/Handles.sh`：新增 vantage 进度条标签字体修复
  （`anothaDev/luci-theme-vantage#52`，与上游 CI 同一 sed 表达式）：把
  `.cbi-progressbar::before` 的
  `font: 500 var(--fs-micro)/1.2 var(--mono)` 改为 `font: inherit; line-height: normal`，
  避免取值标签用等宽字体在窄屏/中文下被截断。补丁前先统计目标串出现次数，命中与否
  都写入日志，上游若已自行修正则自动跳过而不是静默"假修复"。
- `Config/OWRT-DEFAULT.txt`：`WRT_THEME=aurora` → `vantage`，并注明 Aurora 仍编入
  固件、仅不再默认。

### 验证

- Settings.sh 主题段在三组 `WRT_THEME` 下实跑（隔离目录，仅取该段代码）：
  `vantage` → `luci-theme-vantage` + `luci-app-vantage` + `luci-theme-aurora` +
  `luci-app-aurora-config`；`aurora` → 与改动前完全一致（两项，无重复）；
  `argon` → `luci-theme-argon` + `luci-theme-aurora` + `luci-app-aurora-config`。
- 种子脚本用桩 `uci` + 临时 `www/luci-static` 复现三种情形：未种子 → 依次
  `set luci.themes.Vantage` / `mediaurlbase` / `theme_seeded` 并 commit；
  已种子 vantage → 无任何写操作；主题未编入 → 无任何写操作。
- vantage CSS 补丁对本仓库当前上游（v1.0.11）`vantage.css` 做 dry-run：
  仅第 2673 行 `font:` 一行被替换，其余零改动。
- `luci-app-vantage` 依赖 `luci-base`、`rpcd`、`rpcd-mod-iwinfo`、`rpcd-mod-ucode`、
  `ucode-mod-{uci,ubus,fs}`，均为 immortalwrt 现成包，不引入新的构建期编译。

## [2026-10-31] 移除已被上游取代的 firewall4 补丁替换

firewall4 升到 `2026.10.29~e6f600c4` 后，上游已刷新 fullcone 补丁，仓库固定旧快照
反而产生冲突，因此移除无版本约束的覆盖。后续临时补丁应限定版本并在上游升级后让位。

## [2026-10-30] 修复 homeproxy ucode 模块导出缺失（hasForceProxyRules）

### 背景

`Scripts/homeproxy/generate_client.uc` 覆盖上游 `luci-app-homeproxy` 的同名
脚本，该版本在 `import { ... } from 'homeproxy'` 中引入了
`hasForceProxyRules`，并用它决定 `bypass_mainland_china` 模式是否启用
geoip-cn 快速旁路。但覆盖只替换了 `generate_client.uc` 与
`update_subscriptions.uc`，`homeproxy.uc` 仍来自 `VIKINGYFY/packages`，
其中并未导出该符号，构建出的固件在服务启动与订阅更新阶段直接抛：

    Syntax error: Module /etc/homeproxy/scripts/homeproxy.uc does not export 'hasForceProxyRules'

客户端配置因此无法生成，`/var/run/homeproxy/sing-box-c.json` 缺失，
代理全面失效，订阅更新以 exit code 2 退出。

### 变更

- `Scripts/Handles.sh`：在 homeproxy ucode 修复段之后新增幂等补丁逻辑，
  仅当 `generate_client.uc` 引用该符号且 `homeproxy.uc` 未导出时才追加
  实现；上游补齐后该段自动跳过，不会与上游更新冲突。
- `Scripts/homeproxy/generate_client.uc`：不做改动，保持现有覆盖版本。

### 验证

修复后 `ucode -L /etc/homeproxy/scripts -e 'import { hasForceProxyRules } from "homeproxy"'`
导入通过；`sing-box check` 无 error；无 Proxy List 时
`route_exclude_address_set` 正确输出 `["geoip-cn"]`（快速旁路生效）；
代理与直连均正常。

## [2026-10-28] UPnP 插件改用 VIKINGYFY/packages 源（miniupnpd + luci-app-upnp）

### 背景

上游 VIKINGYFY/OpenWRT-CI 于 2026-10-27 把 `miniupnpd` 与 `luci-app-upnp`
纳入其 `VIKINGYFY/packages` 仓库，并在 viking 包组中启用。本仓库同步该
做法，UPnP（IGD / PCP / NAT-PMP 端口自动映射）改用同一维护源，与上游
保持一致的版本节奏与补丁基线。

**未涉及主题**：本仓库默认主题仍为 aurora（`Config/OWRT-DEFAULT.txt` 的
`WRT_THEME=aurora`、`Packages.sh` 的 aurora / aurora-config 源、
`Handles.sh` 的 aurora 菜单样式修复均原样保留），本次不做主题相关改动。

### 改动

- `Scripts/Packages.sh`：viking 包组清理名单追加 `miniupnpd`、
  `luci-app-upnp`：

  ```diff
  -UPDATE_PACKAGE "viking" "VIKINGYFY/packages" "main" "" "axonhub gecoosac sing-box luci-app-homeproxy luci-app-timewol luci-app-wolplus luci-app-wolultra"
  +UPDATE_PACKAGE "viking" "VIKINGYFY/packages" "main" "" "axonhub gecoosac miniupnpd sing-box luci-app-homeproxy luci-app-timewol luci-app-upnp luci-app-wolplus luci-app-wolultra"
  ```

  该名单在克隆前会 `rm -rf` 掉 `../feeds/luci/`、`../feeds/packages/` 下所有
  名字匹配的目录，因此 immortalwrt feeds 自带的 `miniupnpd` /
  `luci-app-upnp` 会被清除，改用 viking 源。

### 说明

- 编译配置无需改动：`Config/GENERAL.txt` 已有
  `CONFIG_PACKAGE_luci-app-upnp=y`（在「新增实用插件」区块内），且各机型
  均会叠加 GENERAL.txt；
- `miniupnpd` 不需要单独选中：`luci-app-upnp` 的
  `LUCI_DEPENDS:=+luci-base +miniupnpd +rpcd-mod-ucode` 会自动带出；
  viking 源的 `miniupnpd` 用 `PROVIDES:=miniupnpd` + `DEFAULT_VARIANT:=1`
  定义两个变体（`miniupnpd-iptables` / `miniupnpd-nftables`），依赖
  `+miniupnpd` 会解析到默认的 **nftables 变体**，与本仓库使用
  `CONFIG_PACKAGE_kmod-nft-*`（firewall4）的栈一致；
- 版本约束自洽：`luci-app-upnp` 的
  `LUCI_EXTRA_DEPENDS:=miniupnpd (>=20261027-r7)` 与同源 `miniupnpd` 的
  `PKG_VERSION:=20261027` / `PKG_RELEASE:=7` 完全吻合，不会在 world 安装
  阶段因约束不满足而失败（与 homeproxy 的 sing-box ≥1.15.0 那类问题同构，
  此处不存在）；
- 与现有 feed 补丁修复的兼容：`WRT-CORE.yml` 的「Update Feeds」步骤中有三处
  针对 immortalwrt feeds 的 `feeds/packages/net/miniupnpd/patches/` 修复
  （移除 020 / 030、用 `Scripts/patches/miniupnpd-040-improve-logging-2.3.11.patch`
  替换 040）。这些步骤均带 `-f` 守卫，而本改动会在后续「Custom Packages」
  阶段删除整个 feeds miniupnpd 目录，故它们自动退化为 no-op，**不会报错、
  无需删除**，作为以后切回 feeds 源时的保险保留；
- viking 源的 `miniupnpd/patches/` 仅含 `010-upnp-igdv2-compat.patch` 与
  `900-miniupnpd-format-xml-to-make-some-app-happy.patch`，正是 CHANGELOG
  [2026-10-18] 条目中已独立复验「补丁链整链通过」的两个，不会复现 2.3.11
  那次的补丁失配中断；
- 配置硬断言（`Scripts/check_defconfig.py` 的 `check_requested`）会校验
  `.config.requested` 中每个 `=y` 符号在 defconfig 后仍为 y；本改动下
  `CONFIG_PACKAGE_luci-app-upnp=y` 仍可满足（包已就位、版本约束吻合），
  不会触发「配置被 defconfig 静默丢弃」报错。

## [2026-10-24] 修复目录复制、fullcone 断言与时区注入

- UPDATE_PACKAGE 的 all 分支以 `\;` 结束 find -exec，不能使用 `cp -rf {} ./ +`。
- Modem Pro 的 VIKINGYFY 源内置 fullconenat-sonic，没有独立 kmod-nft-fullcone；
  Settings 按源码能力裁剪请求，避免 defconfig 断言误报。
- zonename 的 sed 使用 `|` 分隔符，正确写入含 `/` 的 Asia/Shanghai。
- 当时验证了复制、两种 fullcone 布局、时区替换及 shell 语法。

## [2026-10-23] 加固配置断言、feed 注册和 Modem Pro 隔离

- 包脚本失败即中止，校验克隆、解包、本地 feed 注册和安装结果。
- QModem 版本处理兼容 rc.N 与 rcN；Modem Pro 从源头跳过 QModem 仓库和通用界面。
- 新增 check_defconfig.py，核对请求符号、前端互斥、短信栈、通用 QMI、Modem Pro
  隔离和 H5000M 设备 profile、专用插件。
- TEST 模式也加载 GENERAL；defconfig 前保存请求配置，随后执行硬断言。
- 补入 audio-support，移除隐藏或失效的直接请求，平台工具由设备配置管理。
- Auto-Clean 按配置名最长前缀分组，兼容不同源码的标签。

当时在 ImmortalWrt master `e695009` 上完成 feed 与 defconfig 验证：

| 配置 | 请求 y | defconfig 后 y | 结果 |
|---|---:|---:|---|
| H5000M-qmodem-next | 141 | 1125 | 通过 |
| H5000M-qmodem | 142 | 1116 | 通过 |
| H5000M-modem-pro | 133 | 1091 | 通过 |

旧 H5000M 配置的丢弃符号和缺失依赖可被检出；该次未完成全量固件编译。

## [2026-10-23] Modem Pro 切换 VIKINGYFY owrt，手动构建自动匹配分支

H5000M Modem Pro 定时构建使用 VIKINGYFY/immortalwrt 的 owrt，两套 QModem 使用官方 master。
手动选择源码后自动匹配分支：官方为 master、VIKINGYFY 为 owrt、chasey-dev 为 25.12。
结果传给 WRT-CORE 并写入运行摘要，避免手填仓库与分支组合出错。

## [2026-10-23] H5000M Modem Pro 纳入每日自动构建

H5000M-modem-pro 加入 MTK-AUTO，在 Auto-Clean 后与 Next、传统版一起发布。
沿用配置后缀选择、独立 modem_pro feed 和宿主 Rust 工具链通路。

## [2026-10-20] H5000M 新增 Modem Pro 独立配置

新增 H5000M-modem-pro 配置和手动入口。单一 modem-pro 包提供 Rust 守护进程
modemd、QMI/MBIM 拨号、netifd 协议及 LuCI 界面。
通过 MODEM-PRO.txt 排除 QModem 核心、两套前端和通用界面，保留 H5000M 风扇、
网络模式与无线默认值。后端用宿主 rustup 直编，跳过 rust/host。
当时检查了配置格式和工作流语法，完整编译留待 CI。

## [2026-10-18] miniupnpd 2.3.11 修复独立复验：补丁链整链通过（含 900 补丁）

### 背景

224ba16b0 推送后尚无构建类 run 覆盖，本次对修复做独立复现验证，
不采信提交自述，全部结论来自本地实测。

### 验证方法与结果

1. 源码真实性：下载 miniupnpd 上游 2.3.11 发布包
   （miniupnpd_2_3_11/miniupnpd-2.3.11.tar.gz），sha256 与 feed
   Makefile 的 PKG_HASH 一致（91994b12...c48678）。
2. 030 吸收确认：2.3.11 的 upnpsoap.c 第 421 行为
   `if (GETFLAG(ALLOWPRIVATEIPV4MASK))`（无 `!`），与删除 030 的
   前提一致，无功能损失。
3. 新版 040 独立干跑：纯净 2.3.11 源码上 `patch -p1 --dry-run`，
   12/12 文件零 offset、零 fuzz、零 FAILED。
4. 整链复现（CI 实际顺序 010 → 040 替换版 → 900）：
   - 010：3 hunk 成功（offset 4/66/84 行）；
   - 040 替换版：全部 hunk 成功（相对 010 有小 offset，零 FAILED）；
   - 900-miniupnpd-format-xml-to-make-some-app-happy.patch：
     33 hunk 全部成功（2 个 fuzz 2，最大 offset +231 行）。
     注意失败 run 在 030 即中断，040/900 从未在 CI 中被尝试，
     属未验证区；本次实测可通过，不存在下一个断点。
5. 补充核对：新旧 040 补丁文件覆盖 12/12 一致；仓库版补丁为纯 LF；
   WRT-CORE.yml 通过 yaml.safe_load；MTK-AUTO / WRT-BUILD
   均 `uses: ./.github/workflows/WRT-CORE.yml`，修复一处覆盖全部入口。

### 排错记录

900 补丁干跑时 upnpsoap.c 的 hunk #1/#2 无输出行，一度疑似被静默
跳过。实打应用后确认 beforebody 已正确插入 \r\n——该现象系
GNU patch 2.7.6 对零 offset 的 hunk 不打印 succeeded 行所致，
非补丁丢失。

### 待办

224ba16b0 之后仍无构建 run，CI 端到端确认待下一次定时构建
（MTK-AUTO）或手动 workflow_dispatch 完成。

## [2026-10-17] 修复 miniupnpd 2.3.11 补丁链

030-allow-private-fix.patch 已被新版源码吸收，继续应用会失败。
040-improve-logging.patch 仍需保留定制功能，但上下文改变；CI 删除过时 030，
用仓库内针对 2.3.11 刷新的 040 替换原补丁。

## [2026-10-17] 移除过时 miniupnpd 补丁

官方 packages 升级后，020-descr-filter-fix.patch 与新源码冲突。
feeds 更新后删除过时补丁，避免 prepare 阶段中断固件构建。

## [2026-10-11] 恢复 QModem 所需 input-support 门控

input-support 是当前 ImmortalWrt 中 QModem 依赖链使用的功能门控，删除后 Kconfig
会连带取消核心和 LuCI 前端。QModem 配置恢复该门控，并检查 defconfig 后的完整依赖链。

## [2026-10-11] 修复通用 QMI 选择符号，清理失效补丁

使用 `CONFIG_PACKAGE_qmodem_INCLUDE_generic-qmi-wwan=y`，与实际通用 QMI 驱动对齐。
错误符号会被 defconfig 丢弃，可能意外引入同名厂商模块。
同步清理已被上游吸收的兼容脚本，避免继续维护失效补丁。

## [2026-10-04] 修复 qmodem 主包与 LuCI 前端仍未进固件：补上 input-support 依赖

### 背景

feed（src-link）方式集成后，`tom_modem`、`libqmodem-sms`、`sms-forwarder-next`、
`sms-tool_q` 等已成功编译进固件，但 `qmodem` 主包、`luci-app-qmodem-next` /
`luci-app-qmodem` 及 `qmodem-settings` / `qmodem-smsd` 仍缺失。根因：qmodem 各 LuCI
应用与主包的 Kconfig 均声明 `depends on PACKAGE_input-support`（LuCI 的 USB 输入设备
支持包），而 `Config/QMODEM*.txt` 未启用它，导致这些符号在 defconfig 阶段被 Kconfig
静默丢弃，即便配置中显式写了 `=y` 也不生效。

### 变更

- `Config/QMODEM-NEXT.txt`：新增 `CONFIG_PACKAGE_input-support=y`；
- `Config/QMODEM.txt`：新增 `CONFIG_PACKAGE_input-support=y`（传统前端同样依赖）。

本地复现验证：启用 input-support 后重新 defconfig，`CONFIG_PACKAGE_qmodem=y`、
`CONFIG_PACKAGE_luci-app-qmodem-next=y`、`CONFIG_PACKAGE_qmodem-smsd=y`、
`CONFIG_PACKAGE_qmodem-settings=y` 全部恢复（后三者由 luci-app-qmodem-next 的
`select` 自动拉起）。

### 变更文件

- `Config/QMODEM-NEXT.txt`
- `Config/QMODEM.txt`
- `CHANGELOG.md`

## [2026-10-04] 修复 qmodem LuCI 前端仍未编译进固件：QModem 移出 package/ 避免 core 包冲突

### 背景

2026-10-03 以 src-link 注册 qmodem feed 后，后端组件（quectel-CM-5G-M 等）已进入固件，
但 `luci-app-qmodem` / `luci-app-qmodem-next` 等 LuCI 前端包仍在固件 manifest 中缺失。
根因：`UPDATE_PACKAGE "qmodem"` 仍把克隆目录放在 `package/QModem/`，OpenWrt 主包扫描
（package/Makefile 的 `builddirs`）先于 feed 注册命中 `package/QModem/application/*`、
`package/QModem/luci/*` 下的 Makefile，把 `luci-app-qmodem` / `qmodem` / `qmodem-seal`
等提前注册为 core package；随后 `feeds install` 对同名包报
`WARNING: Not overriding core package 'luci-app-qmodem'; use -f to force` 并跳过链接，
`CONFIG_PACKAGE_luci-app-qmodem*` 等符号在 defconfig 阶段被静默丢弃。

### 变更

- `Scripts/Packages.sh`：`REGISTER_QMODEM_FEED` 开头新增目录搬移——若 `package/QModem`
  存在且工作区根尚无 `QModem`，先 `mv -f ./QModem ../QModem` 把克隆目录移出 `package/`，
  再以 `src-link qmodem` 注册 feed；`QMODEM_DIR` / `QMODEM_ABS` 同步指向 `../QModem`，
  使主包扫描不再提前抢注同名包，`feeds install -a -p qmodem` 可正常把所有二级目录包
  链接到 `package/feeds/qmodem/`；
- 同步修正 `FIX_QMODEM_VERSION`（`version.mk`）与 `FIX_QMODEM_VOIP_DEP`
  （`sms_forwarder_next/Makefile`）的路径为 `../QModem/...`。

### 变更文件

- `Scripts/Packages.sh`
- `CHANGELOG.md`

## [2026-10-03] 修复 qmodem 未编译进固件：改为 OpenWrt feed（src-link）方式集成

### 背景

qmodem（FUjr/QModem）此前一直未进入固件。根因：该仓库按 OpenWrt feed（src-git）设计，
顶层没有 Makefile，包分散在 `application/`、`luci/`、`driver/` 等二级目录；而 Packages.sh
仅把仓库克隆到 `package/QModem/`，OpenWrt 的包扫描（package/Makefile 的 `builddirs`）
只认含 Makefile 的一级子目录，导致 `luci-app-qmodem` / `luci-app-qmodem-next` / `qmodem` /
`sms-forwarder-next` 等配置符号在 defconfig 阶段不存在，配置被静默丢弃。

### 变更

- `Scripts/Packages.sh`：`UPDATE_PACKAGE "qmodem" ...` 克隆后新增 `REGISTER_QMODEM_FEED`，
  将克隆目录以 `src-link qmodem` 追加进 feeds 配置（`feeds.conf` 优先于 `feeds.conf.default`），
  再增量执行 `feeds update qmodem && feeds install -a -p qmodem`，由 scripts/feeds 递归
  扫描二级目录并把各包链接到 `package/feeds/qmodem/`，仅影响 qmodem feed、不动其它 feed；
- 各包 Makefile 的 `include ../../version.mk` 相对路径在 feed 符号链接布局下仍指向 QModem
  根目录的 `version.mk`，无需改动；既有的 FIX_QMODEM_VERSION / FIX_QMODEM_VOIP_DEP
  修改的是克隆目录真实文件，对 feed 链接同样生效。

### 变更文件

- `Scripts/Packages.sh`
- `CHANGELOG.md`

## [2026-10-03] H5000M 双频统一使用 EHT

H5000M 的 2.4G/5G 默认 htmode 为 EHT40/EHT160，修复此前 2.4G 误用 HE40。

## [2026-10-01] 修复 H5000M 无线默认参数注入

为 H5000M 提供 WiFi7 的 SSID、密钥、加密、频宽和国家码默认值。
首次启动脚本使用 WRT_SSID/WRT_WORD，修复引用未定义变量而恒用兜底值的问题。

## [2026-09-30] 集中管理出厂默认配置

新增 OWRT-DEFAULT.txt，集中声明网络、无线、主题、国家码和时区。
工作流先加载默认值，再应用显式 inputs；Settings 生成首次启动无线脚本。
修复 HomeProxy 目录查找深度和主题、磁盘插件定位；配置统一 UTF-8 与 LF。

## [2026-09-29] 修复 H5000M 网络模式插件打包

插件保留 Rust src/ 却没有 src/Makefile，LuCI 跳过 Compile 但在 Install 中误执行 make。
真正发布的是 root/ 内的预编译产物，因此克隆后删除无 Makefile 的 src/，避免安装失败。

## [2026-09-25]

### 修复

- **sing-box 过时补丁导致构建失败**：今日（09-24）定时构建批次同时 `failure`，首个失败步骤均为「编译固件」。根因为 `Scripts/Packages.sh` 克隆的 viking feed（`VIKINGYFY/packages`）中 sing-box 自带 `patches/100-fix-dns-tcp-close.patch` 与 `1.15.0_alpha8` 源码上下文不匹配（补丁引入的上游从未合入的 `HandleStreamDNSConnection`，而源码仍是 `HandleStreamDNSRequest`），`Build/Prepare` 阶段应用补丁报 `Patch failed!` 并 `Error 1`，整个固件编译中断。上游 `immortalwrt/packages` 的 sing-box 根本不携带该补丁也能正常构建，故判定为可安全移除的过时补丁。已在克隆 viking feed 后新增 `FIX_SINGBOX_STALE_PATCH`：仅当补丁内容含旧版标记 `HandleStreamDNSConnection` 时移除，若 VIKINGYFY 后续刷新补丁则自动跳过、不误删。

### 变更文件

- `Scripts/Packages.sh` — 新增 `FIX_SINGBOX_STALE_PATCH`（克隆 viking feed 后清理过时 sing-box 补丁）

## [2026-09-10] 兼容 QModem 的 apk 版本格式

共享版本 3.4.0-rc.3 被新版 apk 判定为非法。Packages 将 X.Y.Z-rc.N 转为 X.Y.Z_rcN，
仅调整版本元数据；上游已经采用合法格式时自动跳过。

## [2026-08-31] 修复编译失败后的重试与诊断

默认 bash -e 与 pipefail 会让首次 make 失败立即退出，后续重试和错误注解不会执行。
编译步骤改用 set +e -o pipefail，显式捕获退出码，再执行重试与日志诊断。

## [2026-08-29] H5000M 改用 ImmortalWrt 主线

H5000M 的 QModem 构建改用官方 master，设备 profile 提供板级定义，文档与升级标签同步。

## [2026-08-29] 优化公共构建缓存

工具链按源码和平台复用，单独缓存下载目录并启用 ccache。
设置任务超时并保留缓存保存阶段，失败时提供并行重试与诊断。
Cache-Clean 改为手动触发，减少每周强制冷启动。

## [2026-08-25]

### 新增

- **TTYD Web 终端**：全机型默认集成 [ttyd](https://github.com/tsl0922/ttyd) 网页命令行终端，LuCI「系统 → TTYD 终端」页面可在浏览器直接操作设备 Shell。`Config/GENERAL.txt` 新增并默认启用 `ttyd`、`luci-app-ttyd`、`luci-i18n-ttyd-zh-cn` 三个软件包。

### 变更文件

- `Config/GENERAL.txt` — 新增 TTYD Web 终端配置段（`ttyd` / `luci-app-ttyd` / `luci-i18n-ttyd-zh-cn`，均默认启用）

## [2026-08-18]

### 修复
- **ovpn-dco 编译失败（过时补丁与上游冲突）**：最新 Actions 运行（MTK-AUTO 等定时构建）全部在 `Compile Firmware` 阶段因 `ovpn-dco` 包构建失败。`Scripts/Handles.sh` 此前会向 feeds 的 `ovpn-dco` 包注入自研补丁 `0002-fix-recvmsg-addr-len-6.18.40.patch`（修复 Linux 6.18.40+ recvmsg 兼容性），但上游 `ovpn-backports` 在 7.1.0.2026080300 版本已内置完全相同的修复（`linux-compat.h` 的 `OVPN_PROTO_RECVMSG_HAS_ADDR_LEN` 宏 + `tcp.c` 的 `#elif OVPN_PROTO_RECVMSG_HAS_ADDR_LEN`），继续注入旧补丁导致 `patch` hunk 失败（`1 out of 1 hunk FAILED`），`ERROR: package/feeds/packages/ovpn-dco failed to build`。已移除该过时补丁注入块，由上游自带修复接管。

### 变更文件
- `Scripts/Handles.sh` — 移除 ovpn-dco 0002 过时补丁注入块

## [2026-08-15] 修复 H5000M 初始化时 apt 源哈希不一致

runner 的 google-chrome 源偶发 File has unexpected size，导致 apt update 退出 100。
更新索引前移除该非必需源，并增加一次重试。

## [2026-08-12]

### 修复

- **HomeProxy ucode 兼容性修复**：ImmortalWrt master 已移除 `luci.sys.init_action` 且 ucode 不含 `math` 模块，导致订阅更新与客户端配置生成失败（sing-box 无法启动，页面报 "URLTest: 无效节点"）。在 `Scripts/Handles.sh` 中加入自动覆盖修复，CI 构建时替换上游的两个脚本：
  - `update_subscriptions.uc`：移除 `import { init_action } from 'luci.sys'`，将 `init_action('homeproxy', 'restart')` 替换为 `system('/etc/init.d/homeproxy restart >/dev/null 2>&1')`。
  - `generate_client.uc`：移除 `import { isnan } from 'math'`，将 `isnan(int(i))` 替换为 `type(int(i)) === 'double'`。
  - 修复脚本存放于 `Scripts/homeproxy/`，不包含节点信息。

## [2026-08-10]

### 新增
- **在线升级插件 `luci-app-online-upgrade`**：所有机型默认启用，支持从本仓库 GitHub Releases 在线升级固件。
- **按机型自动匹配固件**：构建时将设备身份（机型 + QModem 前端类型 + 构建标签）烙入 `/etc/online-upgrade-device`，插件据此动态解析本机对应配置的最新 Release 并匹配正确的固件包，避免下错型号/前端。

### 变更文件
- `Scripts/Packages.sh` — 新增 `gooyjq/luci-app-online-upgrade` 仓库克隆
- `Config/GENERAL.txt` — 新增 `CONFIG_PACKAGE_luci-app-online-upgrade=y`（全机型启用）
- `Scripts/online-upgrade/online-upgrade.sh` — 定制脚本：设备身份读取 + 自动匹配 Release + 构建标签判新
- `Scripts/online-upgrade/99-online-upgrade` — 定制默认 UCI 配置（仓库、代理、自动匹配）
- `Scripts/Handles.sh` — 烙入设备身份文件 + 覆盖上游插件脚本/默认值
- `README.md` — 补充在线升级说明

### 修复
- **在线升级 Release 识别**：`online-upgrade.sh` 中 `grep "tag_name":"` 缺少空格，与 GitHub API 实际返回的 `"tag_name": "` 不匹配，导致自动匹配模式无法找到标签。已修正正则并替换有 bug 的 `jsonfilter`（处理大 JSON 卡死）为 `grep`/`sed` 方案。
- **固件文件匹配通配**：`FIRMWARE_PATTERN` 默认值 `squashfs-sysupgrade\.bin$` 太严格，无法匹配文件名中间含分支/日期等额外字段的实际固件（如 `squashfs-sysupgrade-immortalwrt-master-wifi-yes-26.08.10.bin`）。已改为 `squashfs-sysupgrade.*\.bin$`，同时覆盖 `Handles.sh` 构建时设备身份文件和 `99-online-upgrade` 默认 UCI。
- **前端页面显示实际配置**：LuCI 在线升级页面此前硬编码了默认仓库地址而非从 UCI 读取，导致页面始终显示 `gooyjq/ImmortalWrt-Builder` 等默认值。现新增 `fix-frontend.py` 构建脚本，自动修复前端 JS：页面加载时从 UCI 读取 `repo`/`tag`/`firmware_pattern`/`proxy` 并填充表单，`saveCfg` 同时保存全部四项配置。

### 变更文件
- `Scripts/online-upgrade/online-upgrade.sh` — 修复 tag 匹配 + jsonfilter→grep + ASSET_BLOCK 范围
- `Scripts/online-upgrade/99-online-upgrade` — FIRMWARE_PATTERN 通配
- `Scripts/online-upgrade/fix-frontend.py` — 新增：构建时修复前端 JS 从 UCI 读配置
- `Scripts/Handles.sh` — FIRMWARE_PATTERN 通配 + 调用 fix-frontend.py

## [2026-08-09] 修复默认时区

config_generate 的 GMT0/UTC 改为 CST-8/Asia/Shanghai。
