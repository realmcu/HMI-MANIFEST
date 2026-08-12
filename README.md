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
  - [RTL8773G Smarthome](#rtl8773g-smarthome)
  - [RTL8773G Dashboard](#rtl8773g-dashboard)
  - [RTL8773G Chargebox](#rtl8773g-chargebox)
  - [RTL8783GBF eBadge](#rtl8783gbf-ebadge)
  - [RTL8721F Dashboard](#rtl8721f-dashboard)
- [Demo 项目 manifest](#demo-项目-manifestdemo)
  - [RTL8773G CLAW](#rtl8773g-claw)
  - [RTL8783G z2plus](#rtl8783g-z2plus)
  - [RTL8773G 8189NIC](#rtl8773g-8189nic)
- [测试用 manifest](#测试用-manifesttest)
  - [RTL8783GBF EVB WH](#rtl8783gbf-evb-wh)
  - [RTL8773G eBadge WH](#rtl8773g-ebadge-wh)

## 目录结构

- 根目录：正式发布的项目 manifest
- `demo/`：Demo / 示例项目的 manifest（如 CLAW、z2plus、8189 NIC 等）
- `test/`：开发调试用的临时 manifest（个人分支、评估板验证等，不建议外部用户使用）

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

**Gitee / Github：** 暂未开源

**编译：**
```bash
cd zephyrproject
west build -b rtl87x3g_evb realtek-app/applications/eBadge
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
west build -b rtl87x3g_watch/rtl8783gbf realtek-app/applications/eBadge
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

---

### RTL8773G eBadge WH

**内部 Gerrit：**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf test/rtl8773g-eBadge-wh.yml .
west update
```

**Gitee 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf test/rtl8773g-eBadge-wh-gitee.yml .
west update
```

**Github 公开：**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@github.com:realmcu/HMI-MANIFEST.git --mr master --mf test/rtl8773g-eBadge-wh-gitee.yml .
west update
```

---

> 说明：使用 Gitee / Github manifest 时，仓库目录结构与内部版本不同（例如 SDK 路径为 `sdk/` 或 `RTL8773EP/`），请以对应 `*-gitee.yml` 中的 `path` 字段为准。
