<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="ManualTurnIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 手動轉彎轉向燈（試驗）

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN ManualTurnIndicator -->
<a id="ManualTurnIndicator"></a>

## 手動轉彎轉向燈（試驗）

`ManualTurnIndicator`

結合駕駛員轉向力、方向盤轉動及車輛實際旋轉識別左右轉彎，獨立於ATC，支援車道線不清晰的路口。起始速度5–60km/h，同向轉向力持續0.15秒，轉角至少42度且增加22度，並確認同向車身旋轉。方向盤回到±15度且旋轉穩定、駕駛員反向轉向或持續30秒後結束。預設關閉，適用於Ioniq 5 PE、支援的轉向燈裝置及自動轉向燈模式1或2。停車場轉彎也可能觸發，彎道及避讓動作可能誤觸發，實車燈光驗證待完成。 手動變道指示期間符合相同方向的手動轉彎條件時，延續原請求並改依轉彎完成條件追蹤。

<!-- CARROT:AUTO:BEGIN ManualTurnIndicator -->
<!-- CARROT:AUTO:SOURCE facts="ffb82d362231246afd407b601bb973761c3d8337521a73d66d577704eca4b82e" semantic="e08aa7e7e006ddb909a0060571a3f7983d6c70f1249f7f29cc42c19e87f3451a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ManualTurnIndicator -->

<!-- CARROT:MANUAL:BEGIN ManualTurnIndicator -->
<!-- CARROT:REVIEW reviewed-for="e08aa7e7e006ddb909a0060571a3f7983d6c70f1249f7f29cc42c19e87f3451a" reviewed-at="2026-11-14T02:05:14Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 動作

結合駕駛員同向轉向力、方向盤角度增加及新鮮的車身旋轉資料識別轉彎。獨立於ATC和橫向控制啟用狀態，燈光反饋受到自動轉向請求隔離。

方向盤回正且旋轉穩定後結束，駕駛員反向轉向、輸入異常或關閉設定時取消。
上次指示保持結束滿2秒且兩側轉向燈連續熄滅1秒後，才重新識別新的手動轉彎。這兩個等待時間同時計算。
手動變道指示期間符合同向手動轉彎條件時，延續原請求及確認，並改按轉彎完成條件追蹤，不重新輕觸。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

Git Pull後重啟comma並開啟此選項。適用於Ioniq 5 PE、支援的轉向燈裝置及自動轉向燈模式1或2。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

停車場通道、坡道及泊車轉向也可能觸發。無清晰車道線的彎道和避讓動作可能誤觸發，實際燈光驗證待完成。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END ManualTurnIndicator -->

<!-- CARROT:SETTING:END ManualTurnIndicator -->
