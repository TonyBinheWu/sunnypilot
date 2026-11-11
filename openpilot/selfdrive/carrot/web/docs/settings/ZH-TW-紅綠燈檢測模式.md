<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_TRAFFIC" param="TrafficLightDetectMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 紅綠燈檢測模式

**選單:** 駕駛控制 \> 速度與減速 \> 訊號燈

---

<!-- CARROT:SETTING:BEGIN TrafficLightDetectMode -->
<a id="TrafficLightDetectMode"></a>

## 紅綠燈檢測模式

`TrafficLightDetectMode`

0: 無, 1: 僅停止, 2: 停止和起步

<!-- CARROT:AUTO:BEGIN TrafficLightDetectMode -->
<!-- CARROT:AUTO:SOURCE facts="c95dc200429696a622ba14606307486f4df483bdef78f63d6722ef531bac24cd" semantic="fd5f942d148667ec255b07cf1ad246adcea8b41be25a134af644d9c7d0792e99" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `2`
- **範圍:** `0` ~ `2`
- **步長:** `1`
- **選單:** 駕駛控制 \> 速度與減速 \> 訊號燈
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TrafficLightDetectMode -->

<!-- CARROT:MANUAL:BEGIN TrafficLightDetectMode -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 無
- `1` — 僅停車時
- `2` — 走停跟車
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在同一個視野清楚的路口，確認偵測、停車、重新起步時機及停車位置。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 紅綠燈偵測是輔助功能；駕駛仍須確認實際號誌與交通狀況。
<!-- CARROT:NOTICE:END -->

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TrafficLightDetectMode -->

<!-- CARROT:SETTING:END TrafficLightDetectMode -->
