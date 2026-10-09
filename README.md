# HMI Manifest

本仓库统一维护所有平台的 West manifest 配置文件。

仓库同时托管在三处，保持同步：

- 内部 Gerrit：`ssh://cn4soc.rtkbf.com:29418/hmi/manifest`
- Gitee 公开：`git@gitee.com:realmcu/hmi-manifest.git`
- Github 公开：`git@github.com:realmcu/HMI-MANIFEST.git`

对应地，每个已开源的项目会提供三份 manifest：

- `<project>.yml`：指向内部 Gerrit 仓库
- `<project>-gitee.yml`：指向 Gitee 公开仓库（仅部分项目提供）
- `<project>-github.yml`：指向 GitHub 公开仓库（仅部分项目提供）

## 目录

- [目录结构](#目录结构)
- [正式项目 manifest](#正式项目-manifest)
  - [RTL8773E Dashboard](#rtl8773e-dashboard)
  - [RTL8773E eBadge](#rtl8773e-ebadge)
  - [RTL8773G Deskmate](#rtl8773g-deskmate)
  - [RTL8773G eBadge](#rtl8773g-ebadge)
  - [RTL8773G + RTL8711F eBadge](#rtl8773g-rtl8711f-ebadge)
  - [RTL8773G Smarthome](#rtl8773g-smarthome)
  - [RTL8773G Dashboard](#rtl8773g-dashboard)
  - [RTL8773G Chargebox](#rtl8773g-chargebox)
  - [RTL8783GBF eBadge](#rtl8783gbf-ebadge)
  - [RTL8721F Dashboard](#rtl8721f-dashboard)
- [Demo 项目 manifest](#demo-项目-manifestdemo)
  - [RTL8773G CLAW](#rtl8773g-claw)
  - [RTL8783G z2plus](#rtl8783g-z2plus)
  - [RTL8773G 8189NIC](#rtl8773g-8189nic)
- [自动测试用 manifest](#自动测试用-manifestautotest)
  - [RTL8783GBF EVB HoneyGUI](#rtl8783gbf-evb-honeygui)
- [测试用 manifest](#测试用-manifesttest)
  - [RTL8783GBF EVB WH](#rtl8783gbf-evb-wh)
  - [RTL8773GTP eBadge WH](#rtl8773gtp-ebadge-wh)
  - [RTL87X3G Mijia](#rtl87x3g-mijia)

## 目录结构

- 根目录：正式发布的项目 manifest
- `demo/`：Demo / 示例项目的 manifest（如 CLAW、z2plus、8189 NIC 等）
- `autotest/`：自动化测试专用的 manifest
- `test/`：开发调试用的临时 manifest（个人分支、评估板验证等，不建议外部用户使用）
- `scripts/`：发布验证脚本（供 `.github/workflows/` 的 nightly 流程调用）

> 使用时请在 `--mf` 参数中带上对应的相对路径，例如 `--mf demo/rtl8773g-claw.yml`。

## 正式项目 manifest

---

### RTL8773E Dashboard

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773e-dashboard.yml .
west update
```

**Gitee 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf rtl8773e-dashboard-gitee.yml .
west update
```

**Github 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@github.com:realmcu/HMI-MANIFEST.git --mr master --mf rtl8773e-dashboard-github.yml .
west update
```

**编译：** MDK：Keil 编译 / GCC：`west build`

---

### RTL8773E eBadge

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773e-eBadge.yml .
west update
```

**Gitee 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf rtl8773e-eBadge-gitee.yml .
west update
```

**Github 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@github.com:realmcu/HMI-MANIFEST.git --mr master --mf rtl8773e-eBadge-github.yml .
west update
```

**编译：** Keil 编译

---

### RTL8773G Deskmate

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773g-deskmate.yml .
west update
```

**Gitee / Github：** 暂未开源

**编译：**
```bash
west build -b rtl87x3g_evb zephyrproject/realtek-app/applications/deskmate
```

---

### RTL8773G eBadge

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773g-eBadge.yml .
west update
```

**Gitee 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf rtl8773g-eBadge-gitee.yml .
west update
```

**Github：** 暂未开源

**编译：**
```bash
cd zephyrproject
west build -b rtl87x3g_evb realtek-app/applications/eBadge_8773g
```

---

### RTL8773G watch

**下载：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf Apollo/rtl8773gtp-watch-410-502.yml .
west update
```

**编译：**
```bash
py -3.13 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r zephyrproject\zephyr\scripts\requirements-base.txt

cmake -S applications -B applications\build-venv -G Ninja -DBOARD=rtl87x3g_evb -DPython3_EXECUTABLE="%CD%\.venv\Scripts\python.exe"
cmake --build applications\build-venv --parallel 8
```

---

### RTL8773G RTL8711F eBadge

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773g-rtl8711f-eBadge.yml .
west update
```

**Gitee 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf rtl8773g-rtl8711f-eBadge-gitee.yml .
west update
```

**Github：** 暂未开源

**编译：**
```bash
cd zephyrproject
west build -b rtl87x3g_evb realtek-app/applications/eBadge_8773g_8711f
```

---

### RTL8773G Smarthome

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773g-hmi.yml .
west update
```

**Gitee 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf rtl8773g-smarthome-gitee.yml .
west update
```

**Github 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@github.com:realmcu/HMI-MANIFEST.git --mr master --mf rtl8773g-smarthome-github.yml .
west update
```

**编译：**
```bash
west build -b rtl87x3g_evb zephyrproject/realtek-app/applications/smarthome
```

---

### RTL8773G Dashboard

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773g-hmi.yml .
west update
```

**Gitee 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf rtl8773g-dashboard-gitee.yml .
west update
```

**Github 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@github.com:realmcu/HMI-MANIFEST.git --mr master --mf rtl8773g-dashboard-github.yml .
west update
```

**编译：**
```bash
west build -b rtl87x3g_evb zephyrproject/realtek-app/applications/dashboard
```

---

### RTL8773G Chargebox

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773g-hmi.yml .
west update
```

**Gitee 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf rtl8773g-chargebox-gitee.yml .
west update
```

**Github 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@github.com:realmcu/HMI-MANIFEST.git --mr master --mf rtl8773g-chargebox-github.yml .
west update
```

**编译：**
```bash
west build -b rtl87x3g_evb zephyrproject/realtek-app/applications/chargebox
```

---

### RTL8783GBF eBadge

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8783gbf-eBadge.yml .
west update
```

**Gitee 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf rtl8783gbf-eBadge-gitee.yml .
west update
```

**Github 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@github.com:realmcu/HMI-MANIFEST.git --mr master --mf rtl8783gbf-eBadge-github.yml .
west update
```

**编译：**
```bash
cd zephyrproject
west build -b rtl87x3g_evb realtek-app/applications/eBadge
```

---

### RTL8721F Dashboard

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8721f-dashboard.yml .
west update
```

**Gitee 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf rtl8721f-dashboard-gitee.yml .
west update
```

**Github 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@github.com:realmcu/HMI-MANIFEST.git --mr master --mf rtl8721f-dashboard-github.yml .
west update
```

**编译（Linux）：**
```bash
cd ameba-rtos
source env.sh
ameba.py SOC RTL8721F
ameba.py menuconfig
ameba.py build
```

**编译（Windows）：**
```bash
cd ameba-rtos
env.bat
ameba.py SOC RTL8721F
ameba.py menuconfig
ameba.py build
```

---

## Demo 项目 manifest（`demo/`）

---

### RTL8773G CLAW

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf demo/rtl8773g-claw.yml .
west update
```

**编译：**
```bash
cd zephyrproject
west build -b rtl87x3g_watch/rtl8783gbf realtek-app/applications/claw/RustMcuClaw/mcu
```

---

### RTL8783G z2plus

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf demo/rtl8783g-z2plus.yml .
west update
```

**编译：**
```bash
cd zephyrproject
west build -s realtek-app/applications/z2plusTCPUDP -b rtl87x3g_watch/rtl8783gbf -d build/z2plusTCPUDP
```

---

### RTL8773G 8189NIC

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf demo/rtl8773g-8189.yml .
west update
```

**编译：**
```bash
cd zephyrproject
west build -b rtl87x3g_watch/rtl8783gbf realtek-app/applications/wifi_nic_sdio
```

---

## 自动测试用 manifest（`autotest/`）

> 该目录下的 manifest 供自动化测试任务拉取固定的项目组合，不建议作为正式项目配置使用。

---

### RTL8783GBF EVB HoneyGUI

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf autotest/rtl8783gbf-evb-honeygui.yml .
west update
```

**编译：**（该 manifest 把 app 检出到工作区根目录的 `applications/`，不在 `zephyrproject/` 下）
```bash
cd applications
west build -b rtl87x3g_evb
```

**下载/烧录：**

> 首次下载、空片或需要更新 runtime 时，先烧录 RTL8783G runtime：

```bash
cd applications
CHIP=RTL8783G scripts/flash-runtime-linux.sh /dev/ttyUSB0  # Linux
```

```bat
cd applications
set CHIP=RTL8783G && scripts\flash-runtime-win32.bat COM3  :: Windows
```

> 然后烧录 App；后续仅更新 App 时直接执行此步骤：

```bash
cd applications
scripts/flash-linux-app.sh /dev/ttyUSB0  # Linux
```

```bat
cd applications
scripts\flash-win32-app.bat COM3         :: Windows
```

请根据实际连接修改 Linux 下载口 `/dev/ttyUSB0` 或 Windows 串口 `COM3`。

---

## 测试用 manifest（`test/`）

> ⚠️ 该目录下的 manifest 仅用于内部开发测试（例如个人分支、评估板 bring-up），版本可能不稳定，仅限相关开发人员使用。

---

### RTL8783GBF EVB WH

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf test/rtl8783gbf-evb-wh.yml .
west update
```

**编译：**（该 manifest 把 app 检出到工作区根目录的 `applications/`，不在 `zephyrproject/` 下）
```bash
cd applications
west build -b rtl87x3g_evb
```

---

### RTL8773GTP eBadge WH

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf test/rtl8773gtp-eBadge-wh.yml .
west update
```

**Gitee 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf test/rtl8773gtp-eBadge-wh-gitee.yml .
west update
```

**Github 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@github.com:realmcu/HMI-MANIFEST.git --mr master --mf test/rtl8773gtp-eBadge-wh-gitee.yml .
west update
```

**编译：**（该 manifest 把 app 检出到工作区根目录的 `applications/`，不在 `zephyrproject/` 下）
```bash
cd applications
west build -b rtl87x3g_evb
```
**烧录：**

> 首次烧录前需先烧录 运行时：

```bash
cd applications
scripts\flash-runtime-win32.bat COM3     # Windows 首次
scripts/flash-runtime-linux.sh /dev/ttyUSB0  # Linux 首次
```

> 之后每次烧录 app即可：

```bash
cd applications
scripts\flash-win32-app.bat COM3           # Windows
scripts/flash-linux-app.sh /dev/ttyUSB0    # Linux
```

---

### RTL87X3G Mijia

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf test/rtl87x3g-mijia.yml .
west update
```

**编译：**
```bash
cd zephyrproject
west build -b rtl87x3g_evb realtek-app/applications/mijia
```

---

> 说明：使用 Gitee / Github manifest 时，仓库目录结构与内部版本不同（例如 SDK 路径为 `sdk/` 或 `RTL8773EP/`），请以对应 `*-gitee.yml` 中的 `path` 字段为准。
