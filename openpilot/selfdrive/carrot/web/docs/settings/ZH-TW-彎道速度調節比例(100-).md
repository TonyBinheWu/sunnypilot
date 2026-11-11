<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CURVE" param="AutoCurveSpeedFactor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 彎道速度調節比例(100%)

**選單:** 駕駛控制 \> 速度與減速 \> 彎道與轉彎

---

<!-- CARROT:SETTING:BEGIN AutoCurveSpeedFactor -->
<a id="AutoCurveSpeedFactor"></a>

## 彎道速度調節比例(100%)

`AutoCurveSpeedFactor`

數值越高，允許的橫向加速度和彎道目標速度越低。根據距彎道的距離提前減速。

<!-- CARROT:AUTO:BEGIN AutoCurveSpeedFactor -->
<!-- CARROT:AUTO:SOURCE facts="77e0a270aa5de805c81eb0b4bc79bd1b2566b41d4e5204f809dd1b3ff682c30d" semantic="93b019e883847557a9ef42b96bfac26369726ea7c3b0b3c5155e8e10658ac930" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `100%`
- **範圍:** `50%` ~ `300%`
- **步長:** `5`
- **顯示單位:** `%`
- **選單:** 駕駛控制 \> 速度與減速 \> 彎道與轉彎
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoCurveSpeedFactor -->

<!-- CARROT:MANUAL:BEGIN AutoCurveSpeedFactor -->
<!-- CARROT:REVIEW reviewed-for="93b019e883847557a9ef42b96bfac26369726ea7c3b0b3c5155e8e10658ac930" reviewed-at="2026-09-18T11:24:21+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

根據同一預測點的橫擺角速度和速度計算曲率。設定比例用於調整允許的橫向加速度，並根據距彎道的距離、控制響應和逐漸建立的減速確定當前速度上限。

- **調高:** 同一彎道的目標速度降低。
- **調低:** 同一彎道的目標速度升高。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

每次調整一項，比較同一彎道前的目標速度和透過速度。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

不直接把遠期預測速度作為行駛目標。預測較晚時仍可能減速較晚；連續的新模型路徑確認轉彎趨緩後，vTurn 會快速恢復至最近約 0.25 秒內的最低上限。更嚴格的彎道限制立即生效；重複幀或缺失的模型輸入不會觸發快速解除。實際加速仍受現有加速度和加加速度限制。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoCurveSpeedFactor -->

<!-- CARROT:SETTING:END AutoCurveSpeedFactor -->
