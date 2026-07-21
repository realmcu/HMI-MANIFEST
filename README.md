# HMI Manifest

本仓库统一维护所有平台的 West manifest 配置文件。

仓库同时托管在两处，二者保持同步：

- 内部 Gerrit：`ssh://cn4soc.rtkbf.com:29418/hmi/manifest`
- Gitee 公开：`git@gitee.com:realmcu/hmi-manifest.git`

对应地，每个已开源的项目会提供两份 manifest：

- `<project>.yml`：指向内部 Gerrit 仓库
- `<project>-gitee.yml`：指向 Gitee 公开仓库（仅部分项目提供）

## 目录结构

- 根目录：正式发布的项目 manifest
- `demo/`：Demo / 示例项目的 manifest（如 CLAW、z2plus、8189 NIC 等）
- `test/`：开发调试用的临时 manifest（个人分支、评估板验证等，不建议外部用户使用）

> 使用时请在 `--mf` 参数中带上对应的相对路径，例如 `--mf demo/rtl8773g-claw.yml`。

## 正式项目 manifest

| 项目 | 内部 Gerrit 下载命令 | Gitee 公开下载命令 | 编译命令 |
| ------ | ---------- | ---------- | ---------- |
| RTL8773E Dashboard | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773e-dashboard.yml . && west update` | `mkdir <workspace> && cd <workspace> && west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf rtl8773e-dashboard-gitee.yml . && west update` | MDK：Keil 编译 / GCC：`west build` |
| RTL8773E eBadge | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773e-eBadge.yml . && west update` | `mkdir <workspace> && cd <workspace> && west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf rtl8773e-eBadge-gitee.yml . && west update` | Keil 编译 |
| RTL8773G Deskmate | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773g-deskmate.yml . && west update` | 暂未开源 | `west build -b rtl87x3g_evb zephyrproject/realtek-app/applications/deskmate` |
| RTL8773G eBadge | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773g-eBadge.yml . && west update` | 暂未开源 | `cd zephyrproject && west build -b rtl87x3g_evb realtek-app/applications/eBadge` |
| RTL8773G Smarthome | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773g-smarthome.yml . && west update` | 暂未开源 | `west build -b rtl87x3g_evb zephyrproject/realtek-app/applications/smarthome` |
| RTL8783GBF eBadge | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8783gbf-eBadge.yml . && west update` | `mkdir <workspace> && cd <workspace> && west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf rtl8783gbf-eBadge-gitee.yml . && west update` | `cd zephyrproject && west build -b rtl87x3g_watch/rtl8783gbf realtek-app/applications/eBadge` |
| RTL8721F Dashboard | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8721f-dashboard.yml . && west update` | `mkdir <workspace> && cd <workspace> && west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf rtl8721f-dashboard-gitee.yml . && west update` | Linux：<br>1. `cd ameba-rtos`<br>2. `source env.sh`<br>3. `ameba.py SOC RTL8721F`<br>4. `ameba.py menuconfig`<br>5. `ameba.py build`<br><br>Windows：<br>1. `cd ameba-rtos`<br>2. `env.bat`<br>3. `ameba.py SOC RTL8721F`<br>4. `ameba.py menuconfig`<br>5. `ameba.py build` |

## Demo 项目 manifest（`demo/`）

| 项目 | 内部 Gerrit 下载命令 | 编译命令 |
| ------ | ---------- | ---------- |
| RTL8773G CLAW | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf demo/rtl8773g-claw.yml . && west update` | `cd zephyrproject && west build -b rtl87x3g_watch/rtl8783gbf realtek-app\applications\claw\RustMcuClaw\mcu` |
| RTL8783G z2plus | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf demo/rtl8783g-z2plus.yml . && west update` | `cd zephyrproject && west build -s realtek-app/applications/z2plusTCPUDP -b rtl87x3g_watch/rtl8783gbf -d build/z2plusTCPUDP` |
| RTL8773G 8189NIC | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf demo/rtl8773g-8189.yml . && west update` | `cd zephyrproject && west build -b rtl87x3g_watch/rtl8783gbf realtek-app/applications/wifi_nic_sdio` |

## 测试用 manifest（`test/`）

> ⚠️ 该目录下的 manifest 仅用于内部开发测试（例如个人分支、评估板 bring-up），版本可能不稳定，仅限相关开发人员使用。

| 文件 | 说明 |
| ------ | ---------- |
| `test/rtl8783gbf-evb-wh.yml` | RTL8783GBF 评估板测试 manifest |
| `test/rtl87x3g-eBadge-board-wh.yml` | RTL87x3G eBadge 板级测试 manifest |
| `test/rtl87x3g-zephyr-simple-test.yml` | RTL87x3G Zephyr simple test manifest |

> 说明：使用 Gitee manifest 时，仓库目录结构与内部版本不同（例如 SDK 路径为 `sdk/` 或 `RTL8773EP/`），请以对应 `*-gitee.yml` 中的 `path` 字段为准。
