<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="VehicleNaviDecelCancel" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 原車導航減速中止請求

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancel -->
<a id="VehicleNaviDecelCancel"></a>

## 原車導航減速中止請求

`VehicleNaviDecelCancel`

僅在外部導航未連線時應用（原車導航 CAN）。啟用後，在 openpilot 啟用（約 18km/h 以上）且下方已啟用的型別正在減速時，按一次巡航 + 鍵或輕踩油門（踩下不足 0.4 秒後鬆開）即中止該處減速。此輸入不會提高設定速度（+1 和輕踩油門 +10 均不生效）。中止只適用於該攝影機或減速帶，下一個仍會減速。闖紅燈、後向攝影機和區間測速不能中止；固定攝影機僅在其詳細項單獨開啟時可中止。在詳細項中按型別（箱式攝影機、移動區間、減速帶、固定攝影機）分別開關。

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancel -->
<!-- CARROT:AUTO:SOURCE facts="c1161d32687148f922e4d040337e05b012cbec19247bc488987535654aa71964" semantic="b4932756ef27f4ad90176e3da43004bb00e3808dc92ffd2bff98e1c48d5fe10f" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancel -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancel -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

啟用後，巡航 + 或輕踩油門可取消指定類型的支援原廠導航減速；停用時不使用此取消輸入。固定式、號誌及後方執法仍排除在外。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在子設定中選擇適用類型。若輸入已用於取消減速，就不會同時增加設定速度。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancel -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancel -->
