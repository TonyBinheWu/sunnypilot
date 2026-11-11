<!-- CARROT:GENERATED schema="1" locale="zh" group="CRUISE_DRIVE_MODE" param="MyDrivingModeAuto" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 驾驶模式: 自动

**菜单:** 驾驶控制 \> 巡航与车距 \> 加速特性 \> 驾驶模式

---

<!-- CARROT:SETTING:BEGIN MyDrivingModeAuto -->
<a id="MyDrivingModeAuto"></a>

## 驾驶模式: 自动

`MyDrivingModeAuto`

0:手动，1:普通↔安全，2:节能↔安全。接近停止前车时迅速进入安全模式，持续低速跟车也会进入。不满足停车接近条件时，前车加速度超过1.0m/s²并持续约0.5秒即可返回。否则需确认交通持续恢复3秒或行驶中前方持续无车。不会自动选择高速模式。

<!-- CARROT:AUTO:BEGIN MyDrivingModeAuto -->
<!-- CARROT:AUTO:SOURCE facts="6a3f9adfcb13cfd4f5efeea1bf94840acd4e661dd2a1f5c701c10bc6eac028e3" semantic="0704a17d228794f4dfa2ce01cffbcaf023b513a0993d4106e62db6057ef8b025" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 分段选择
- **默认值:** `0`
- **范围:** `0` ~ `2`
- **步长:** `1`
- **菜单:** 驾驶控制 \> 巡航与车距 \> 加速特性 \> 驾驶模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MyDrivingModeAuto -->

<!-- CARROT:MANUAL:BEGIN MyDrivingModeAuto -->
<!-- CARROT:REVIEW reviewed-for="0704a17d228794f4dfa2ce01cffbcaf023b513a0993d4106e62db6057ef8b025" reviewed-at="2026-09-27T14:30:00+09:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

`0`为手动，`1`为普通↔安全，`2`为节能↔安全。接近停止前车约0.3秒或持续低速跟车8秒后进入安全。不满足停车接近条件时，前车加速度超过1.0m/s²并持续约0.5秒即可返回普通/节能。否则需确认交通恢复3秒，或以至少15km/h行驶且前方无车持续4秒。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

行驶中手动更改保存的驾驶模式后，自动切换暂停至规划器重启。不会自动选择高速，也不会仅因停车时前车丢失而返回基本模式。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MyDrivingModeAuto -->

<!-- CARROT:SETTING:END MyDrivingModeAuto -->
