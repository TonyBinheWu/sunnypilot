<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_DRIVE_MODE" param="MyDrivingModeAuto" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 駕駛模式: 自動

**選單:** 駕駛控制 \> 巡航與車距 \> 加速特性 \> 駕駛模式

---

<!-- CARROT:SETTING:BEGIN MyDrivingModeAuto -->
<a id="MyDrivingModeAuto"></a>

## 駕駛模式: 自動

`MyDrivingModeAuto`

0:手動，1:普通↔安全，2:節能↔安全。接近停止前車時迅速進入安全模式，持續低速跟車也會進入。不滿足停車接近條件時，前車加速度超過1.0m/s²並持續約0.5秒即可返回。否則需確認交通持續恢復3秒或行駛中前方持續無車。不會自動選擇高速模式。

<!-- CARROT:AUTO:BEGIN MyDrivingModeAuto -->
<!-- CARROT:AUTO:SOURCE facts="59eab8f828f72ed6082b941ee4e7ba0d1cfc770030dd50a859ef3bb00510f841" semantic="0704a17d228794f4dfa2ce01cffbcaf023b513a0993d4106e62db6057ef8b025" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `2`
- **步長:** `1`
- **選單:** 駕駛控制 \> 巡航與車距 \> 加速特性 \> 駕駛模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MyDrivingModeAuto -->

<!-- CARROT:MANUAL:BEGIN MyDrivingModeAuto -->
<!-- CARROT:REVIEW reviewed-for="0704a17d228794f4dfa2ce01cffbcaf023b513a0993d4106e62db6057ef8b025" reviewed-at="2026-09-27T14:30:00+09:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

`0`為手動，`1`為普通↔安全，`2`為節能↔安全。接近停止前車約0.3秒或持續低速跟車8秒後進入安全。不滿足停車接近條件時，前車加速度超過1.0m/s²並持續約0.5秒即可返回普通/節能。否則需確認交通恢復3秒，或以至少15km/h行駛且前方無車持續4秒。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

行駛中手動更改儲存的駕駛模式後，自動切換暫停至規劃器重啟。不會自動選擇高速，也不會僅因停車時前車丟失而返回基本模式。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MyDrivingModeAuto -->

<!-- CARROT:SETTING:END MyDrivingModeAuto -->
