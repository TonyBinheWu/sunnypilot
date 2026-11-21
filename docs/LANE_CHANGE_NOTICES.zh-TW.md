# 變道預告、進度與完成確認

車機與已連線的網頁／APK「駕駛視覺」共用變道提示。須停車更新車機並重新啟動，再重新開啟 App 頁面；不必另外開啟自動方向燈。現有 APK 使用車機提供的介面，本次沒有修改 APK 原生程式。

## 會看到什麼

| 提示 | 意義 |
| --- | --- |
| 模型預估向左／右變道 | 模型的近程預測或路徑持續指向該側；請自行確認路況並操作方向燈。 |
| 前方左／右側出口 | 接近導航的出口或分岔；不代表目前車道一定需要變更。 |
| 準備向左／右變道 | 既有變道流程已進入準備階段，仍受原本車道、盲點與駕駛操作條件限制。 |
| 左／右變道流程進行中 | 既有流程正在開始或收尾，不表示已跨線或已完成。 |
| 左／右變道已完成 | 觀察到同方向車道邊界換位，並在新車道穩定置中。 |
| 左／右變道已取消 | 進行中受到符合既有門檻的反向駕駛接管而取消。 |
| 左／右變道流程結束；完成未確認 | 流程已結束，但車道觀測不足以確認實際完成；不會當成成功。 |

預告是畫面提示，不會代打方向燈、觸發轉向、證明旁車道安全或保證固定秒數前出現。不增加語音播報。模型未產生可用預測時，也不會憑導航地址虛構變道需求。

## 完成如何判定

只有既有變道正在執行、橫向控制有效、D 檔且時速至少 30 km/h 時才觀察。兩條內側車道線須有足夠信心、合理車道寬度；先接近目標側邊界，再觀察兩條邊界同方向換位，最後在目標車道中心 ±35 公分內穩定至少 0.6 秒。重複影格、過期資料、低信心或反向接管會中斷這次確認。

確認後結束此次變道意圖，讓下一輪模型不再收到同一次變道請求。這是既有模型輸入與變道狀態機的收尾，不是重新訓練模型、重設神經網路記憶或增加控制能力。保留駕駛明確排隊的下一次變道；單純持續亮著同一側方向燈仍須依原本條件操作，不會因此無限連續變道。

完成、取消與未確認結果短暫顯示 2 秒。沒有觀察到跨線時，方向燈熄滅、時間經過或變道預測降低都不足以宣告完成。這依賴模型車道觀測，不是地面真值；複雜分岔、無標線與遮蔽路段可能無法確認。

## 高速公路導航與近線提示

座艙會持續顯示出口距離與路線。送給駕駛模型的上下匝道與分岔指引，以模型前方地圖能涵蓋的 192 公尺為範圍。

啟用車道偏離警示後，在約 50 km/h 以上、橫向輔助已介入時，若模型持續辨認出兩側標線，且車身中心持續靠近同一側標線，車機會顯示車道偏離並發出提示音。方向燈亮起期間及熄滅後五秒會抑制警示。畫面與提示音使用模型估計位置，請依實際車道接管。

在採用扭力控制的 Kia EV6 上，系統確認駕駛持續向反方向施力後，會依原有速率限制逐步卸除相抵的輔助扭力。

## 何時隱藏

車況、模型、控制與警告狀態任一超過 0.5 秒未更新，CAN 無效、退出 D 檔、橫向關閉、低於 30 km/h、回放或已有行車警告時，新增畫面提示會隱藏。既有盲點阻擋、CAN 錯誤、安全退出、駕駛接管與 Panda 限制繼續優先。

## 驗證範圍

測試涵蓋左右預告、確認跨線／置中、燈滅與時間不能冒充完成、反向取消、等待下一次駕駛操作、舊版封包相容、原生與 Python 編碼一致、畫面切換／過期清除及多種螢幕尺寸。隔離畫面使用合成車況，並非實車閉迴路或道路驗收。既有導航偏移與 CAN 匯流排錯誤仍須獨立依實際紀錄判斷。

2026-11-18 驗證：網頁 1,088 項及相關 Python 184 項通過。正式 SCons 原生編譯與 [原生封包編碼一致性步驟](https://github.com/TonyBinheWu/sunnypilot/actions/runs/44313014178)通過；[訊號整合](https://github.com/TonyBinheWu/sunnypilot/actions/runs/44316247535)含 Panda F4／H7 建置通過。此處只列出已完成的步驟，不代表整套 CI 或實車道路驗收均已通過。

正式座艙在隔離的 1920×720、1280×720、1024×768、390×844 CSS viewport 檢查大字、畫面切換與進出全螢幕。提示會避讓座艙資訊列；一般網頁的儀表模式也會在可見期間訂閱所需模型資料，背景及離開畫面時釋放，與鏡頭啟動權限無關。這是瀏覽器模擬，不是實體 Android 車用盒子測試。

## English

Vehicle and connected Web/APK Vision share read-only advance, preparation, active, completed, cancelled and unconfirmed notices. Forecasts do not operate indicators or initiate steering; nearby exit guidance does not establish a required lane change. No fixed warning lead time is guaranteed. Notices require fresh state, valid CAN, active lateral control, Drive and at least 30 km/h, and yield to existing alerts.

Completion requires observed same-direction boundary relabeling after approaching the selected line, then at least 0.6 seconds of stable centering within 0.35 m. Invalid/stale observations and opposite takeover interrupt confirmation. Confirmed completion ends the current FSM desire for subsequent model inputs; it does not retrain the neural model or reset hidden state. Explicit queued driver requests and existing takeover, blind-spot and Panda protections remain. A lamp ending or a timer alone never proves completion. End results appear for two seconds. Update and restart vehicle source; the native APK is unchanged. Simulated UI and fixed-input replay are not closed-loop road acceptance.

## 한국어

차량과 연결된 웹/APK 주행 시각화에 예측·준비·진행·완료·취소·완료 미확인 상태를 표시합니다. 예고는 깜빡이나 조향을 작동시키지 않으며, 가까운 출구 안내가 현재 차로 변경의 필요성을 증명하지 않습니다. 일정한 사전 안내 시간도 보장하지 않습니다. 최신 데이터·정상 CAN·활성 횡방향 제어·D 기어·30km/h 이상이 필요하며 기존 경고가 우선합니다.

선택한 경계에 접근한 뒤 두 경계가 같은 방향으로 재배치되고, 새 차로 중앙 ±0.35m 이내에서 0.6초 이상 안정적일 때만 완료를 확인합니다. 오래되거나 불확실한 관측과 반대 방향 운전자 개입은 확인을 중단합니다. 확인 시 현재 FSM 변경 의도를 끝내 다음 모델 입력에 반영하지만, 모델을 재학습하거나 신경망 기억을 초기화하지 않습니다. 명시적으로 대기시킨 다음 변경과 기존 개입·사각지대·Panda 보호를 유지합니다. 소등이나 시간 경과만으로 완료를 선언하지 않습니다. 종료 결과는 2초 표시합니다. 차량 소스 업데이트와 재시작이 필요하며 APK 네이티브 변경은 없습니다. 합성 화면과 고정 입력 재생은 실제 도로 폐루프 검증이 아닙니다.
