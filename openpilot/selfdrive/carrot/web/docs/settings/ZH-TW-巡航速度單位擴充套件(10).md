<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BUTTON_UNIT" param="CruiseSpeedUnit" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 巡航速度單位擴充套件(10)

**選單:** 駕駛控制 \> 按鈕·預設 \> 速度單位

---

<!-- CARROT:SETTING:BEGIN CruiseSpeedUnit -->
<a id="CruiseSpeedUnit"></a>

## 巡航速度單位擴充套件(10)

`CruiseSpeedUnit`

SET/DECEL 加減速單位 (模式 1,2,3, GasTok)

<!-- CARROT:AUTO:BEGIN CruiseSpeedUnit -->
<!-- CARROT:AUTO:SOURCE facts="76dfa22daec3b249c3a20e801e24ad6c495eee6109b42903bf6282bb88f0894d" semantic="a5e07bb426bb832d07d78bd6f304a09aae259509b726f72c8de9fb610763a878" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `10km/h`
- **範圍:** `1km/h` ~ `100km/h`
- **步長:** `1`
- **顯示單位:** `km/h`
- **選單:** 駕駛控制 \> 按鈕·預設 \> 速度單位
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseSpeedUnit -->

<!-- CARROT:MANUAL:BEGIN CruiseSpeedUnit -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

SET／DECEL 增減速度單位（模式 1、2、3、GasTok）。

- **調高：** 增加自訂按鍵模式及輕點油門操作每次調整設定速度的幅度。
- **調低：** 減少每次調整的幅度。

Volkswagen 此單位適用於獨立 +／- 調速，不適用於 SET 選取目前速度或 RES 恢復先前速度。長按與第二段滑動的 10 km/h 增量不受此設定影響。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

分別確認單次按壓及長按的設定速度變化量與時機。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseSpeedUnit -->

<!-- CARROT:SETTING:END CruiseSpeedUnit -->
