<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BUTTON_UNIT" param="CruiseSpeedUnitBasic" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 巡航速度單位基礎(10)

**選單:** 駕駛控制 \> 按鈕·預設 \> 速度單位

---

<!-- CARROT:SETTING:BEGIN CruiseSpeedUnitBasic -->
<a id="CruiseSpeedUnitBasic"></a>

## 巡航速度單位基礎(10)

`CruiseSpeedUnitBasic`

SET/DECEL 加減速單位 (基礎單位)

<!-- CARROT:AUTO:BEGIN CruiseSpeedUnitBasic -->
<!-- CARROT:AUTO:SOURCE facts="14ebeb68b301ec23b371623e28e8a76d37052c1866a9844a4cef0dd302d4119c" semantic="7b48bb82f966475975d3c3d2c777ca567eb1ed3846b4d9fa5f3ec085600de7a0" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `10km/h`
- **範圍:** `1km/h` ~ `100km/h`
- **步長:** `1`
- **顯示單位:** `km/h`
- **選單:** 駕駛控制 \> 按鈕·預設 \> 速度單位
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseSpeedUnitBasic -->

<!-- CARROT:MANUAL:BEGIN CruiseSpeedUnitBasic -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

SET／DECEL 增減速度單位（基本單位）。

- **調高：** 增加基本按鍵模式每次調整設定速度的幅度。
- **調低：** 減少基本調整幅度。

Volkswagen 一般模式下，此增量適用於獨立 +／- 按鈕的短按。SET 選取目前速度，RES 恢復先前設定速度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

分別確認單次按壓及長按的設定速度變化量與時機。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseSpeedUnitBasic -->

<!-- CARROT:SETTING:END CruiseSpeedUnitBasic -->
