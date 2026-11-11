<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_CENTER" param="CameraYawTrimDeg" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 攝影機YAW校正(0)

**選單:** 駕駛控制 \> 轉向 \> 居中校正

---

<!-- CARROT:SETTING:BEGIN CameraYawTrimDeg -->
<a id="CameraYawTrimDeg"></a>

## 攝影機YAW校正(0)

`CameraYawTrimDeg`

微調攝影機左右(YAW)值(+: right)

<!-- CARROT:AUTO:BEGIN CameraYawTrimDeg -->
<!-- CARROT:AUTO:SOURCE facts="52775666372bb2cc78f541f3f2e68269747666101b784de87d48985d3a517fb1" semantic="290906bf88c0f6a12d995faeea4c0ab18dad803aefe18bf89e349b3a45474f4a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0`
- **範圍:** `-200` ~ `200`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 居中校正
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CameraYawTrimDeg -->

<!-- CARROT:MANUAL:BEGIN CameraYawTrimDeg -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

微調攝影機偏航對準角度（+：向右）。

- **負值：** 將攝影機偏航角往左微調。
- **正值：** 往右微調。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在平坦直路以穩定速度評估，逐步調整，比較向左／向右偏移是否減少。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END CameraYawTrimDeg -->

<!-- CARROT:SETTING:END CameraYawTrimDeg -->
