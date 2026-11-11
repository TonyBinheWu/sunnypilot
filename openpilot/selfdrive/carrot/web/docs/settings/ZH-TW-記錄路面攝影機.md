<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SYS_RECORD_BASIC" param="RecordRoadCam" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 記錄路面攝影機

**選單:** 系統 \> 錄製與電源 \> 錄製與電源

---

<!-- CARROT:SETTING:BEGIN RecordRoadCam -->
<a id="RecordRoadCam"></a>

## 記錄路面攝影機

`RecordRoadCam`

1: 標準攝影機, 2: 標準攝影機 + 廣角攝影機

<!-- CARROT:AUTO:BEGIN RecordRoadCam -->
<!-- CARROT:AUTO:SOURCE facts="df4d124b744e4b0c1c6980650e84c423193136b218cd972d6054b24f4012bc68" semantic="ae86d8c67fad0c96a2cfaad63d1ccea6d5408fea17c62cd5a549ab67faf97d69" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `2`
- **步長:** `1`
- **選單:** 系統 \> 錄製與電源 \> 錄製與電源
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END RecordRoadCam -->

<!-- CARROT:MANUAL:BEGIN RecordRoadCam -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `1` — 標準攝影機
- `2` — 標準攝影機＋廣角攝影機
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

檢查儲存空間及電源條件，並於下次錄影或轉為停車狀態時確認結果。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> 錄製廣角攝影機也會增加儲存空間與記憶體頻寬用量。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END RecordRoadCam -->

<!-- CARROT:SETTING:END RecordRoadCam -->
