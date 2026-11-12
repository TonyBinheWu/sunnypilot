<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_RADAR" param="EnableRadarTracks" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 開啟雷達軌跡 (0)

**選單:** 車輛與硬體 \> 雷達

---

<!-- CARROT:SETTING:BEGIN EnableRadarTracks -->
<a id="EnableRadarTracks"></a>

## 開啟雷達軌跡 (0)

`EnableRadarTracks`

-2: VOACC 純視覺測試 -1: 無視覺匹配始終使用 SCC；無 SCC 時使用視覺 0: 始終使用 SCC 縱向距離和相對速度；無 SCC 時使用視覺 1: 僅前雷達與視覺匹配；失敗時使用視覺 2: 前雷達 + 低速 SCC 與視覺匹配；失敗時使用視覺 3: 前雷達視覺匹配失敗後始終使用 SCC；無 SCC 時使用視覺 新視覺目標要求 prob \>= 0.40；所有 SCC 匹配均忽略橫向位置 自動支援傳統 Mando 32/64 槽位版本

<!-- CARROT:AUTO:BEGIN EnableRadarTracks -->
<!-- CARROT:AUTO:SOURCE facts="b4658fdb18f329a648a130938d7a5c6ce2354ff051c3d2abef1b1d8170382514" semantic="0aab8f5fa0c29c37fd4b650cd2a25ffe0451f1c62b9f8fcbcb386721f8c81218" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** `0`
- **範圍:** `-2` ~ `3`
- **步長:** `1`
- **選單:** 車輛與硬體 \> 雷達
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END EnableRadarTracks -->

<!-- CARROT:MANUAL:BEGIN EnableRadarTracks -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值決定 L1 雷達來源及視覺匹配策略。

- `-2` — 測試純視覺控制。
- `-1` — 使用 SCC，不進行視覺匹配；沒有 SCC 時使用視覺。
- `0` — 固定使用 SCC 距離與相對速度；沒有 SCC 時使用視覺。
- `1` — 將不含 SCC 的前方雷達與視覺匹配；匹配失敗時使用視覺。
- `2` — 將前方雷達與低速 SCC 對應至視覺；匹配失敗時使用視覺。
- `3` — 前方雷達／視覺匹配失敗後使用 SCC；前方／角雷達證據顯示該物體位於行車路徑旁時除外。SCC 不存在或遭拒絕時使用視覺。

新的靜止前方雷達物體，須由相應視覺或吻合的角雷達物體確認後，才會成為 L1。僅有長距離觀測時間及高追蹤品質不足以核准；角雷達確認必須持續符合距離、橫向位置及速度。

若另一個被量測的移動目標與視覺位置及速度吻合，該視覺就不能核准或保留不同的靜止反射。附近高品質的靜止回波若與該移動車輛速度矛盾，必須有自身吻合的角雷達證據。角雷達確認僅屬於選定物體本身。只有前方雷達的回波，若距離及速度都偏離視覺，即使更近也會被釋放。

未經確認且缺少相應角雷達佐證的靜止前方目標，若失去視覺支持超過允許的 0.10 秒寬限，會同時重設待確認身分及確認起始時間。重新偵測後須再次完成三個支持影格及新的 0.25 秒確認；不沿用中斷前累積的時間。

對已選定的移動前車，距離防護會使用模型的距離不確定性，而非僅因雷達比視覺遠超過 8 m 就捨棄雷達。雷達與視覺都必須顯示物體以超過 4 m/s 移動，並位於模型路徑中央。同一前方目標必須持續被量測且物理狀態連續，觀測中斷不得超過 0.15 秒。比視覺位置更遠的允許差距為 `max(8 m, min(15 m, 15% of vision distance, 1.5 × xStd))`。新 ID、匹配遺失、無效路徑、位置或速度突變，以及較精確的近方視覺估計，都不會繼承此寬限。這不會增加確認延遲，也不會阻止吻合度更高的較近前車成為 L1。保留的前車使用雷達距離及速度，不會與視覺估計取平均。

平緩彎道上的遠方靜止車輛，在模型速度仍不準確時，可透過反覆的視覺位置吻合取得確認。在 60 m 以外，量測中的前方目標須維持位置與速度連續至少 0.50 秒，並符合 `trackState >= 2`、`|vLead| <= 2 m/s`、`|dPath| <= 1.25 m` 及 `|yawRate| < 0.10 rad/s`。至少兩個視覺機率達 0.40 的影格，須在距離差 5 m 及原始橫向位置差 1.25 m 內吻合；這項近期位置證據會在 0.50 秒後失效。只有同時具備這項證據及足夠的視覺速度不確定性，才允許 `min(24 m/s, 4 × vStd)` 內的速度差；精確的移動速度估計仍會拒絕靜止反射。新目標仍須符合目前距離差在 15 m 內、三個支持影格及 0.25 秒確認時間。雷達 ID 存續時間或單純存在角雷達點，都不足以通過確認。另行確認的移動前方／SCC 目標仍可立即否決。若要否定這個具備位置歷史的前方目標，同一角雷達目標須在連續移動至少 0.15 秒時，同時與視覺位置及速度吻合。實際吻合的前方／角雷達配對，仍保有其獨立佐證。

已確認的靜止前方目標，在仍持續被量測且物理狀態連續時，可容忍短暫的視覺距離雜訊；目標須符合 `|dPath| <= 1.5 m`，且與視覺橫向位置相差不超過 2 m。其比視覺位置更遠的允許差距為 `max(8 m, min(25 m, 25% of vision distance, 2 × xStd))`。距離在 8 m 內吻合或反覆完成位置確認後，此寬限最多持續 0.50 秒。超過 0.15 秒的觀測中斷，以及位置／速度突變，都會重設該歷史。尚未確認的新物體或較精確的近方視覺估計，不會取得此寬限。前車資料仍會發布目前雷達距離與速度。這些規則不保證在所有道路上都能於 100 m 偵測到目標，也不保證完全沒有誤判。
在 `EnableRadarTracks=1`–`3` 模式，當雷達顯示目標向外移動，且視覺也切換至更遠車輛時，已確認正在離開的前車可在 ACC 中取得有限度的未來跟車時距放寬。請參閱[預測前車切出行為（英文）](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/radar.md)。

模式 3 可銜接最多一秒的橫向支持缺失。距離／速度不連續、SCC 或路徑遺失，以及離開此模式，都會重設先前的拒絕紀錄；僅重複使用 ID 不會將紀錄轉移給另一輛車。

一般未改線的 HDA2 配置使用 openpilot 縱向控制時，啟動程序會停止原廠 SCC 發送，原始前方雷達則仍是獨立輸入。此配置不會僅因原廠 SCC 缺失而判定正常的原始追蹤資料無效；必收的原始雷達訊息缺失仍會報錯。Camera-SCC 改線及 passive Bosch 接收維持原有的原廠 SCC 處理方式。模式 `1` 將前方雷達與視覺匹配；原廠發送停止時，模式 `2` 與 `3` 也沒有 SCC 備援資料。變更雷達來源或接線設定後請重新啟動。這不會啟用角雷達。
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
<!-- CARROT:MANUAL:END EnableRadarTracks -->

<!-- CARROT:SETTING:END EnableRadarTracks -->
