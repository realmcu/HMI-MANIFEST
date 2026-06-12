# HMI Manifest

本仓库统一维护所有平台的 West manifest 配置文件。

## manifest 文件

| 项目 | 下载命令 | 编译命令 |
| ------ | ---------- | ---------- |
| RTL8773G Deskmate | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773g-deskmate.yml . && west update` | `west build -b rtl87x3g_evb zephyrproject/realtek-app/applications/deskmate` |
| RTL8773E eBadge | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773e-eBadge.yml . && west update` | Keil 编译 |
| RTL8773G eBadge | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773g-eBadge.yml . && west update` | `west build -b rtl87x3g_evb zephyrproject/realtek-app/applications/eBadge` |
| RTL8773E Dashboard | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773e-dashboard.yml . && west update` | MDK：Keil 编译 / GCC：`west build` |
| RTL8773G CLAW | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773g-claw.yml . && west update` | `cd zephyrproject && west build -b rtl87x3g_watch/rtl8783gbf  realtek-app\applications\claw\RustMcuClaw\mcu` |
| RTL8783G z2plus | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8783g-z2plus.yml . && west update` | `cd zephyrproject && west build -s realtek-app/applications/z2plusTCPUDP -b rtl87x3g_watch/rtl8783gbf -d build/z2plusTCPUDP` |
| RTL8773G 8189NIC | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8773g-8189.yml . && west update` | `cd zephyrproject && west build -b rtl87x3g_watch/rtl8783gbf realtek-app/applications/wifi_nic_sdio` |
| RTL8783GBF eBadge | `mkdir <workspace> && cd <workspace> && west init -m ssh://cn4soc.rtkbf.com:29418/hmi/manifest --mr master --mf rtl8783gbf-eBadge.yml . && west update` | `cd zephyrproject && west build -b rtl87x3g_watch/rtl8783gbf realtek-app/applications/eBadge` |

## 常用命令

```bash
# 同步所有子项目
west update

# 构建
west build -b rtl87x3g_evb zephyrproject/realtek-app/applications/deskmate

# 烧录
west flash
```
