# FormosaLink 道路環境研究

車主可以將前方道路的觀測資料收集到自己的 FormosaLink。車機依時間整理道路幾何，伺服器依定位找出附近的 OpenStreetMap 路段。網頁與 APK 共用車機提供的 Carrot Vision 介面。此資料集供回放、資料品質檢查和離線研究使用。

## 車主操作

1. 車機更新到包含此功能的 `carrot-wip` 並連上 FormosaLink。伺服器健康檢查的 `features` 應包含 `road-scenes-v1`。
2. 在 FormosaLink 開啟已配對裝置的「道路環境研究」，閱讀位置與行動網路使用說明，選「開始分享」。授權以車主與裝置為單位，預設關閉。車機約每 30 秒更新授權。
3. 車機取得新鮮模型影格後即開始記錄車道、道路邊緣與前方目標。要加入行人、機車、汽車、三角錐等分類時，讓網頁或座艙 APK 保持連線，在駕駛視覺開啟物件／道路辨識並保持前方道路畫面可見。瀏覽器必須能確認正在顯示的原始影格。單有分類框也可以收集，但只能在影像座標中解讀。
4. 在車機網頁或 APK 的鳥瞰畫面可看灰色 OSM 道路參考線。FormosaLink 的研究視窗每 5 秒刷新，可看最後接收時間、車道與道路邊緣數量、目標數和附近 OSM 路段數。切斷車機連線後請以最後接收時間判讀。選「下載道路場景」取得 NDJSON。
5. 「停止分享」會立即拒收新資料，仍可下載既有紀錄。「停止並清除資料」同時撤銷授權、刪除此裝置已存的研究場景。配對、診斷日誌及完整 rlog 的授權各自獨立。

## 圖上各項資料代表什麼

| 資料 | 實際來源與限制 |
| --- | --- |
| 車道線與道路邊緣 | 車機模型最多輸出四條車道線和兩側道路邊緣的 XYZ 點。保留模型給的機率或標準差，並捨棄不可靠的曲線。 |
| 雙黃線 | 支援的車型另有原廠攝影機標線訊息。收到有效且與影格相差不超過 200 毫秒的顏色與線型時，才加上原廠分類。例：代碼 24 表示黃色雙線、內側實線。畫面上的雙線間距為示意。其他車型可能僅有幾何線。 |
| 前方目標 | 車機提供的前方與相鄰車道目標記為未分類位置。座艙偵測器辨識出的物件另記類別、信心及估計的地面位置或影像框。兩路觀測可能重複看到同一目標，計數代表觀測筆數。 |
| 交通號誌與斑馬線 | 偵測器的框可供人工檢查。號誌燈色、遮擋後的路況及斑馬線各個角點仍未知。前方鏡頭的可見區域決定收集範圍。 |
| OSM 道路 | 伺服器本機查詢距定位點 125 公尺內的候選路段，最多 24 段。平行道路、匝道或高架上下層可能同時入選。車道線的顏色與線型來自車端觀測。 |
| 動態累積 | 同一次開機內最多累積最近 6 秒的靜態車道／邊緣作為背景，資料中斷即停止串接。移動目標保留各自的影格。 |

有水平精度及方向品質的 GNSS 資料才可產生地理投影。方向不足或車輛靜止時，仍可能有車身座標觀測。輸出的經緯度是水平近似，橋面高程、車道級絕對位置和被遮蔽區域需要額外量測。OSM 出處為 [OpenStreetMap 貢獻者，ODbL](https://www.openstreetmap.org/copyright)。

## 資料傳輸與保存

車機以配對金鑰簽署 HTTPS 批次，傳至配對的 FormosaLink。基本場景約每秒一筆，有對應分類的影格另可入列。每筆含開機識別、影格編號、感測器擷取時間、可用的定位與校正資訊。座艙推論與車端必須吻合影格及擷取時間。資料通道只收結構化觀測，不收原始影像、車牌文字、音訊或車內鏡頭。

伺服器保留最多 30 天，每台最多 200,000 筆。斷線時最多暫存在記憶體 90 筆，且僅在短效授權仍有效時重送。長時間離線可能產生缺段。研究資料庫位於 FormosaLink 私有狀態目錄的 `road-research.sqlite3`。下載只開放給該配對裝置的所有者。

## 離線 OSM 與佔用模型

IIS 後端可直接讀取部署套件隨附的台灣空間索引。自行更新時，下載區域 PBF，在安裝了 Python `osmium` 的工作站執行下列命令，把完成的索引放進後端私有資料目錄的 `scene-osm.sqlite3`。道路查詢在自己的伺服器完成。[台灣 OSM 下載來源](https://download.geofabrik.de/asia/taiwan.html)

```powershell
python -m formosalink.server.scene_osm taiwan.osm.pbf scene-osm.sqlite3
```

獨立的工作站工具以戶外公制深度模型估計可見表面，再以光達標記訓練小型佔用分類網路。輸入需為已去畸變的前鏡頭影像，與該影像相符的內參 JSON 含 `width`、`height`、`fx`、`fy`、`cx`、`cy` 及 `rectified: true`。建議在工作站的獨立 Python 環境安裝 NumPy、Pillow、PyTorch 與 Transformers 4.x。原始研究權重與授權見 [Depth Anything V2 戶外 Small](https://huggingface.co/depth-anything/Depth-Anything-V2-Metric-Outdoor-Small-hf)。

```powershell
python -m tools.carrot_mapping.kitti_reference train_sync.zip calib.zip train_frames --step 7
python -m tools.carrot_mapping.kitti_reference test_sync.zip calib.zip test_frames --step 12
$training = (Get-ChildItem train_frames -Filter '*.npz').FullName
$evaluation = (Get-ChildItem test_frames -Filter '*.npz').FullName
python -m tools.carrot_mapping.occupancy_head --train $training --test $evaluation --output occupancy-head.npz
python -m tools.carrot_mapping.depth_surface front.png camera.json surface.npz --occupancy-head occupancy-head.npz
```

用兩趟獨立的 KITTI 行程驗證。五張影格共 93,909 個可比對光達像素，各影格深度絕對誤差中位數為 0.67–0.96 公尺。佔用分類以行程 0001 的 16 張影格訓練、行程 0002 的 7 張評估。在 160,281 個有參考量測的候選位置，IoU 為 22.3%、精確率為 40.1%、召回率為 33.4%。成績只適用於這組可見候選位置。20 公分是格子尺寸；目前缺少台灣道路、夜間與雨天的獨立精度驗證。[KITTI 同步攝影機與光達資料](https://www.cvlibs.net/datasets/kitti/raw_data.php)

車載即時收集與工作站佔用推論是兩條獨立流程。僅靠上傳的稀疏線條和物件框，無法重建所有未分類障礙物的密集表面。若要訓練台灣道路的高精度佔用網路，仍需經同意且時間同步的已校正道路影像、獨立光達或其他可靠深度量測，以及涵蓋不同道路和天候的保留測試行程。
