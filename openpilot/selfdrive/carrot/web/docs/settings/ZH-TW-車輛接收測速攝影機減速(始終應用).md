<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="VehicleSpeedCameraControlMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 車輛接收測速攝影機減速（始終應用）

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN VehicleSpeedCameraControlMode -->
<a id="VehicleSpeedCameraControlMode"></a>

## 車輛接收測速攝影機減速（始終應用）

`VehicleSpeedCameraControlMode`

僅在外部導航未連線時應用。外部導航連線期間，即使沒有當前引導專案也不使用原車導航。 選擇如何將透過車輛 CAN 接收的測速攝影機執法速度用於自動減速。此設定不影響從 Carrot Navi 接收的測速攝影機資訊。 0：禁用 1：無論加速踏板輸入如何都始終應用 2：車輛接收的攝影機減速開始後，新踩下加速踏板會忽略當前事件，並將覆蓋期間達到的最高車速保持為減速下限 3：踩下加速踏板期間暫停車輛接收的測速攝影機減速

<!-- CARROT:AUTO:BEGIN VehicleSpeedCameraControlMode -->
<!-- CARROT:AUTO:SOURCE facts="b5f21eaebc4a6457553b29b71d5723c91f44ef909f11ded90396b680dff7da46" semantic="751d90cd219472ee82418f090d5685fd521295720a7ff37eb36bf0b66f9d92e9" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** 始終應用 (`1`)
- **範圍:** 禁用 (`0`) ~ 加速時暫停 (`3`)
- **步長:** `1`
- **選項:** `0` 禁用, `1` 始終應用, `2` 加速踏板忽略減速, `3` 加速時暫停
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleSpeedCameraControlMode -->

<!-- CARROT:MANUAL:BEGIN VehicleSpeedCameraControlMode -->
<!-- CARROT:REVIEW reviewed-for="9b48b9341a4ad5213f5220c933fa0f581110bf68f4e799917977eb831c1e67bd" reviewed-at="2026-09-13T07:52:41.725083+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

外部導航連線期間僅使用外部導航，即使沒有當前引導專案也不使用原車導航。確認斷開連線或接收超時後，按各項設定恢復使用原車導航。

0禁用；1不受加速踏板影響；2在減速開始後重新踩下加速踏板時，將達到的最高速度作為下限保持至事件結束；3踩下加速踏板期間解除。此模式不控制外部導航減速。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

同時檢查外部導航連線狀態以及顯示的事件型別和剩餘距離。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleSpeedCameraControlMode -->

<!-- CARROT:SETTING:END VehicleSpeedCameraControlMode -->
