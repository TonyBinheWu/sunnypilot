<!-- CARROT:GENERATED schema="1" locale="zh" group="VEH_DM" param="DriverMonitoringMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 驾驶员监控模式

**菜单:** 车辆与硬件 \> 驾驶员监控

---

<!-- CARROT:SETTING:BEGIN DriverMonitoringMode -->
<a id="DriverMonitoringMode"></a>

## 驾驶员监控模式

`DriverMonitoringMode`

0：标准；1：实验。实验模式可能违反法规，仅限受控测试。无摄像头时基础警告为15/30/45秒；实验模式在确认的空旷直道上为30/60/90秒。周围从无移动车辆变为首次确认有移动车辆时，才启用20秒标准监测。持续观测或新增车辆不会延长，之后恢复实验监测。此期间停止摄像头操作宽限、特殊前方注视重置和检测放宽，并结束此前宽限。有摄像头的0模式保留comma行为；1模式为10/16/26秒，空旷道路为20/32/52秒，头部姿态容差增加20%。驾驶员或蓝牙按键操作重置计时，推迟摄像头警告45或90秒后开始摄像头监控；这也会延迟困倦、闭眼和手机警告。连续2秒明确注视前方可重置摄像头计时。操作不能解除最高警告或锁定。摄像头故障自动切换为操作监控。标准模式不保证合法认证。模式更改无需重启，约每0.5秒实时应用。切换保留累计监控时间、警告次数和锁定，并结束此前的操作宽限及连续前方注视判定。 现代/起亚/捷尼赛思CAN-FD中不按车型名称限制、通过格式、校验和、计数器及新鲜度验证的原始STEER\_TOUCH\_2AF触摸在摄像头不可用时持续重置操作计时；摄像头正常的1模式仅将新接触视为操作，0模式保持原样。 共同例外：无论摄像头是否可用，两种模式均在有效信号持续确认P挡、完全静止及辅助驾驶解除1秒后重置累计警告和锁定。仅零速或关闭再开启不能解除，必须手动重新启用。

<!-- CARROT:AUTO:BEGIN DriverMonitoringMode -->
<!-- CARROT:AUTO:SOURCE facts="06480cead541c69a5f9763864c2e545980bff263713b7281ea237f343557ad80" semantic="41de43ecd7b558bf3408066b776219f5a1367f4ed91a5aae8a31995a4f0b821a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 选择
- **默认值:** 标准 (`0`)
- **范围:** 标准 (`0`) ~ 实验（仅供测试） (`1`)
- **步长:** `1`
- **选项:** `0` 标准, `1` 实验（仅供测试）
- **菜单:** 车辆与硬件 \> 驾驶员监控
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END DriverMonitoringMode -->

<!-- CARROT:MANUAL:BEGIN DriverMonitoringMode -->
<!-- CARROT:REVIEW reviewed-for="71597058dbc3a5673ec5c3fa80f182b7386309654371ebfdfcbf577dd83a765d" reviewed-at="2026-09-28T23:46:27.865578+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

标准模式在摄像头正常时保留comma行为，不可用时采用独立的操作监控时间。实验模式在观测到的空旷道路上延长时间，在驾驶员或蓝牙操作后推迟摄像头警告，并在明确注视前方时重置计时。

现代/起亚/捷尼赛思CAN-FD中不按车型名称限制、通过格式、校验和、计数器及新鲜度验证的原始STEER_TOUCH_2AF触摸在摄像头不可用时持续重置操作计时。摄像头正常时，实验模式仅将有效松手后的新接触视为操作；持续握持或信号恢复不会重复延长宽限。摄像头正常的标准模式保持原样，触摸不能解除最高警告。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

实验模式仅限受控测试。模式更改无需重启，约每0.5秒实时应用，保留累计监控时间、警告次数和锁定。此前的操作宽限及连续前方注视判定结束。周围从无移动车辆变为首次确认有移动车辆时，才启用20秒标准监测。持续观测或新增车辆不会延长，之后恢复实验监测，但仍有车辆时不增加空路倍率。摄像头正常时，此期间使用原厂检测和输入处理，暂停实验操作宽限和特殊前方注视重置。此前宽限结束；所有观测消失且超过最后观测的2秒保留期后，再次出现才可触发新的监测窗口。

无论摄像头是否可用，两种模式均在有效信号持续确认P挡、完全静止及辅助驾驶解除1秒后重置累计警告和锁定。该例外也适用于标准模式；仅零速或关闭再开启不能解除，必须手动重新启用。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

操作宽限也会延迟困倦、闭眼及手机警告，不能保证清醒或合法合规。请阅读[四种模式的时间、宽限、重置和最高警告限制](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/driver-monitoring.md)。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END DriverMonitoringMode -->

<!-- CARROT:SETTING:END DriverMonitoringMode -->
