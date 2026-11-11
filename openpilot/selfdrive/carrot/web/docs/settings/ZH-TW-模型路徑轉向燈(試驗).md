<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="ModelPathIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 模型路徑轉向燈（試驗）

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN ModelPathIndicator -->
<a id="ModelPathIndicator"></a>

## 模型路徑轉向燈（試驗）

`ModelPathIndicator`

車速至少30km/h，模型未來1至3秒路徑持續越過彎曲車道邊界，且控制曲率方向一致時顯示轉向燈。要求目標線置信度至少10%、連續邊界及重複觀測。排除左側中央線及右側道路邊緣，不新增自動轉向請求。 預設關閉，僅支援Ioniq 5 PE、Jetson USB2CAN及自動轉向燈模式1或2；實車驗證另行進行。

<!-- CARROT:AUTO:BEGIN ModelPathIndicator -->
<!-- CARROT:AUTO:SOURCE facts="3bc7ff4270b7e83fd03062fbde095c5125648d7188f13b259d62ab75a4a8c5ec" semantic="09c4851f68312e9070186bb23698703b51d5b7dce50dbeca5e9cb4cf5626b6c8" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ModelPathIndicator -->

<!-- CARROT:MANUAL:BEGIN ModelPathIndicator -->
<!-- CARROT:REVIEW reviewed-for="09c4851f68312e9070186bb23698703b51d5b7dce50dbeca5e9cb4cf5626b6c8" reviewed-at="2026-11-01T04:38:46.048274+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

在相同前方位置比較模型路徑與彎曲邊界，檢測持續越線。要求目標線置信度至少10%、連續幾何、重複觀測，以及相對道路曲率一致的控制方向。

僅重新識別車道線不會產生新請求，生成的訊號不會請求轉向。寬路肩及路口仍存在邊界估計侷限。
手動及模型顯示僅在請求時間、方向和撥杆計數一致時有限識別自身輕觸反饋。反向輸入、撥杆鎖定或接收端檢測到駕駛員介入時取消。先於傳送完成應答的點燈反饋會短暫記憶，但保持仍須匹配應答；短暫傳送期間同方向人工操作無法僅憑這些資訊完全區分。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ModelPathIndicator -->

<!-- CARROT:SETTING:END ModelPathIndicator -->
