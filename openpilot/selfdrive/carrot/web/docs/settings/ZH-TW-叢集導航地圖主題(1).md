<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="HUD_BASIC" param="ClusterNaviMapTheme" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 叢集導航地圖主題(1)

**選單:** 顯示 \> 外部HUD \> 基本

---

<!-- CARROT:SETTING:BEGIN ClusterNaviMapTheme -->
<a id="ClusterNaviMapTheme"></a>

## 叢集導航地圖主題(1)

`ClusterNaviMapTheme`

0: 自動 1: 深色 2: 淺色 更改後外部導航應用會自動重新連線。

<!-- CARROT:AUTO:BEGIN ClusterNaviMapTheme -->
<!-- CARROT:AUTO:SOURCE facts="df174baf1483e200ae7d295a14aeefe5b7462660131d8986f20d1a9496d9fa60" semantic="22c25adc7668b0b1e6f02c8676e96b5d9f45276bc7802f5e0fdc596b6f12bb21" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** 深色 (`1`)
- **範圍:** 自動 (`0`) ~ 淺色 (`2`)
- **步長:** `1`
- **選項:** `0` 自動, `1` 深色, `2` 淺色
- **選單:** 顯示 \> 外部HUD \> 基本
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterNaviMapTheme -->

<!-- CARROT:MANUAL:BEGIN ClusterNaviMapTheme -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 自動
- `1` — 深色
- `2` — 淺色／變更時會自動重新連接外部導航 App
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
<!-- CARROT:MANUAL:END ClusterNaviMapTheme -->

<!-- CARROT:SETTING:END ClusterNaviMapTheme -->
