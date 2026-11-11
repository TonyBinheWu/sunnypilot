<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="AutoNaviCountDownMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 導航倒計時模式

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN AutoNaviCountDownMode -->
<a id="AutoNaviCountDownMode"></a>

## 導航倒計時模式

`AutoNaviCountDownMode`

外部導航連線期間僅使用外部導航距離，否則使用原車導航距離。連線狀態變化時重置之前的倒計時。 0: 不使用, 1: 轉向點 + 速度, 2: 轉向點 + 速度 + 減速帶

<!-- CARROT:AUTO:BEGIN AutoNaviCountDownMode -->
<!-- CARROT:AUTO:SOURCE facts="dccc70e6eb050f4f71e2bf45b7dc341eef3dc8154f50e6532f634acece2de815" semantic="164adc98b3573e2f4d0ea6aa380a9920ed4d56a1dc37b6bdf056a7ae5f0de063" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `2`
- **範圍:** `0` ~ `2`
- **步長:** `1`
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviCountDownMode -->

<!-- CARROT:MANUAL:BEGIN AutoNaviCountDownMode -->
<!-- CARROT:REVIEW reviewed-for="164adc98b3573e2f4d0ea6aa380a9920ed4d56a1dc37b6bdf056a7ae5f0de063" reviewed-at="2026-09-13T07:52:41.385068+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

外部導航連線期間僅使用外部導航，即使沒有當前引導專案也不使用原車導航。確認斷開連線或接收超時後，按各項設定恢復使用原車導航。

0關閉提醒；1包含轉向點和速度事件；2還包含減速帶。連線期間僅使用外部距離，否則使用原車距離，連線切換時重置之前的倒計時。不改變減速時機或強度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

同時檢查外部導航連線狀態以及顯示的事件型別和剩餘距離。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoNaviCountDownMode -->

<!-- CARROT:SETTING:END AutoNaviCountDownMode -->
