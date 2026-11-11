<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BASIC_AUTOCRUISE" param="AutoGasCancelSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自動巡航: 鬆開油門取消速度

**選單:** 駕駛控制 \> 啟動·自動 \> 自動巡航

---

<!-- CARROT:SETTING:BEGIN AutoGasCancelSpeed -->
<a id="AutoGasCancelSpeed"></a>

## 自動巡航: 鬆開油門取消速度

`AutoGasCancelSpeed`

鬆開油門踏板時，當前速度低於設定值則取消巡航。

<!-- CARROT:AUTO:BEGIN AutoGasCancelSpeed -->
<!-- CARROT:AUTO:SOURCE facts="54b1868b7426c7518fefb2b2ab9d33428c996b657f2f6ed15268e9a13256f038" semantic="93fa59e0c6761db851d9a73b8ceb501e211a24304f3b3f35a030a37bb4e5df3f" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `30km/h`
- **範圍:** `0km/h` ~ `200km/h`
- **步長:** `5`
- **顯示單位:** `km/h`
- **選單:** 駕駛控制 \> 啟動·自動 \> 自動巡航
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoGasCancelSpeed -->

<!-- CARROT:MANUAL:BEGIN AutoGasCancelSpeed -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

放開油門踏板時，低於此速度會取消巡航。

- **調高：** 提高適用的速度或速度門檻。
- **調低：** 降低速度或門檻。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同起步、油門及前車條件下，每次調整一項，比較巡航啟用時機及設定速度。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoGasCancelSpeed -->

<!-- CARROT:SETTING:END AutoGasCancelSpeed -->
