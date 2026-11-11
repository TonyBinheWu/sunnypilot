<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_RADAR" param="EnableCornerRadar" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 開啟角雷達 (0)

**選單:** 車輛與硬體 \> 雷達

---

<!-- CARROT:SETTING:BEGIN EnableCornerRadar -->
<a id="EnableCornerRadar"></a>

## 開啟角雷達 (0)

`EnableCornerRadar`

1: 開啟角雷達, 2: CCNC 車輛的切入檢測

<!-- CARROT:AUTO:BEGIN EnableCornerRadar -->
<!-- CARROT:AUTO:SOURCE facts="cdcf3e11de560b6dabaa94b1d3f1511f0a64c7ecad74df97981d6f9ac4076b2c" semantic="f3344cc43f62d863ecb64a7db5ee5dc1890061598ea1a111001723780943390c" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `2`
- **步長:** `1`
- **選單:** 車輛與硬體 \> 雷達
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END EnableCornerRadar -->

<!-- CARROT:MANUAL:BEGIN EnableCornerRadar -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- `0` — 不使用角雷達。
- `1` — 使用支援的角雷達追蹤資料。
- `2` — 使用角雷達追蹤資料與切入偵測。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在支援的雷達配置上，每次調整一項，並在相同前車及切入條件下確認偵測與追蹤。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> 車上有實體雷達，不代表已受支援。請在相同車輛配置下確認訊息接收與追蹤。
<!-- CARROT:NOTICE:END -->

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/radar.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END EnableCornerRadar -->

<!-- CARROT:SETTING:END EnableCornerRadar -->
