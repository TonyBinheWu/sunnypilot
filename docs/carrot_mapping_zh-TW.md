# 前方車道建圖、多趟比對與 BEV 審查

本功能是**離線研究工具**，使用既有模型預測與另外提供的位姿，產生可審查的公尺尺度車道候選。網頁／APK「工具 → 車道建圖與多趟比對」可查看成果。沒有接入轉向、縱向、導航或訓練；不是 Tesla 的模型或車隊服務，也沒有取得其資料。

## 已提供與尚需建置的部分

| 技術方向 | 目前可使用 | 還缺少的配套 |
|---|---|---|
| 3D 車道候選 | 擷取 modelV2 車道 XYZ；以外部 world_from_model 位姿轉到共用 ENU；JSON／PLY 匯出 | 經校驗軌跡、實測精度基準；沒有建築物、號誌或交通標誌建圖 |
| 多車、多趟比對 | 共用框架逐格比對、趟次／車輛來源、分散度、不可覆寫修訂與父版本 | 跨趟配準、閉環與全域最佳化須外部先完成；框架同名不能證明對齊 |
| 動態更新 | 重建時比較新增觀測／本次未觀測／格內位移 | 不能自動認定道路變更；須覆蓋檢查、審查與核准 |
| 自動標註 | 模型輔助車道候選、BEV／3D、人工保留／排除／複查、審查 JSON | 不是訓練真值；仍需與原影像精確配對、獨立標註與評估 |
| VIO | 最佳化位姿輸入契約與時間檢查 | 未新增 VIO 求解器；需要原始影像／IMU、時空校正及 VIO／SLAM 後端 |
| 前方物件／BiFPN | 既有觀看端 EfficientDet-Lite0 辨識人、自行車、汽車、機車、公車、卡車，與建圖分開 | 未訓練 BEV／occupancy 網路；2D 框不等於精確 3D 位置 |
| 夜間／雨天 | 低機率、高不確定度、校正／位姿品質不足時排除 | 沒有新增雨夜權重，不保證任何光線下可靠 |

近期另加入車主可啟用的道路觀測回傳、離線 OSM 疊圖及工作站佔用網路實驗。以下流程仍供已取得外部最佳化位姿的離線資料使用。[即時道路環境研究與獨立精度評估](ROAD_SCENE_RESEARCH.zh-TW.md)

## 前窄角＋廣角能做什麼

兩個前鏡頭提供互補前方視野，配合 IMU、連續影像與校正，可作為 VIO／多視角研究輸入。工具取出既有駕駛模型的車道結果，沒有把兩路影像當作兩份獨立量測或啟動另一個駕駛模型。

