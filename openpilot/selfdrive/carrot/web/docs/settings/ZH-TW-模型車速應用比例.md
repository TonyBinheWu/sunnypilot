<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CURVE" param="ApplyModelSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 模型車速應用比例

**選單:** 駕駛控制 \> 速度與減速 \> 彎道與轉彎

---

<!-- CARROT:SETTING:BEGIN ApplyModelSpeed -->
<a id="ApplyModelSpeed"></a>

## 模型車速應用比例

`ApplyModelSpeed`

按設定比例應用模型計算的行駛速度。

<!-- CARROT:AUTO:BEGIN ApplyModelSpeed -->
<!-- CARROT:AUTO:SOURCE facts="dc20b9f84614d57f771b3156317ee100589e8e042337b6a3c07ef03fb2502f9c" semantic="8039edb57e0c4c2bb0d6e9911d247c64a6f0c42f2e912402bc572f0a4701f388" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0%`
- **範圍:** `-120%` ~ `120%`
- **步長:** `1`
- **顯示單位:** `%`
- **選單:** 駕駛控制 \> 速度與減速 \> 彎道與轉彎
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ApplyModelSpeed -->

<!-- CARROT:MANUAL:BEGIN ApplyModelSpeed -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- `0` — 不將模型預測速度套用至巡航設定速度。
- **正值：** 縮放後的模型預測速度高於目前設定速度時，提高設定速度，最高以道路速限的 110% 為上限。
- **負值：** 直接套用縮放後的模型目標，因此設定速度可能明顯下降。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同彎道與路線導引條件下，每次調整一項，比較入彎前的目標及過彎速度。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> `0` 不會將模型駕駛速度混入目標。正值與負值會以相反方向套用模型速度混合。
<!-- CARROT:NOTICE:END -->

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END ApplyModelSpeed -->

<!-- CARROT:SETTING:END ApplyModelSpeed -->
