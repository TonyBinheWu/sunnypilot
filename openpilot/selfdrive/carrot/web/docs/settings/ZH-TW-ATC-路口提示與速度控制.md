<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="AutoTurnControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC 路口提示與速度控制

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControl -->
<a id="AutoTurnControl"></a>

## ATC 路口提示與速度控制

`AutoTurnControl`

0 關閉，1 路口提示，2 路口提示與速度控制，3 速度控制。導航顯示出口和轉彎提示，變換車道的方向由駕駛選擇。

<!-- CARROT:AUTO:BEGIN AutoTurnControl -->
<!-- CARROT:AUTO:SOURCE facts="26a54ff6b270f92997011df69f32bcd1b0a3bf7213758af0c05b0145edba3e86" semantic="c60e74ae9f02f3b4ca847ca4e7f0b5d7a9e4b85043058d06861a116e22426191" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `3`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControl -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControl -->
<!-- CARROT:REVIEW reviewed-for="c60e74ae9f02f3b4ca847ca4e7f0b5d7a9e4b85043058d06861a116e22426191" reviewed-at="2026-11-22T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

0 關閉，1 路口提示，2 路口提示與速度控制，3 速度控制。導航顯示出口和轉彎提示，變換車道的方向由駕駛選擇。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

模式 1 提供路口提示，模式 2 同時控制轉彎速度，模式 3 僅控制速度。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

變換車道前請先確認鄰車道狀況，再打對應的方向燈。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END AutoTurnControl -->

<!-- CARROT:SETTING:END AutoTurnControl -->
