<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_AUX" param="MaxAngleFrames" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 最大角度幀數 (89)

**選單:** 車輛與硬體 \> 車輛輔助

---

<!-- CARROT:SETTING:BEGIN MaxAngleFrames -->
<a id="MaxAngleFrames"></a>

## 最大角度幀數 (89)

`MaxAngleFrames`

推薦 89

<!-- CARROT:AUTO:BEGIN MaxAngleFrames -->
<!-- CARROT:AUTO:SOURCE facts="40d00772bee7120c924bf1d965e43353f712e9fae1e0e19090cb4f6fa97f439a" semantic="c21f5b2f6d919fcc7d07af6ad5fe3f43c01fc42b1a190dd097bbd44f74ebad29" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `89`
- **範圍:** `80` ~ `100`
- **步長:** `1`
- **選單:** 車輛與硬體 \> 車輛輔助
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MaxAngleFrames -->

<!-- CARROT:MANUAL:BEGIN MaxAngleFrames -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

調整大轉向角時允許連續送出的轉向請求影格數。

- **調高：** 允許在大轉向角度下維持轉向請求的週期數更多。
- **調低：** 較早停止請求，以避免 EPS 故障。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

僅在支援車輛上，每次調整一項，並於下次行車時確認轉向或原廠 SCC 行為。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 與車輛控制配置不符的數值，可能改變轉向或原廠 SCC 行為。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MaxAngleFrames -->

<!-- CARROT:SETTING:END MaxAngleFrames -->
