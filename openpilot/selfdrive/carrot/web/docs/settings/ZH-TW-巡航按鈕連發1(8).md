<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BUTTON_TEST" param="CruiseButtonTest1" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 巡航按鈕連發1(8)

**選單:** 駕駛控制 \> 按鈕·預設 \> 按鈕測試

---

<!-- CARROT:SETTING:BEGIN CruiseButtonTest1 -->
<a id="CruiseButtonTest1"></a>

## 巡航按鈕連發1(8)

`CruiseButtonTest1`

僅限非縱向控制車輛，速度按鈕訊號傳送限制時間

<!-- CARROT:AUTO:BEGIN CruiseButtonTest1 -->
<!-- CARROT:AUTO:SOURCE facts="78be2132bd9ec4a344d6d218fa50038a63f196ef7c190e8d19b928efd601aedb" semantic="b76fc3c2fedf34451067daab249e5a3933c4cbbe94d61cbb0fd5198798b31a2f" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0`
- **範圍:** `1` ~ `20`
- **步長:** `1`
- **選單:** 駕駛控制 \> 按鈕·預設 \> 按鈕測試
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseButtonTest1 -->

<!-- CARROT:MANUAL:BEGIN CruiseButtonTest1 -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

僅供未由系統控制縱向的車輛使用：速度按鈕訊號傳送限制時間。

- **調高：** 延長每個按鍵訊息的傳送週期。
- **調低：** 縮短傳送週期。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

僅在使用原廠 SCC 按鈕訊息、且未由系統控制縱向的車輛上調整；每次變更一項，檢查是否漏送或過量輸入。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 此設定會直接影響非 openpilot 縱向控制車輛的原廠 SCC 按鍵訊息。請先記錄預設值，並僅在已驗證的車輛上調整。
<!-- CARROT:NOTICE:END -->

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseButtonTest1 -->

<!-- CARROT:SETTING:END CruiseButtonTest1 -->
