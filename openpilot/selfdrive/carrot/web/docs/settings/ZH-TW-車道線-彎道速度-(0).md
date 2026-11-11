<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANEMODE" param="UseLaneLineCurveSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 車道線: 彎道速度 (0)

**選單:** 駕駛控制 \> 轉向 \> 車道模式

---

<!-- CARROT:SETTING:BEGIN UseLaneLineCurveSpeed -->
<a id="UseLaneLineCurveSpeed"></a>

## 車道線: 彎道速度 (0)

`UseLaneLineCurveSpeed`

低於設定速度時不使用車道模式

<!-- CARROT:AUTO:BEGIN UseLaneLineCurveSpeed -->
<!-- CARROT:AUTO:SOURCE facts="d8f7c24313c6f0159f9ac8d1cf8e75082fb6871d4098d5cb3d38ff5895a09601" semantic="ba0eea8757a1b91d43653961d6c80ce6c8384ba9524d5ee91a71df24e30beb5e" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0km/h`
- **範圍:** `0km/h` ~ `200km/h`
- **步長:** `10`
- **顯示單位:** `km/h`
- **選單:** 駕駛控制 \> 轉向 \> 車道模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END UseLaneLineCurveSpeed -->

<!-- CARROT:MANUAL:BEGIN UseLaneLineCurveSpeed -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

低於設定速度時不使用 LaneMode。

- **調高：** 提高適用的速度或速度門檻。
- **調低：** 降低速度或門檻。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同車道及彎道重複測試，每次調整一項，同時比較路徑追蹤、轉向反應及平順度。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 不適當的數值可能降低轉向或縱向控制的穩定性與舒適度。每次只小幅調整一項，行為異常時恢復預設值。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END UseLaneLineCurveSpeed -->

<!-- CARROT:SETTING:END UseLaneLineCurveSpeed -->
