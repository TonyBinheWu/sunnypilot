<!-- CARROT:GENERATED schema="1" locale="zh" group="SYS_NET" param="HotspotOnBoot" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 开启热点 (0)

**菜单:** 系统 \> 网络与地图

---

<!-- CARROT:SETTING:BEGIN HotspotOnBoot -->
<a id="HotspotOnBoot"></a>

## 开启热点 (0)

`HotspotOnBoot`

SIM 就绪且移动数据已连接时，自动开启已保存的 Wi-Fi 热点并共享互联网；手动关闭热点会暂停本次开机的自动开启。

<!-- CARROT:AUTO:BEGIN HotspotOnBoot -->
<!-- CARROT:AUTO:SOURCE facts="e82f5b81680c38388d3410c7eb1c9aa0350de6b7168672a10b9eeb46a5bc7a7b" semantic="483a8e450bc5248e62520b76fc55c79fad20bff0753ad2f7a1540169a0b7c434" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 系统 \> 网络与地图
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HotspotOnBoot -->

<!-- CARROT:MANUAL:BEGIN HotspotOnBoot -->
<!-- CARROT:REVIEW reviewed-for="483a8e450bc5248e62520b76fc55c79fad20bff0753ad2f7a1540169a0b7c434" reviewed-at="2026-11-18T09:30:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 运作方式

开启后等待 SIM 就绪且有新鲜有效的移动数据连接，再启动已保存的热点与互联网共享。关闭后停止由本选项自动管理的热点。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

更新后重新启动一次，此后变更约五秒内生效。沿用热点名称和密码；连接其他设备，确认 Carrot 页面及外部网站均可开启。启动失败会间隔重试。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 补充说明

手动关闭热点会暂停自动启动，关闭再开启本选项或重启设备可恢复。移动网络短暂中断时保留本地网络。单个 Wi-Fi 无线接口可能从客户端切换为热点；SIM 套餐、APN 和运营商必须允许共享。本功能不修改 APN 或漫游设置。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END HotspotOnBoot -->

<!-- CARROT:SETTING:END HotspotOnBoot -->
