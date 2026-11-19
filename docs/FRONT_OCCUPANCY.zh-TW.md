# 前鏡頭即時 3D 環境佔用

在 FORMOSA 座艙或 Carrot Web 的駕駛視覺裡，前鏡頭現在可以畫出地面和高於地面的可見表面。物體即使沒有分類名稱，也能產生佔用觀測。網路另外估計視線抵達表面之前的可見空間。單一前鏡頭的覆蓋範圍有限，請以車外實況判斷通行空間。

## 開啟與閱讀

1. 將車機更新到含本功能的 `carrot-wip`，重新啟動，讓座艙連線。已安裝的 FORMOSA 座艙 0.6.3 可沿用。
2. 在座艙開啟「應用程式 → 鏡頭與物件辨識」，打開「3D 環境佔用（研究）」。Carrot Web 也能在網頁設定的駕駛視覺項目開啟。開關預設關閉。
3. 進入 3D 駕駛視覺。首次使用由車機下載約 36 MB 的非商用研究模型，後續由車機快取提供。觀看裝置的 WebGL 2 與 WebAssembly、前鏡頭串流及有效安裝校正均須就緒。狀態頁提供模型載入、校正、運算過慢與重試提示。
4. **青色方格**代表模型推估的第一個可見表面。靠近地面的格子壓平為地磚，較高的格子則畫成立方體。**淡紫色短線**表示表面可能落入的一段距離。缺少足夠證據時保留空白。車旁、車後和遮擋物後方皆可能是未知區域。

這項功能只使用本機觀看中的道路鏡頭。開啟此圖層不會開啟 FormosaLink 的研究上傳，圖層也不向轉向、煞車或路徑規劃提供輸入。既有雷達、分類物件和車道線各自繼續運作。

## 影像如何變成立體方格

- 依支援的前鏡頭設定和當時的安裝校正，擷取約 37.6° × 21.7° 的中央視野。輸入為 224 × 126 RGB。支援的道路鏡頭設定為 OS04C10、AR0231、OX03C10。鏡頭種類、串流比例、安裝高度或校正無效時會暫停。
- 戶外公制深度骨幹與光達監督訓練的卷積網路，在 64 × 36 條視線上，各輸出 43 格深度的佔用機率及可見空間機率。涵蓋光軸前方 2 到 45 公尺，每格 1 公尺。經安裝姿態投影到車身座標後，重複的立方體合併。格距是顯示解析度，實際估距誤差依畫面而異。
- 較集中的表面機率才畫實格。較分散的離地表面，取模型分布中間 50% 的深度區間，每四條視線取樣一次，區間最長 8 公尺。這些區間的實際命中率依路段而異。模型不為遮擋後方補上幾何。
- 觀看裝置的背景執行緒負責推論。渲染使用同一批 GPU 物件並依新近車速與轉向角速度補償自車移動。資料從畫格擷取起最多保留 0.9 秒；失去視訊、校正或有效車況時清除。移動物體的方向與速度仍由原本的物件追蹤處理。

## 與光達對照的結果

以下為最終發行的量化 ONNX。使用 KITTI 2011-09-26 四趟行程（0001、0002、0005、0015）共 176 張影格、127,088 筆稀疏光達參考來訓練佔用輸出層。下列三趟行程均未用於訓練該輸出層。只比較中央視野中具有獨立光達參考且鄰近深度一致的像素。三趟結果均曾在開發過程中檢視，仍需要新的台灣保留行程評估泛化能力。

| KITTI 行程 | 影格 | 有光達參考的視線 | 同一公尺深度格的精確率 | 同一格的召回率 | 願意畫實格時的前後距離中位誤差 |
|---|---:|---:|---:|---:|---:|
| 0013 | 36 | 26,656 | 49.6% | 25.1% | 0.51 m |
| 0017 | 29 | 20,047 | 39.9% | 28.8% | 0.65 m |
| 0019 | 61 | 47,456 | 45.1% | 20.6% | 0.57 m |

上表是沿相機視線的深度指標。離地表面的表現弱於地面。以相機高度 1.65 公尺近似，在行程 0019 有 13,137 筆約離地 0.5–6 公尺的光達參考，其中只有 2 筆同時獲實格輸出且落在正確的一公尺深度格。另有 249 條可對照的淡紫色估距線，其中 152 條涵蓋實際光達回波。牆面、細柱及懸空障礙物都可能漏掉或被投在錯誤深度。若要重建可用於駕駛的完整環境，仍需多視角或獨立深度量測、精準同步，以及夜間、雨天與台灣道路的實車驗證。

以真實 KITTI 影片送進正式網頁、模擬車況與校正，在桌面 Chromium 測過 1920 × 720、1024 × 768、393 × 852、全螢幕、切到設定再返回及拔除影像。桌面的執行速度不代表手機、Android 車用盒子或車機的運算速度。

## 模型、資料與重現

### 開發電腦 GPU 與手機回放

