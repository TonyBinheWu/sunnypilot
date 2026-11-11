<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_FEEL" param="CustomSR" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自定義轉向比x0.1(0)

**選單:** 駕駛控制 \> 轉向 \> 轉向手感

---

<!-- CARROT:SETTING:BEGIN CustomSR -->
<a id="CustomSR"></a>

## 自定義轉向比x0.1(0)

`CustomSR`

轉向比 (參考車輛引數)，0: 使用實時轉向比

<!-- CARROT:AUTO:BEGIN CustomSR -->
<!-- CARROT:AUTO:SOURCE facts="64ccebfcde28feb24d1cbba8ccdcdb48ccebd20dbc438f3cd5d6801a424f7b70" semantic="ac448bdc0d0511e23b7beef678bc36d35b02b4610877afe79699ea4a590e9210" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0`
- **範圍:** `0` ~ `300`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 轉向手感
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSR -->

<!-- CARROT:MANUAL:BEGIN CustomSR -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

轉向比（請參照車輛規格）。

- **調高：** 使用較大的固定轉向比，改變相同曲率下計算出的轉向角度。
- **調低：** 使用較小的固定轉向比。

此設定也適用於 VW MEB（含 ID.4），控制迴圈會重新讀取變更。儲存值乘以 0.1 後大於 1.0 時，使用手動轉向比；否則使用學習所得轉向比及 `SteerRatioRate`。選用手動轉向比不會停止 SR 學習。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同直路及平緩彎道，每次小幅調整一項，檢查延遲、振盪及駕駛介入後的恢復。

先前被忽略的 ID.4 設定值會在更新後生效。使用 `CustomSR=0` 及 `SteerRatioRate=100%` 可保留原本學習所得的轉向比。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> `0` 使用學習所得的轉向比。直接指定的自訂值會優先於 `SteerRatioRate` 倍率。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CustomSR -->

<!-- CARROT:SETTING:END CustomSR -->