兩鏡頭不會自動變成深度雙目系統。雙目深度需要已知基線、內外參、可匹配且同步的視野；不同畸變、解析度、曝光也要處理。[OpenCV 深度原理](https://docs.opencv.org/4.8.0/dd/d53/tutorial_py_depthmap.html)說明深度與基線、焦距、視差的關係。BEV 平面投影無法補出遮擋物體、高架下方或側後方環境。

## 額外配套清單

| 項目 | 必要性與用途 |
|---|---|
| 原始影像＋IMU | VIO／重新標註需要原始訊號；影片、rlog、影格 ID、曝光與硬體時間須能配對。只有 rlog 的車道預測不足以重建完整感知。 |
| 時間同步 | 確認兩路影像、IMU、GNSS 的共同時基與延遲；rolling shutter 另需讀出時間。不可用網頁收到訊息的時間當曝光時間。 |
| 校正工具與固定安裝 | 每台鏡頭內參、畸變、相機－IMU 六自由度外參及平移桿臂；rpyCalib 不是完整測量校正。CameraYawTrimDeg／實際輸入 warp 也須計入 world_from_model。 |
| VIO／SLAM 工作站 | 在 Linux 電腦／NAS 離線處理尺度、閉環、跨趟配準與異常值；避免高負載求解／訓練進入駕駛程序。可評估 [VINS-Fusion 官方專案](https://github.com/HKUST-Aerial-Robotics/VINS-Fusion)，另行整合並處理其授權；本分支沒有內嵌該程式。 |
| RTK GNSS＋基站或 NTRIP＋同步訊號 | 針對全球一致且可驗證的高精度地圖規劃。一般 GPS、僅累積 livePose.velocityDevice 不足以保證公分精度；固定解、天線桿臂、遮蔽／失鎖皆需品質檢查。 |
| 獨立測量基準 | 測量控制點、測量級定位，必要時測量 LiDAR，供獨立精度驗證；LiDAR 不是先看候選圖的必備設備。 |
| 側後攝影機 | 要完整呈現周圍車、人、機車才需要；前鏡頭無法填補側後盲區。 |
| 儲存與備份 | 保留選定原始資料、校正、位姿、成果與審查。容量以兩路實際總碼率×秒數÷8，加 IMU、紀錄、衍生資料及備份估算。 |
| 訓練／評估平台 | 新車道、深度、occupancy 或雨夜辨識需要標註資料、訓練 GPU、獨立測試集與按條件評估；BiFPN 不能代替資料和驗證。 |
| 私有資料管理 | 多車使用者同意、假名化、位置保存期限、存取控制、版本回退及審查。本次未啟用 FormosaLink 自動收集／上傳。 |

候選圖工具主要用 CPU／NumPy，不需新增 GPU；VIO 效能依後端實測，訓練另估算。**AMD 需先確認確切型號與作業系統**，對照 [Linux](https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/compatibility/compatibilityrad/native_linux/native_linux_compatibility.html)及 [Windows 支援矩陣](https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/compatibility/compatibilityryz/windows/windows_compatibility.html)；不能假設所有卡或整套 ROCm 支援 Windows。本次沒有安裝／修改驅動。

## 離線操作

在儲存庫根目錄、已有完整 openpilot cereal／LogReader 環境的 Linux 工作站執行。純建圖需 Python 3.12+／NumPy；擷取另需專案原生相依套件。不可用 opendbc 縮減版紀錄 schema 判斷服務是否存在。

### 1. 合成範例

```sh
python -m tools.carrot_mapping demo --output demo-map.json
```

網頁「合成範例」也可直接看，不需檔案。範例不是道路精度測試。

### 2. 擷取指定本機紀錄

```sh
python -m tools.carrot_mapping extract \
  --rlog /path/to/rlog.zst --trip trip-a --vehicle vehicle-a \
  --clock boot-a --output trip-a.jsonl
```

僅接受本機檔案，不自動下載 route。使用假名，不用真實 dongle ID；相同趟次跨段維持 trip／vehicle／clock，重開機必須換 clock。輸出含 frame ID、timestampEof、原生校正與模型車道，不含影片或定位地名。

每次最多 100,000 模型影格；長資料分案處理。有效且最近 2 秒內的完成校正才可用。先寫 .partial，成功才不可覆寫發布；失敗 partial 只供診斷，不可當完整資料。

### 3. 準備外部最佳化位姿

工具**不會從 livePose 自動生成高精度全球軌跡**。由校正過的 VIO／RTK／測量流程提供 poses.json；source 是產製者聲明，工具未證實其精度。

```json
{
  "schema": "carrot-mapping-poses/v1",
  "frame": {"id": "survey-origin-001", "axes": "ENU", "units": "m"},
  "trajectories": [{
    "trip_id": "trip-a", "vehicle_id": "vehicle-a", "clock_id": "boot-a",
    "calibration_id": "camera-imu-model-v1", "source": "vio_optimized",
    "poses": [{
      "timestamp_ns": "1000000000", "frame_id": 10,
      "translation": [0, 0, 0],
      "quaternion_wxyz": [0, 0.7071067811865476, 0.7071067811865476, 0],
      "position_std_m": 0.2, "orientation_std_deg": 0.5
    }]
  }]
}
```

以上只是格式例，不能直接把時間、影格或誤差套用在實際紀錄。

- 旋轉與平移必須合成 **world_from_model**：該模型影格 calibrated FRD（前／右／下）到 ENU（東／北／上），不可直接填 IMU、GNSS 天線或 optical frame 的 pose。例中 quaternion 對應向北，右側為東。
- 必須含鏡頭－IMU 平移／旋轉、模型校正／yaw trim 等實際轉換；calibration_id 是外部版本標識，不是工具完成校正的證明。原生 rpy 不能代替完整外參。
- 時間使用曝光 EOF 所在的**開機單調時鐘納秒字串**。其他 VIO 時鐘先校正偏移／漂移；GPS UTC、Unix、瀏覽器時間不能混用。每趟 observation／pose 的 clock 必須一致。
- 時間嚴格遞增；本版取最近一筆，不插值。時間差限 25 ms，有 frame_id 還須相同。此納入門檻**不代表影像訓練對已精確同步**。
- 多趟先外部配準到同一原點、方向、尺度；原點改變須換 frame.id。工具只核對框架標識與軸向，無法證明真的對齊。
- 位置 std≤1 m、姿態 std≤2°、車道機率≥0.7、車道 std≤1 m。另以位置 std＋車道 std＋距離×角度 std 粗略篩選，限≤2 m，**不是嚴格誤差上界或融合後精度**。範圍前方 0–60 m、左右 20 m、上下 10 m。
- 最多 64 趟、每趟 100,000 筆 pose、位置在原點 100 km 內。缺位姿／有效觀測可以產生空成果，不應宣稱實際建圖成功。

### 4. 建圖與版本比對

```sh
python -m tools.carrot_mapping build \
  --observations trip-a.jsonl trip-b.jsonl --poses poses.json \
  --output lanes-v1.json --ply lanes-v1.ply

python -m tools.carrot_mapping build \
  --observations trip-a-new.jsonl trip-b-new.jsonl --poses poses-new.json \
  --previous lanes-v1.json --output lanes-v2.json --ply lanes-v2.ply
```

每版使用完整、明確選定的觀測集合重建；不是在舊點雲增量套新趟次。舊版只作比對。使用 1×1×0.5 m 格，每趟每格選一個誤差指標較小的候選，再取跨趟中位數；每案最多 25,000 格，並非連續車道拓樸或導引線。

重複影格不重計；同資料改 trip ID 的完全複製也拒絕。但 ID／位姿仍由提供者聲明，這不是車隊身分認證。相關模型誤差不會因平均自動消失。格界可能把車道分散到鄰格或產生假差異；高度分格不等於完整高架分層。未觀測可能只是路線、視野或篩選不同，不代表道路消失。

JSON 含 SHA-256 修訂、父版、篩除原因、來源／品質，固定 ground_truth:false、control_eligible:false、pose_verified:false。PLY 是格中心候選點雲，不含影像、建築網格或地理 CRS。輸出不覆寫，回退只需選舊成果，不修改行車設定。

### 5. 網頁／APK 檢視與人工審查

更新車機後，開「工具 → 車道建圖與多趟比對」：

1. 開合成範例、本機 JSON 或貼上 JSON，上限 8 MiB。Android 若無選檔功能，改貼文字或讀車機成果。本機檔不會上傳。
2. 共享成果由管理者手動放 `/data/carrot/mapping/<名稱>.json`，名稱限英數、底線、點、減號。不存在時列表為空，不自動收集紀錄。最多列出 32 案、檢視目錄前 256 筆；大型版本庫另管理。
3. 車機只提供 GET、限制大小、禁止連結路徑並校驗內容修訂，無上傳／修改／刪除 API。以新檔名發布已完成成果。**本機匯入只查格式／界限，未獨立驗證雜湊或來源。**
4. 切 BEV／3D、旋轉、縮放、拖曳，篩選趟次或至少兩趟支持。3D 是既有預測 XYZ，不是新的稠密深度表面。
5. 點格看座標、來源、車輛數、分散度與輸入指標，標記「可保留／排除／複查」及備註。
6. 下載審查 JSON 或選取文字複製。審查只存目前分頁，換圖先顯示捨棄確認；不改原成果，不升級為真值，不自動訓練。

CarrotAssist 0.2.19 載入更新後車機網頁即可使用，無新 APK 或權限；實體 Android 選檔／效能依系統 WebView。這是離線成果，既有 Carrot Vision 即時 BEV 為另一畫面。

成果沿用既有 Carrot Web 存取範圍，包括已授權遠端網頁。即使沒有經緯度，局部軌跡與假名也可能透露路線特徵，請只發布獲同意資料。本次未讀取／上傳使用者路線。

## 後續實測驗收

先取一小段獲同意的影片／IMU／rlog與校正，用獨立控制點確認尺度、左右正負、同步與漂移，再作跨趟閉環／配準。以未參與最佳化的測量資料報誤差分布／失敗率，分別評估白天、雨夜、無線道路、高架、隧道與遮蔽；測試差異假陽性／漏報、回退後，再投入稠密 3D／occupancy 或訓練。合成測試、整齊 BEV、RTK 規格或來源 std 都不能證明端到端精度。

## 原始資料核對

- [使用者提供文章](https://electrify.tw/tesla-ai-powered-labeling-patent/)連結的 [WO2024073115A1](https://patents.google.com/patent/WO2024073115A1/)主軸為 AI 推論編譯／執行鏈，亦提及 occupancy／標註資料；不能據此推定能取得 Tesla 權重／車隊資料或證明雨夜不受影響。
- [EfficientDet 原始論文](https://arxiv.org/abs/1911.09070)提出加權 BiFPN 多尺度特徵融合；不是完整 VIO／建圖流程，也不能單憑文章認定 Tesla 使用該架構。
- [VINS-Fusion 官方程式與校正範例](https://github.com/HKUST-Aerial-Robotics/VINS-Fusion)可作外部位姿流程評估；本工具只提供輸入契約，未移入其求解器、Tesla 專利實作或資料集。
