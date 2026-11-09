# HMI Manifest

This repository is the single place where the West manifest files for all platforms are maintained.

The repository is hosted in three locations, kept in sync:

- Internal Gerrit: `ssh://cn4soc.rtkbf.com:29418/hmi/manifest`
- Gitee (public): `git@gitee.com:realmcu/hmi-manifest.git`
- GitHub (public): `git@github.com:realmcu/HMI-MANIFEST.git`

Accordingly, every open-sourced project provides up to three manifests:

- `<project>-gerrit.yml`: points at the internal Gerrit repositories
- `<project>-gitee.yml`: points at the public Gitee repositories (only for some projects)
- `<project>-github.yml`: points at the public GitHub repositories (only for some projects)

## Table of contents

- [Prerequisites](#prerequisites)
- [Project maturity](#project-maturity)
- [Repository layout](#repository-layout)
- [Watch](#watch)
  - [RTL8773GTP Watch 360360](#rtl8773gtp-watch-360360)
- [Dashboard](#dashboard)
  - [RTL8773E Dashboard](#rtl8773e-dashboard)
  - [RTL8773G Dashboard](#rtl8773g-dashboard)
  - [RTL8721F Dashboard](#rtl8721f-dashboard)
- [eBadge](#ebadge)
  - [RTL8773E eBadge](#rtl8773e-ebadge)
  - [RTL8773G eBadge](#rtl8773g-ebadge)
  - [RTL8773G + RTL8711F eBadge](#rtl8773g--rtl8711f-ebadge)
  - [RTL8783GBF eBadge](#rtl8783gbf-ebadge)
- [Other products](#other-products)
  - [RTL8773G Deskmate](#rtl8773g-deskmate)
  - [RTL8773G Smarthome](#rtl8773g-smarthome)
  - [RTL8773G Chargebox](#rtl8773g-chargebox)
  - [RTL8762D LVGL HMI](#rtl8762d-lvgl-hmi)
- [Demo manifests (`demo/`)](#demo-manifests-demo)
  - [RTL8773G CLAW](#rtl8773g-claw)
  - [RTL8783G z2plus](#rtl8783g-z2plus)
  - [RTL8773G 8189NIC](#rtl8773g-8189nic)
- [Automated-test manifests (`autotest/`)](#automated-test-manifests-autotest)
  - [RTL8783GBF EVB HoneyGUI](#rtl8783gbf-evb-honeygui)
- [Test manifests (`test/`)](#test-manifests-test)
  - [RTL8783GBF EVB WH](#rtl8783gbf-evb-wh)
  - [RTL8773GTP eBadge WH](#rtl8773gtp-ebadge-wh)
  - [RTL87X3G Mijia](#rtl87x3g-mijia)
- [Reporting problems](#reporting-problems)

## Prerequisites

| Tool | Version | Check |
| --- | --- | --- |
| `git` | ≥ 2.20 | `git --version` |
| `python3` | ≥ 3.8 | `python3 --version` |
| `west` | ≥ 1.2 | `west --version` |

The commands below clone over SSH, so an SSH key must be registered with your hosting service
beforehand. If you have not set one up, use the HTTPS address of the same repository instead.

## Project maturity

| Project | Maturity |
| --- | --- |
| RTL8773E Dashboard | Released |
| RTL8773G Smarthome | Released |
| RTL8773G Dashboard | Released |
| RTL8773G Chargebox | Released |
| RTL8773G + RTL8711F eBadge | In development |
| RTL8721F Dashboard | In development |
| RTL8762D LVGL HMI | In development |
| RTL8773E eBadge | Internal use |
| RTL8773G eBadge | Internal use |
| RTL8783GBF eBadge | Internal use |
| RTL8773GTP Watch 360360 | Internal use |
| RTL8773G Deskmate | Internal use |

Manifests are published for the projects above so the sources and their history are available.
A project listed as in development or for internal use is not a released product, and its manifest
may change without notice.

## Repository layout

- `watch/`: watch manifests
- `dashboard/`: dashboard manifests grouped by chip family
- `ebadge/`: eBadge manifests grouped by chip family
- `deskmate/`: deskmate manifests
- `smarthome/`: smart-home manifests
- `chargebox/`: charging-case manifests
- `lvgl/`: LVGL HMI manifests
- `demo/`: manifests for demo and sample projects (CLAW, z2plus, 8189 NIC, etc.)
- `autotest/`: manifests used only by automated tests
- `test/`: temporary manifests for development and debugging (personal branches, EVB bring-up, etc.); not recommended for external users
- `scripts/`: release verification scripts

Product directories use lowercase names. Every manifest has an explicit source suffix such as
`-gerrit`, `-gitee`, or `-github`; channel variants are not separate directories.

> When using these files, pass the matching relative path to `--mf`, for example `--mf demo/rtl8773g-claw-gerrit.yml`.

## Watch

### RTL8773GTP Watch 360360

Smartwatch application for the RTL8773GTP, with a 360×360 display.

**Internal Gerrit:**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf watch/rtl8773gtp-watch-360360-gerrit.yml .
west update
```

**Gitee (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf watch/rtl8773gtp-watch-360360-gitee.yml .
west update
```

**Build:**
```bash
py -3.13 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r zephyrproject\zephyr\scripts\requirements-base.txt

cmake -S applications -B applications\build-venv -G Ninja -DBOARD=rtl87x3g_evb -DPython3_EXECUTABLE="%CD%\.venv\Scripts\python.exe"
cmake --build applications\build-venv --parallel 8
```

---

## Dashboard

### RTL8773E Dashboard

HMI dashboard application for the RTL8773E: an instrument-cluster display with GUI, OTA updates and
a designer-based UI.

**Internal Gerrit:**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf dashboard/rtl8773e-dashboard-gerrit.yml .
west update
```

**Gitee (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf dashboard/rtl8773e-dashboard-gitee.yml .
west update
```

**GitHub (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@github.com:realmcu/HMI-MANIFEST.git --mr master --mf dashboard/rtl8773e-dashboard-github.yml .
west update
```

**Build:** MDK (Keil) or GCC via `west build`

---

### RTL8773G Dashboard

HMI dashboard application for the RTL8773G.

**Internal Gerrit:** no standalone internal manifest is currently provided.

**Gitee (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf dashboard/rtl8773g-dashboard-gitee.yml .
west update
```

**GitHub (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@github.com:realmcu/HMI-MANIFEST.git --mr master --mf dashboard/rtl8773g-dashboard-github.yml .
west update
```

**Build:**
```bash
west build -b rtl87x3g_evb zephyrproject/realtek-app/applications/dashboard
```

---

### RTL8721F Dashboard

Dashboard application for the RTL8721F on the Ameba platform, with the UI in HoneyGUI.

**Internal Gerrit:**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf dashboard/rtl8721f-dashboard-gerrit.yml .
west update
```

**Gitee (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf dashboard/rtl8721f-dashboard-gitee.yml .
west update
```

**GitHub (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@github.com:realmcu/HMI-MANIFEST.git --mr master --mf dashboard/rtl8721f-dashboard-github.yml .
west update
```

**Build (Linux):**
```bash
cd ameba-rtos
source env.sh
ameba.py SOC RTL8721F
ameba.py menuconfig
ameba.py build
```

**Build (Windows):**
```bash
cd ameba-rtos
env.bat
ameba.py SOC RTL8721F
ameba.py menuconfig
ameba.py build
```

---

## eBadge

### RTL8773E eBadge

Electronic badge application for the RTL8773E.

**Internal Gerrit:**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf ebadge/rtl8773e-ebadge-gerrit.yml .
west update
```

**Gitee (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf ebadge/rtl8773e-ebadge-gitee.yml .
west update
```

**GitHub (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@github.com:realmcu/HMI-MANIFEST.git --mr master --mf ebadge/rtl8773e-ebadge-github.yml .
west update
```

**Build:** Keil (MDK)

---

### RTL8773G eBadge

Electronic badge application for the RTL8773G.

**Internal Gerrit:**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf ebadge/rtl8773g-ebadge-gerrit.yml .
west update
```

**Gitee (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf ebadge/rtl8773g-ebadge-gitee.yml .
west update
```

**GitHub:** not open-sourced yet

**Build:**
```bash
cd zephyrproject
west build -b rtl87x3g_evb realtek-app/applications/eBadge_8773g
```

---

### RTL8773G + RTL8711F eBadge

Electronic badge application combining the RTL8773G and the RTL8711F for the wireless link.

**Internal Gerrit:**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf ebadge/rtl8773g-rtl8711f-ebadge-gerrit.yml .
west update
```

**Gitee (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf ebadge/rtl8773g-rtl8711f-ebadge-gitee.yml .
west update
```

**GitHub:** not open-sourced yet

**Build:**
```bash
cd zephyrproject
west build -b rtl87x3g_evb realtek-app/applications/eBadge_8773g_8711f
```

---

### RTL8783GBF eBadge

Electronic badge application for the RTL8783GBF.

**Internal Gerrit:**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf ebadge/rtl8783gbf-ebadge-gerrit.yml .
west update
```

**Gitee (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf ebadge/rtl8783gbf-ebadge-gitee.yml .
west update
```

**GitHub (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@github.com:realmcu/HMI-MANIFEST.git --mr master --mf ebadge/rtl8783gbf-ebadge-github.yml .
west update
```

**Build:**
```bash
cd zephyrproject
west build -b rtl87x3g_evb realtek-app/applications/eBadge
```

---

## Other products

### RTL8773G Deskmate

Desktop companion device application for the RTL8773G.

**Internal Gerrit:**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf deskmate/rtl8773g-deskmate-gerrit.yml .
west update
```

**Gitee / GitHub:** not open-sourced yet

**Build:**
```bash
west build -b rtl87x3g_evb zephyrproject/realtek-app/applications/deskmate
```

---

### RTL8773G Smarthome

Smart-home control panel application for the RTL8773G.


**Internal Gerrit:** no standalone internal manifest is currently provided.

**Gitee (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf smarthome/rtl8773g-smarthome-gitee.yml .
west update
```

**GitHub (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@github.com:realmcu/HMI-MANIFEST.git --mr master --mf smarthome/rtl8773g-smarthome-github.yml .
west update
```

**Build:**
```bash
west build -b rtl87x3g_evb zephyrproject/realtek-app/applications/smarthome
```

---

### RTL8773G Chargebox

Charging-case application for the RTL8773G.

**Internal Gerrit:** no standalone internal manifest is currently provided.

**Gitee (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf chargebox/rtl8773g-chargebox-gitee.yml .
west update
```

**GitHub (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@github.com:realmcu/HMI-MANIFEST.git --mr master --mf chargebox/rtl8773g-chargebox-github.yml .
west update
```

**Build:**
```bash
west build -b rtl87x3g_evb zephyrproject/realtek-app/applications/chargebox
```

---

### RTL8762D LVGL HMI

An RTL8762D HMI project built on LVGL v9. Made up of the following components:

| Component | Internal Gerrit | Gitee |
| --- | --- | --- |
| SDK | `HoneyComb` (`sbee2-sdk-v0`) → `honeycomb/` | `realmcu/rtl8762d-hmi-sdk` (`master`) → `sdk/` |
| Wearable | HoneyComb submodule → `honeycomb/sdk/src/app/Wearable` | `realmcu/wearable` (`master`) → `sdk/src/app/Wearable` |
| LVGL | HoneyComb submodule → `honeycomb/sdk/src/app/lvgl` | `realmcu/lvgl` (`lvgl_v9`) → `sdk/src/app/lvgl` |
| HMI application | `HoneyRepo/hmi` (`rtl8762d-lvgl-hmi`) → `honeycomb/sdk/board/evb_stack_img/lvgl_hmi` | `realmcu/hmi` (`rtl8762d-lvgl-hmi`) → `sdk/board/evb_stack_img/lvgl` |

**Internal Gerrit:**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf lvgl/rtl8762d-lvgl-hmi-gerrit.yml .
west update
```

**Gitee (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf lvgl/rtl8762d-lvgl-hmi-gitee.yml .
west update
```

**GitHub:** not open-sourced yet

**Build:** open `sdk/board/evb_stack_img/lvgl/mdk/project.uvprojx` in Keil and build.

---

## Demo manifests (`demo/`)

---

### RTL8773G CLAW

**Internal Gerrit:**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf demo/rtl8773g-claw-gerrit.yml .
west update
```

**Build:**
```bash
cd zephyrproject
west build -b rtl87x3g_watch/rtl8783gbf realtek-app/applications/claw/RustMcuClaw/mcu
```

---

### RTL8783G z2plus

**Internal Gerrit:**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf demo/rtl8783g-z2plus-gerrit.yml .
west update
```

**Build:**
```bash
cd zephyrproject
west build -s realtek-app/applications/z2plusTCPUDP -b rtl87x3g_watch/rtl8783gbf -d build/z2plusTCPUDP
```

---

### RTL8773G 8189NIC

**Internal Gerrit:**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf demo/rtl8773g-8189-gerrit.yml .
west update
```

**Build:**
```bash
cd zephyrproject
west build -b rtl87x3g_watch/rtl8783gbf realtek-app/applications/wifi_nic_sdio
```

---

## Automated-test manifests (`autotest/`)

> The manifests in this directory give automated test jobs a fixed set of projects. Do not use them as production configurations.

---

### RTL8783GBF EVB HoneyGUI

**Internal Gerrit:**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf autotest/rtl8783gbf-evb-honeygui-gerrit.yml .
west update
```

**Build:** (this manifest checks the app out to `applications/` at the workspace root, not under `zephyrproject/`)
```bash
cd applications
west build -b rtl87x3g_evb
```

**Flash:**

> On a blank chip, on the first flash, or when the runtime needs updating, flash the RTL8783G runtime first:

```bash
cd applications
CHIP=RTL8783G scripts/flash-runtime-linux.sh /dev/ttyUSB0  # Linux
```

```bat
cd applications
set CHIP=RTL8783G && scripts\flash-runtime-win32.bat COM3  :: Windows
```

> Then flash the app. For later app-only updates, run this step alone:

```bash
cd applications
scripts/flash-linux-app.sh /dev/ttyUSB0  # Linux
```

```bat
cd applications
scripts\flash-win32-app.bat COM3         :: Windows
```

Adjust the Linux port `/dev/ttyUSB0` or the Windows COM port `COM3` to match your actual connection.

---

## Test manifests (`test/`)

> ⚠️ The manifests in this directory are for internal development and testing only (personal branches, EVB bring-up, and so on). They may be unstable and are meant only for the developers concerned.

---

### RTL8783GBF EVB WH

**Internal Gerrit:**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf test/rtl8783gbf-evb-wh-gerrit.yml .
west update
```

**Build:** (this manifest checks the app out to `applications/` at the workspace root, not under `zephyrproject/`)
```bash
cd applications
west build -b rtl87x3g_evb
```

---

### RTL8773GTP eBadge WH

**Internal Gerrit:**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf test/rtl8773gtp-ebadge-wh-gerrit.yml .
west update
```

**Gitee (public):**
```bash
mkdir <workspace> && cd <workspace>
west init -m git@gitee.com:realmcu/hmi-manifest.git --mr master --mf test/rtl8773gtp-ebadge-wh-gitee.yml .
west update
```

**GitHub:** not provided for this test manifest.

**Build:** (this manifest checks the app out to `applications/` at the workspace root, not under `zephyrproject/`)
```bash
cd applications
west build -b rtl87x3g_evb
```

**Flash:**

> Flash the runtime before the first app flash:

```bash
cd applications
scripts\flash-runtime-win32.bat COM3     # Windows, first time
scripts/flash-runtime-linux.sh /dev/ttyUSB0  # Linux, first time
```

> Afterwards, flash the app only:

```bash
cd applications
scripts\flash-win32-app.bat COM3           # Windows
scripts/flash-linux-app.sh /dev/ttyUSB0    # Linux
```

---

### RTL87X3G Mijia

**Internal Gerrit:**
```bash
mkdir <workspace> && cd <workspace>
west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf test/rtl87x3g-mijia-gerrit.yml .
west update
```

**Build:**
```bash
cd zephyrproject
west build -b rtl87x3g_evb realtek-app/applications/mijia
```

---

> Note: when you use a Gitee or GitHub manifest, the repository layout differs from the internal one (the SDK lives under `sdk/` or `RTL8773EP/`, for example). The `path` field in the matching `*-gitee.yml` is authoritative.

## Reporting problems

Please include the manifest name, the exact command you ran, the failing project from `west update`,
and the first build error.