Windows 工作站用 ONNX Runtime DirectML 執行佔用模型，瀏覽器用 WebGL 2 繪製 3D 畫面。手機座艙接收最新一幀，也可調整視角。等待傳送與解碼的時間都計入 900 毫秒的有效期間，逾時便清除舊畫面。請在工作站安裝 NumPy、aiohttp、onnxruntime-directml 與網頁專案相依套件，準備下節指定雜湊的模型及已校正的前鏡頭影片。

以下以 PowerShell 示範。本例內參僅適用於本次校正過的測試影片。請依影片實際裁切、縮放、相機高度及安裝角度填值，角度以弧度表示。

```powershell
npm ci --prefix openpilot/selfdrive/carrot/web
python -m tools.carrot_mapping.gpu_preview formosa-front-occupancy-v1.onnx rectified.mp4 --fx 570.75 --fy 570.75 --cx 336 --cy 190 --height-m 1.65 --rpy 0 0 0
```

在開發電腦開啟 `http://127.0.0.1:7000/render` 播放影片，另開 `http://127.0.0.1:7000/cockpit` 觀看座艙。要用手機觀看，在啟動指令加上 `--listen 電腦區網IP --viewer 手機區網IP`，並讓手機連至該電腦。服務只供這台手機讀取開發回放；手機畫面上的車況為停車測試資料。

RTX 2080 Ti 搭配 Samsung 手機實測，在 35 秒內收到並顯示 119 張新的道路體素畫面。另一項同卡 N16 測試以每幀 50 毫秒為期限，先跑駕駛模型，時間足夠才接受座艙工作；駕駛逾時或座艙超出預估時間時暫停座艙。最近一次 150 幀測試觸發了暫停。此策略目前用於開發回放量測，實車 AMD USB eGPU 共用仍待同卡硬體驗證。可執行 `python -m tools.carrot_mapping.gpu_priority_bench bench --help` 查看量測入口。

單檔 `formosa-front-occupancy-v1.onnx` 共 35,939,304 位元組，SHA-256 為 `d477bac0f82ace6c8663b222d2c0c00987906a6939f545a5fdf60ef81138b787`。車機及觀看端均檢查檔案完整性。[模型與授權附件](https://github.com/TonyBinheWu/sunnypilot/releases/tag/formosa-front-occupancy-research-v1)

骨幹引用 Yang 等人的 Depth Anything V2 戶外 Small（Apache 2.0），固定版本 `fd2c22027eaf20374204f14099b8341e1925ad39`。FORMOSA 新的佔用輸出層以 KITTI 研究資料訓練，以 CC BY-NC-SA 3.0 提供非商業研究使用。資料作者為 Andreas Geiger、Philip Lenz、Christoph Stiller 和 Raquel Urtasun。[骨幹模型](https://huggingface.co/depth-anything/Depth-Anything-V2-Metric-Outdoor-Small-hf) · [KITTI 同步道路影像與光達](https://www.cvlibs.net/datasets/kitti/raw_data.php) · [研究授權](https://creativecommons.org/licenses/by-nc-sa/3.0/)

研究工作站需要 NumPy、Pillow、PyTorch、Transformers 4.x、ONNX 和 ONNX Runtime。以下指令假設已從 KITTI 下載日期相符的校正及同步行程 ZIP，在空的輸出目錄中執行。

```powershell
$m = 'tools.carrot_mapping.cockpit_occupancy'
python -m $m export depth-fp32.onnx
python -m $m quantize depth-fp32.onnx depth.onnx
foreach ($drive in '0001','0002','0005','0015','0013','0017','0019') {
  $step = if ($drive -eq '0019') { 8 } elseif ($drive -in '0001','0002') { 3 } else { 4 }
  python -m $m prepare "2011_09_26_drive_${drive}_sync.zip" 2011_09_26_calib.zip depth.onnx "$drive.npz" --step $step
}
python -m $m train head.pt 0001.npz 0002.npz 0005.npz 0015.npz
python -m $m export environment-fp32.onnx --head head.pt
python -m $m quantize environment-fp32.onnx environment.onnx
python -m $m evaluate 2011_09_26_drive_0019_sync.zip 2011_09_26_calib.zip 0019.npz environment.onnx
```


### 車機 USB AMD 與雙鏡頭停車量測

FormosaLink 裝置資訊頁顯示的 USB 連線速率來自車機目前枚舉到的橋接器。確認駕駛模型確實使用 eGPU，可以查看新版座艙的「駕駛模型前車來源」，或讀取行車紀錄中的模型執行後端。速率與驅動溫度、板卡顯存、實際推論耗時是不同的讀值。

車機停車熄火後，可用 `python -m tools.carrot_mapping.usb_gpu_objects yolox_nano.onnx road.rgba wide.rgba` 對已錄製的遠距與廣角影格進行獨立 GPU 量測。兩份檔案應由同一時間的兩顆實際鏡頭產生，等比例縮放並補邊成 416×416 RGBA。工具會核對官方 YOLOX-Nano 模型雜湊、橋接器韌體與 gfx1200 執行環境，輸出每顆鏡頭的辨識類別和成對處理耗時。超時、點火或停車資料過期會結束測試。此量測使用駕駛模型既有的獨占鎖，結果不送入車輛控制。實車行駛中同卡執行第二套辨識模型的時限仍須另外驗證。
