# 行車影片內嵌車況 SEI

車機 loggerd 在**既有攝影機錄影已啟用**時，替新錄製的 H.265／HEVC 與 H.264 影片逐影格加入 `user_data_unregistered` SEI。這不會開啟原先關閉的錄影、不增加上傳，也不修改畫面像素、攝影機原始資料、rlog 或控制指令。既有影片不會補寫；UI 螢幕錄製及 PC 的 FFVHUFF 無損格式不在此次範圍。

UUID：`d15fb7ea-5569-4bdf-a640-4f524d4f5341`，JSON schema：`formosa.drive.v1`。

| 欄位 | 意義 |
|---|---|
| `frame_id`、`frame_mono_ns` | 影格 ID 與拍攝起始單調時間；缺少起始時間時採既有結束時間 |
| `car_mono_ns`、`control_mono_ns` | 對應車況與控制訊息的時間，供核對同步誤差 |
| `speed_mps` | 車速，m/s；乘 3.6 轉 km/h |
| `steering_angle_deg` | 車機回報的方向盤角度，度 |
| `gas`、`brake` | 原生車況的 0～1 踏板比例；部分車型沒有完整比例，不能當成已校正踏板行程 |
| `gas_pressed`、`brake_pressed` | 原生油門／煞車踩踏狀態 |
| `cruise_enabled` | 原廠 cruiseState 的巡航啟用狀態 |
| `control_enabled` | 車機 carControl 的 enabled 狀態 |
| `lateral_active`、`longitudinal_active` | 橫向與縱向各自是否介入，獨立記錄 |

不把「enabled」標示為 Tesla FSD 或全自動駕駛。資料只選拍攝時間以前、最多相差 **250 ms** 的有效訊息，使用有界歷史以應對編碼／音訊佇列延遲；過期、CAN 無效、尚未收到或數值不合法時為 JSON `null`，不會用最新狀態回填舊影格，也不把未知當關閉。資料不含 GPS、目的地、裝置序號或帳號。

SEI 是影片中的機器可讀資訊，一般播放器不一定顯示。原始 `.hevc` 可直接取回 JSON Lines：

```sh
python tools/carrot_android/extract_driving_sei.py fcamera.hevc --codec hevc > driving.jsonl
```

H.264 使用 `--codec h264`。MP4／TS 容器可先用 FFmpeg 以 `-c:v copy` 及相應 `hevc_mp4toannexb`／`h264_mp4toannexb` 匯出原始串流，再讀取；重新編碼或第三方剪輯可能移除 SEI，請保留原檔。解讀工具僅讀本機檔案、不連網。

已以 C++ 編譯與執行檢查因果時間、250 ms 邊界、無效訊息、亂序、有界歷史、H.264／H.265 NAL、AUD 順序與防起始碼跳脫。另用 FFmpeg 產生各 12 影格影片，再透過實際 C++ 注入函式加上逐影格資料：兩種格式解碼後 framemd5 完全相同，均取回 12 筆正確資料及交替縱向狀態。這是合成影片驗證，尚不能當成實車錄影的長時間或所有播放器相容性驗收。
