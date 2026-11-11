<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_TRAFFIC" param="TrafficStopDistanceAdjust" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 交通訊號停止距離調整

**選單:** 駕駛控制 \> 速度與減速 \> 訊號燈

---

<!-- CARROT:SETTING:BEGIN TrafficStopDistanceAdjust -->
<a id="TrafficStopDistanceAdjust"></a>

## 交通訊號停止距離調整

`TrafficStopDistanceAdjust`

交通訊號停止距離調整

<!-- CARROT:AUTO:BEGIN TrafficStopDistanceAdjust -->
<!-- CARROT:AUTO:SOURCE facts="2e9856750d86a5dfac1bd2770b68f21a2d8ca9d5d42c5c4709ed1101af9ea70f" semantic="2c0307757de5931be931759240b41c4dbfa911d065c2e58f09356222e3b41eaa" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `-150cm`
- **範圍:** `-600cm` ~ `600cm`
- **步長:** `100`
- **顯示單位:** `cm`
- **選單:** 駕駛控制 \> 速度與減速 \> 訊號燈
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TrafficStopDistanceAdjust -->

<!-- CARROT:MANUAL:BEGIN TrafficStopDistanceAdjust -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

車輛行進時，為虛擬號誌停車障礙物加入距離修正。

- **正值：** 將停車目標沿道路往前移。
- **負值：** 將停車目標往本車方向拉近。

停車時，目前程式另使用 `-2 m` 修正。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在同一個視野清楚的路口，確認偵測、停車、重新起步時機及停車位置。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TrafficStopDistanceAdjust -->

<!-- CARROT:SETTING:END TrafficStopDistanceAdjust -->
