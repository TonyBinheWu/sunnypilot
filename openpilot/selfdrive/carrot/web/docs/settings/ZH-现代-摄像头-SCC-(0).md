<!-- CARROT:GENERATED schema="1" locale="zh" group="VEH_HYUNDAI" param="HyundaiCameraSCC" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 现代: 摄像头 SCC (0)

**菜单:** 车辆与硬件 \> 现代·起亚

---

<!-- CARROT:SETTING:BEGIN HyundaiCameraSCC -->
<a id="HyundaiCameraSCC"></a>

## 现代: 摄像头 SCC (0)

`HyundaiCameraSCC`

1: 纵向控制车辆, 2: 巡航状态同步 (CAN-FD 车辆), 3: 原厂巡航 (CANFD 纵向线束) 关闭时，若在摄像头总线上检测到 SCC，发生 CAN 错误时会提示启用此设置。已配置摄像头 SCC 的车型除外。 CAN-FD CameraSCC 使用 openpilot 纵向控制并启用角雷达时，在 CAN 有效、D 挡、松开制动且车速超过 10.8 km/h 的条件下，会周期性请求开启原厂 SCC MAIN。此功能独立于 AutoEngage 和 Carrot 巡航激活状态，MAIN 开启后停止该请求。SET 和停车后恢复请求仍要求 Carrot 巡航处于激活状态。 CAN-FD CameraSCC 使用 openpilot 纵向控制时，用于仪表显示的原厂 SCC MAIN 状态与 Carrot 激活意图分别处理。转向激活遵循 AutoEngage 初始设置及现有驾驶员按键设置。

<!-- CARROT:AUTO:BEGIN HyundaiCameraSCC -->
<!-- CARROT:AUTO:SOURCE facts="cca3f0c59d4c217787d0ddf59f36d13f62fa9092b36de216387c44e5f0e9ae41" semantic="287a1e4a7254a0c59acf4e381efa7c629c34796276cbd8584241a52c4a779f28" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 分段选择
- **默认值:** `0`
- **范围:** `0` ~ `3`
- **步长:** `1`
- **菜单:** 车辆与硬件 \> 现代·起亚
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HyundaiCameraSCC -->

<!-- CARROT:MANUAL:BEGIN HyundaiCameraSCC -->
<!-- CARROT:REVIEW reviewed-for="287a1e4a7254a0c59acf4e381efa7c629c34796276cbd8584241a52c4a779f28" reviewed-at="2026-11-04T12:00:00+09:00" -->
<!-- CARROT:MANUAL:END HyundaiCameraSCC -->

<!-- CARROT:SETTING:END HyundaiCameraSCC -->
