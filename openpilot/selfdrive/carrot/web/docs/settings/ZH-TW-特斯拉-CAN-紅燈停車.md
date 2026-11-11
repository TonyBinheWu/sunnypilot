<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BASIC_START" param="TeslaCanTrafficStop" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 特斯拉 CAN 紅燈停車

**選單:** 駕駛控制 \> 啟動·自動 \> 起步動作

---

<!-- CARROT:SETTING:BEGIN TeslaCanTrafficStop -->
<a id="TeslaCanTrafficStop"></a>

## 特斯拉 CAN 紅燈停車

`TeslaCanTrafficStop`

預設關閉，修改後重新啟動。僅 Tesla Model 3/Y 且 openpilot 縱向已啟用時，使用新鮮 APP\_trafficControl 紅燈及小於126米的停止線補充停車約束。僅支援8位元組、米制、視覺來源協議，拒絕6位元組 DAS\_road。綠燈只解除本約束，不覆蓋其他障礙和人工停車。近距離變紅可能超出制動能力；訊號丟失或距離不一致會提示接管並請求既有軟退出。需核對實車協議和距離參考點，並在封閉場地驗證，不代表已透過道路驗收。

<!-- CARROT:AUTO:BEGIN TeslaCanTrafficStop -->
<!-- CARROT:AUTO:SOURCE facts="785b74797a55b428a6930af304a4deffedc5f345b96ea39089a8de13c0e31fd2" semantic="046215718bed37d52f0c6633e5d551de2ff163be2a341b1cb647fab8b5f803dc" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 啟動·自動 \> 起步動作
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaCanTrafficStop -->

<!-- CARROT:MANUAL:BEGIN TeslaCanTrafficStop -->
<!-- CARROT:REVIEW reviewed-for="046215718bed37d52f0c6633e5d551de2ff163be2a341b1cb647fab8b5f803dc" reviewed-at="2026-11-08T01:13:19.667172+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

開啟後僅在 Model 3/Y 實際 openpilot 縱向啟用時補充停車，關閉保留原行為。3次不同紅燈跨越0.2秒且正停止線小於126米，在 ACC/blended 新增約束；同一目標3次連續綠燈跨越0.5秒，僅解除此約束。CAN 停車期間 blended 臨時使用 ACC 求解，保留更強模型制動，解除後恢復原模式。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

修改後重啟，獨立於打燈、資料共享及訊號輔助。僅接受嚴格8位元組、米制、視覺來源 APP_trafficControl，拒絕6位元組 DAS_road。踩踏板後需退出並重新接入、等待新觀測；其他車型忽略此開關。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

先在封閉場地核對原始 CAN、行駛方向適用性及暫定2米停車餘量。近距離變紅可能超出制動能力；訊號超過0.5秒未更新或目標跳變會請求接管和最終解除控制的軟退出，駕駛員必須制動。不增加 Panda 許可權，不代表道路驗收。詳見原始碼倉庫 docs/user/zh/tesla.md。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaCanTrafficStop -->

<!-- CARROT:SETTING:END TeslaCanTrafficStop -->
