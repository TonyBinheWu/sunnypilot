<!-- CARROT:GENERATED schema="1" locale="zh" group="VEH_DM" param="DriverMonitoringEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 启用驾驶员监控（例外设置）

**菜单:** 车辆与硬件 \> 驾驶员监控

---

<!-- CARROT:SETTING:BEGIN DriverMonitoringEnabled -->
<a id="DriverMonitoringEnabled"></a>

## 启用驾驶员监控（例外设置）

`DriverMonitoringEnabled`

默认开启，建议保持开启。此例外选项仅供未安装 DM 摄像头，或 DM 摄像头故障而无法正常进行驾驶员监控的设备使用。关闭后，正常行驶时的 DM 模型与警告、监控触发的强制减速及锁定都会停用。未启用驾驶员监控时驾驶，可能违反所在地法律、车辆要求或使用条件；请仅在确认适用要求并承担安全责任后关闭。

<!-- CARROT:AUTO:BEGIN DriverMonitoringEnabled -->
<!-- CARROT:AUTO:SOURCE facts="440a07ede7117a4b7c7f4f611aea1e17fa202eb493f853debe32700a3c05693d" semantic="75de16e159e826f4dfe20f040bbaada4fc65960b24b5d45781569bb9bb118027" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `1`
- **范围:** `0` ~ `1`
- **菜单:** 车辆与硬件 \> 驾驶员监控
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END DriverMonitoringEnabled -->

<!-- CARROT:MANUAL:BEGIN DriverMonitoringEnabled -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END DriverMonitoringEnabled -->

<!-- CARROT:SETTING:END DriverMonitoringEnabled -->
