<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="HUD_BASIC" param="ClusterNaviMapType" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 叢集導航地圖型別(0)

**選單:** 顯示 \> 外部HUD \> 基本

---

<!-- CARROT:SETTING:BEGIN ClusterNaviMapType -->
<a id="ClusterNaviMapType"></a>

## 叢集導航地圖型別(0)

`ClusterNaviMapType`

0: 普通地圖 1: 衛星地圖 更改後外部導航應用會自動重新連線。

<!-- CARROT:AUTO:BEGIN ClusterNaviMapType -->
<!-- CARROT:AUTO:SOURCE facts="6bf31a4c093e25df700dfe2152a5e38fc546a9cef650174d1909985fce883374" semantic="74a31937ac7dd81fe72e06f0f41520736d6558235984d4865a8b22153b7a32f0" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** 普通地圖 (`0`)
- **範圍:** 普通地圖 (`0`) ~ 衛星地圖 (`1`)
- **步長:** `1`
- **選項:** `0` 普通地圖, `1` 衛星地圖
- **選單:** 顯示 \> 外部HUD \> 基本
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterNaviMapType -->

<!-- CARROT:MANUAL:BEGIN ClusterNaviMapType -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 一般地圖
- `1` — 衛星地圖／變更時會自動重新連接外部導航 App
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

連接外接 HUD 後變更，確認方向、亮度及地圖連線。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> 變更此設定會自動重新連接外部導航來源。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END ClusterNaviMapType -->

<!-- CARROT:SETTING:END ClusterNaviMapType -->
