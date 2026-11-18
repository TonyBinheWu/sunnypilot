# 導航模型底圖有效性修正

導航模型使用的灰階底圖，與網頁／APK 顯示給駕駛的地圖是不同資料。這次修正的是底圖失效後，模型端是否仍會接收該影像。

## 修正內容

- 定位不可用、圖磚載入失敗或繪製超過 500 毫秒時，`mapsd` 原本會輸出空白影像，卻仍附上當前路線識別碼。現在失效影像的路線識別碼歸零。
- 模型端收到失效影像時，立即撤銷上一張底圖。為支援程式更新時新舊程序並存，也拒收舊版程序送出的全黑失效影像。
- 既有的路線一致性、影像 500 毫秒及導航指令 2 秒新鮮度檢查保留。未改變轉向輸出、車型限制、Panda 保護或 CAN 錯誤退出規則。

## 已驗證與限制

回歸測試以正式發布迴圈驗證「有效 → 定位中斷／圖磚失效／繪製逾時 → 恢復」的識別碼及影像變化，並驗證新收到的失效影像不會讓模型繼續使用舊底圖。測試的 IPC、定位與圖磚來源完全隔離，不會連接實車或發送控制。

這修復了一個確定存在的有效性傳遞問題；不能據此認定任一次偏移都由空白底圖造成。實際偏移仍須比對當次紀錄的模型輸出、有效路線、導航指令、定位及駕駛接管。CAN 訊息遺失造成的安全退出，也必須獨立調查，不能靠隱藏警告或延長容許逾時來宣稱修復。

更新車機程式並重新啟動後生效。這次沒有修改 APK 原生程式；現有座艙版與 CarrotAssist 會使用更新後車機提供的共用網頁功能。

## English

Invalid map renders now publish route ID zero. The model consumer immediately revokes cached maps and rejects legacy all-black invalid frames during rolling updates. Existing route and freshness gates, steering limits, Panda protection and CAN disengagement rules remain unchanged. Isolated production-loop tests cover position loss, missing tiles, slow renders and recovery. This fixes a verified validity propagation defect; it does not establish the cause of an individual navigation deviation. Vehicle source update and restart are required; no native APK change is involved.

## 한국어

유효하지 않은 지도 프레임은 이제 경로 ID 0으로 전송됩니다. 모델 수신부는 기존 지도 캐시를 즉시 해제하고, 순차 업데이트 중 구버전이 보내는 검은 무효 프레임도 거부합니다. 경로·최신성 검사, 조향 한계, Panda 보호 및 CAN 오류 해제 규칙은 유지됩니다. 격리된 실제 송신 루프 테스트로 위치 손실, 타일 오류, 느린 렌더링 및 복구를 확인했습니다. 이는 확인된 유효성 전달 오류의 수정이며, 특정 주행 편향의 원인이 입증되었다는 의미는 아닙니다. 차량 소스 업데이트와 재시작이 필요하며 APK 네이티브 코드는 변경하지 않았습니다.
