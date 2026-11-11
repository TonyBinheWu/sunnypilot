<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_TRAFFIC" param="SignalAssistMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 訊號輔助模式（試驗）

**選單:** 駕駛控制 \> 速度與減速 \> 訊號燈

---

<!-- CARROT:SETTING:BEGIN SignalAssistMode -->
<a id="SignalAssistMode"></a>

## 訊號輔助模式（試驗）

`SignalAssistMode`

0:關閉識別、顯示及控制。1:行駛中持續顯示識別結果，提供提醒及停車時紅燈起步限制。2:在1的基礎上增加行駛中減速準備；確認有效紅燈且50米以內沒有前車時逐漸請求約-0.5m/s²。任一跟蹤前車進入50米以內則取消輔助減速，保留原有跟車。停車後與模式1相同，輔助減速不直接要求停車。停車紅燈起步限制僅在5km/h及以下保留，超過該速度後清除此前的停車記憶。夜間需要兩個紅燈及道路方向支援；紅燈證據消失或綠燈衝突時取消準備。顯示與控制介入獨立，舊結果最多暗顯2秒後轉為未知。與主模型獨立，試驗功能仍可能誤檢或漏檢。

<!-- CARROT:AUTO:BEGIN SignalAssistMode -->
<!-- CARROT:AUTO:SOURCE facts="6cf47229c740b81e2b58e92bea5c6689617df9c362cc4864eeaa3b6523fac664" semantic="ba8119151eab7971db5323d2e70e29e83140178360a67bae13fb690b0084d730" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `2`
- **步長:** `1`
- **選單:** 駕駛控制 \> 速度與減速 \> 訊號燈
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SignalAssistMode -->

<!-- CARROT:MANUAL:BEGIN SignalAssistMode -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END SignalAssistMode -->

<!-- CARROT:SETTING:END SignalAssistMode -->
