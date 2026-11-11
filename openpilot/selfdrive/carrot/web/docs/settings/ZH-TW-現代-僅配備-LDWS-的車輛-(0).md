<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_HYUNDAI" param="IsLdwsCar" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 現代: 僅配備 LDWS 的車輛 (0)

**選單:** 車輛與硬體 \> 現代·起亞

---

<!-- CARROT:SETTING:BEGIN IsLdwsCar -->
<a id="IsLdwsCar"></a>

## 現代: 僅配備 LDWS 的車輛 (0)

`IsLdwsCar`

僅配備 LDWS 的車輛

<!-- CARROT:AUTO:BEGIN IsLdwsCar -->
<!-- CARROT:AUTO:SOURCE facts="3cd3a10fd53db5187af4b24464f9324090e2950b085f206d11678b5c2ac85a2a" semantic="34f98ba7f7fd321a9bdd1b0e97bda0d45664cf5d320a3024bcfddb0784f5c889" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 車輛與硬體 \> 現代·起亞
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END IsLdwsCar -->

<!-- CARROT:MANUAL:BEGIN IsLdwsCar -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- **開啟：** 在舊款 Hyundai／Kia 的 `LKAS11` 訊息中，使用僅 LDWS 的儀表選項。
- **關閉：** 保留該車型預設的儀表 LKAS／LFA 選項。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

確認車輛規格及線組配置，停妥後設定，並於下次行車確認 SCC 及車道警示行為。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> 車型、年式、HDA 世代或線組位置不符，可能導致 SCC 或縱向控制行為錯誤。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END IsLdwsCar -->

<!-- CARROT:SETTING:END IsLdwsCar -->
