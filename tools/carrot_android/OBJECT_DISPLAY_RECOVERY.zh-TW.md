# 人車物件顯示修正與檢查

此修正位於車機提供的網頁與前鏡頭串流，Formosa 座艙和 CarrotAssist 共用。既有 APK 可沿用；須停車後更新 carrot-wip，完成原生建置並重新啟動車機，再重新連線 App。單獨安裝 APK 不會更新車機的編碼器。

## 為什麼會只剩未分類目標

C3／C3X 的 AR0231／OX03C10 前鏡頭為 1928×1208，舊標準串流的 964×604 正好是其一半。C4 的 OS04C10 為 1344×760，沿用 964×604 會拉伸影像，不符合立體投影的鏡頭比例檢查。新版標準串流使用完整來源畫面的一半：C4 為 672×380；C3／C3X 保持 964×604。360／540／720 的選項仍保留。

物件辨識使用觀看裝置本機的 EfficientDet-Lite0 CPU worker，不會把影像上傳給模型服務。一次只處理一張影像，分類門檻仍為 0.5。首次運算另有 20 秒預熱預算，後續運算逾時仍為 4 秒；這並未延長物件的 1.2 秒有效期限。過期位置不會換上新時間戳後繼續顯示。

## 從哪裡檢查

在「視覺設定」或「應用程式 → 鏡頭與物件辨識」開啟物件辨識，確認已接上前鏡頭。

| 狀態 | 處理方式 |
| --- | --- |
| 等待前鏡頭 | 先連接 Carrot Vision；沒有影像不能辨識 |
| 相機尚未完成校正／高度資料不足 | 等待車機提供有效校正資料，不填入猜測高度 |
| 車機校正／相機資料未更新 | 檢查資料連線，重新連線 |
| 串流比例不符 | 更新並重啟車機；C4 的舊標準串流需更新編碼器 |
| 辨識運算超過時限 | 先關閉道路附加辨識及其他高負載 App，再重試模型 |
| 模型載入／運算失敗 | 在同一畫面重試；仍失敗時回報狀態與觀看裝置型號 |

定位不足時，仍顯示真實分類的影像提示，並明確標示「無 3D 位置」。可定位的行人、汽車、機車等繼續顯示立體模型。未分類的原生雷達參考不會假裝成汽車。只有前鏡頭可見範圍；地面投影是近似位置，並非環景、測量級深度或車輛控制輸入。

## English

Update and rebuild the vehicle, then reboot while parked and reconnect the viewer. Existing APKs load the shared vehicle UI. The standard encoder now preserves full-frame camera aspect: C4 672×380, C3/C3X 964×604. Recognition remains on the viewer's CPU, with unchanged confidence and 1.2-second capture expiry. A one-time cold inference may finish within 20 seconds; its expired output is discarded. Later inference keeps the four-second timeout. Image-only classifications remain visible when calibrated ground projection is unavailable; no depth is invented. The viewer reports missing calibration, stale telemetry, incompatible stream aspect and slow inference separately. These are display fixes, not navigation or steering validation.

## 한국어

주차 상태에서 차량 소프트웨어를 업데이트하고 네이티브 빌드를 완료한 뒤 재부팅하여 앱을 다시 연결하세요. 기존 APK는 차량의 공통 웹 UI를 사용합니다. 기본 영상은 전체 원본 비율을 유지하며 C4는 672×380, C3/C3X는 964×604입니다. 인식은 뷰어 CPU에서 실행되며 신뢰도 기준과 촬영 시점 기준 1.2초 만료는 그대로입니다. 최초 추론에만 20초 예열을 허용하지만 오래된 결과는 표시하지 않습니다. 이후 추론 제한은 4초입니다. 지면 투영이 불가능해도 실제 영상 분류는 깊이 없이 표시하고, 보정 부족·오래된 데이터·비율 불일치·처리 지연을 구분합니다. 내비게이션이나 조향 성능을 검증한 변경은 아닙니다.
