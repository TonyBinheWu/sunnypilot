<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CURVE" param="AutoCurveSpeedLowerLimit" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 彎道自動減速下限 (30)

**選單:** 駕駛控制 \> 速度與減速 \> 彎道與轉彎

---

<!-- CARROT:SETTING:BEGIN AutoCurveSpeedLowerLimit -->
<a id="AutoCurveSpeedLowerLimit"></a>

## 彎道自動減速下限 (30)

`AutoCurveSpeedLowerLimit`

彎道最低速度設定

<!-- CARROT:AUTO:BEGIN AutoCurveSpeedLowerLimit -->
<!-- CARROT:AUTO:SOURCE facts="6b82911b76ab02265a26dcdb66a8e2f04732efbe80f07c9a3ecda979b433c209" semantic="185888d940778f15492f4238006adf9ccc06f2ab8e488209936b2cf8bd099102" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `30km/h`
- **範圍:** `10km/h` ~ `200km/h`
- **步長:** `10`
- **顯示單位:** `km/h`
- **選單:** 駕駛控制 \> 速度與減速 \> 彎道與轉彎
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoCurveSpeedLowerLimit -->

<!-- CARROT:MANUAL:BEGIN AutoCurveSpeedLowerLimit -->
<!-- CARROT:REVIEW reviewed-for="185888d940778f15492f4238006adf9ccc06f2ab8e488209936b2cf8bd099102" reviewed-at="2026-09-11T13:36:03+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

設定視覺彎道和路線轉彎的目標速度下限。視覺控制先將下限應用於彎道目標，再根據剩餘距離計算當前接近速度上限。

- **調高:** 即使急彎也不會選擇低於更高下限的目標。
- **調低:** 允許更低的彎道目標速度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

需要目標速度下限時，與彎道調節比例分開調整。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

此值不保證道路上的安全速度。下限過高可能阻止必要的減速。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoCurveSpeedLowerLimit -->

<!-- CARROT:SETTING:END AutoCurveSpeedLowerLimit -->
