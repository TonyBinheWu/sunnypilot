<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BASIC_AUTOCRUISE" param="AutoCruiseControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自動巡航控制 (僅限現代/起亞)

**選單:** 駕駛控制 \> 啟動·自動 \> 自動巡航

---

<!-- CARROT:SETTING:BEGIN AutoCruiseControl -->
<a id="AutoCruiseControl"></a>

## 自動巡航控制 (僅限現代/起亞)

`AutoCruiseControl`

1: 軟駐車 + 自動巡航, 2: 如果軟駐車報錯

<!-- CARROT:AUTO:BEGIN AutoCruiseControl -->
<!-- CARROT:AUTO:SOURCE facts="307d75c0a97622ef68f30ee31129e189d6e36a62e31ba89749a26061d49cbdff" semantic="686814b2afc5769591dcd6e77c8b4ea3b65cc4c23c4b4437b0e289a38f9273d5" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `3`
- **步長:** `1`
- **選單:** 駕駛控制 \> 啟動·自動 \> 自動巡航
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoCruiseControl -->

<!-- CARROT:MANUAL:BEGIN AutoCruiseControl -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

符合條件時，此設定會自動啟用巡航加速與煞車；不會直接啟用橫向控制或限制轉向扭矩。

- `0` — 停用自動巡航與柔和停車保持；手動巡航與常駐橫向控制仍可使用。
- `1` — 啟用自動巡航，使用標準柔和停車保持行為。
- `2` — 啟用自動巡航；柔和停車保持行為適用於使用標準模式會回報錯誤的車輛。
- `3` — 目前控制路徑使用與 `2` 相同的自動巡航與柔和停車保持行為。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

不需要自動巡航時使用 `0`，一般自動巡航使用 `1`。僅當車輛在 `1` 時回報 soft-hold 錯誤，才使用 `2`，並在相同起步、油門及前車條件下比較啟用時機。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> `AlwaysLateral=1` 時，只要橫向控制已啟用，自動巡航關閉後仍會持續輔助轉向。`AlwaysLateral=0` 時，轉向與巡航共用啟用狀態，因此轉向看起來可能隨自動巡航一起切換。
<!-- CARROT:NOTICE:END -->

此設定適用於 Hyundai 及 Kia 車輛；實際可用性取決於車輛的縱向控制配置。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoCruiseControl -->

<!-- CARROT:SETTING:END AutoCruiseControl -->
