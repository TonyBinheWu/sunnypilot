<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANECHANGE" param="ManualTurnIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 手動轉彎轉向燈（試驗）

**選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)

---

<!-- CARROT:SETTING:BEGIN ManualTurnIndicator -->
<a id="ManualTurnIndicator"></a>

## 手動轉彎轉向燈（試驗）

`ManualTurnIndicator`

結合駕駛員轉向力、方向盤轉動及車輛實際旋轉識別左右轉彎，獨立於ATC，支援車道線不清晰的路口。起始速度5–60km/h，同向轉向力持續0.15秒，轉角至少42度且增加22度，並確認同向車身旋轉。方向盤回到±15度且旋轉穩定、駕駛員反向轉向或持續30秒後結束。預設關閉，適用於Ioniq 5 PE、支援的轉向燈裝置及自動轉向燈模式1或2。停車場轉彎也可能觸發，彎道及避讓動作可能誤觸發，實車燈光驗證待完成。

<!-- CARROT:AUTO:BEGIN ManualTurnIndicator -->
<!-- CARROT:AUTO:SOURCE facts="c26b0bdd4e3bce8120c208b4e9635ac8df75eb58e51fea185cd344f33901242f" semantic="376bcf8235f7ad9de6c1ed48484745355356b0c0edbb66be12b5637052655754" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 轉向 \> 變道 (自動轉向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ManualTurnIndicator -->

<!-- CARROT:MANUAL:BEGIN ManualTurnIndicator -->
<!-- CARROT:REVIEW reviewed-for="376bcf8235f7ad9de6c1ed48484745355356b0c0edbb66be12b5637052655754" reviewed-at="2026-11-08T12:45:07+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 動作

結合駕駛員同向轉向力、方向盤角度增加及新鮮的車身旋轉資料識別轉彎。獨立於ATC和橫向控制啟用狀態，燈光反饋受到自動轉向請求隔離。

方向盤回正且旋轉穩定後結束，駕駛員反向轉向、輸入異常或關閉設定時取消。
上次指示保持結束滿2秒且兩側轉向燈連續熄滅1秒後，才重新識別新的手動轉彎。這兩個等待時間同時計算。
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
