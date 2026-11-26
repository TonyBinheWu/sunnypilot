# C3X／C4 模型選擇與感知畫面

## 選模型

在手機瀏覽器或 CarrotAssist 開啟「工具 → sunnypilot 駕駛模型選擇器」。Formosa 座艙從「應用程式 → 工具／診斷」進入同一頁。即使沒有連接 eGPU 也能瀏覽。兩個下拉清單分別列出小模型與大模型，各自按 carrot-wip 和 sunnypilot 分組。上方會顯示本次開機選用的模型。停車、關閉點火並等裝置進入停駛狀態後可變更設定。首次選擇請等到顯示「已儲存，下次開機套用」再重啟。車機提供這個頁面，更新並重新啟動車機後重新開啟 App 即可。

同一頁的「C3X／C4 本機駕駛畫面」可設定動態 3D、原始鏡頭或模型感知 3D，選擇「沿用裝置配置」即可恢復既有配置。這個選項控制 comma 自身的螢幕。手機上的座艙視覺仍由座艙介面設定。

停車後開啟裝置設定中的模型選擇器。「模型清單」可以切換全部、carrot-wip、sunnypilot 小模型或 sunnypilot 大模型。小模型使用內建 GPU，大模型使用相容的 USB eGPU。第一次選取 sunnypilot 模型需要網路和足夠的儲存空間。下載會驗證模型、兩種攝影機的校正影像轉換程式和執行環境。看到「下次開機」後，重新啟動裝置才會套用。

本版固定收錄 sunnypilot 官方清單中的 79 個小模型和 25 個大模型。部分名稱共用相同權重，裝置依 SHA-256 共用下載檔。原有 CD210、Michael RL V2、Rebel Legion 和 carrot-wip 的外接模型仍可選。兩類模型各自保留選擇，移除 eGPU 或推理失敗時，原有內建後備路徑會接手。

## 主駕駛模型

停車後可在 C3X 或 C4 的「重新開機後的主駕駛模型」選擇內建 GPU 小模型或優先使用 eGPU 大模型。兩組模型名稱會各自保留。舊版曾選「輔助減速推理」的裝置，升級後會繼續以原先的小模型為主。舊版第二個駕駛模型的減速度修正已移除。

## 讀取 3D 畫面

在「駕駛畫面」切換原始鏡頭、原有 3D 或「模型感知 3D」。感知畫面中，駕駛模型提供路徑、標線、道路邊界及前車觀測。獨立的道路攝影機偵測器提供行人、自行車、機車、汽車、公車及卡車分類。

有地面定位、連續觀測和有效自車運動資料時，車體圖示和箭頭沿估計移動方向旋轉，可顯示同向、對向或橫向穿越。箭頭也可能指出倒車方向。靜止、方向不明或配對不確定的物件使用無方向圖示。僅有影像分類的物件列在「僅影像辨識」，畫面不會為它指定距離。

「可能的路口」標示兩側可見道路邊界同步變寬並再次收窄的位置。有已下載的區域圖資、可靠定位和車頭方向時，「路口圖資」會再畫出最近相連的道路分支。道路帶的寬度為示意值。資料來源標示為 OpenStreetMap，無法從這一層判斷通行權、紅綠燈狀態或橫向來車。高架與隧道不參與平面路口連接。這些顯示資料不送入駕駛控制。

## 驗證範圍與來源

在 390 像素寬的桌面 Chrome 模擬手機視窗中，已從 Carrot Web 與 Formosa 座艙的「工具」開啟正式頁面。以隔離的車機狀態及實際權重快取，選取 Sharp Cheddar 小模型和 ETCW Driving 大模型。選擇器完成檔案驗證，將兩筆選擇分別寫入下次開機設定。另從網頁切換本機駕駛畫面，在座艙頁讀回相同設定。

已用 104 個實際發行檔的欄位定義和合成數值，通過本分支的解析及駕駛模型、相機姿態訊息序列化。另已完整下載 LAv2、Sharp Cheddar、ETCW Driving，核對 SHA-256，並為 C3X／C4 兩種相機格式讀取或組合模型與影像轉換程式。已用兩種裝置的原生繪圖配置渲染方向箭頭，也用實際下載的安道爾圖資讀取相連路口。上述驗證在桌機執行。車機推理耗時、連續運轉、交通辨識準確率與道路閉環行為仍待硬體驗證。

清單採用 sunnypilot-models 的固定版本。[小模型清單](https://github.com/sunnypilot/sunnypilot-models/blob/8f3dc68ceed4c328b2f0345eb19e82360a675196/docs/driving_models_v25.json) · [大模型清單](https://github.com/sunnypilot/sunnypilot-models/blob/8f3dc68ceed4c328b2f0345eb19e82360a675196/docs/driving_models_chestnut_v28.json)

模型讀取與執行介面依據 sunnypilot 的 modeld_v2 及該版配套的 tinygrad 子模組。This software is licensed under a custom license requiring permission for use. [上游原始碼](https://github.com/sunnypilot/sunnypilot/tree/abada6315d514715167377e3db1355abbc141ddf/openpilot/sunnypilot/modeld_v2) · [授權條款](../openpilot/sunnypilot/modeld_v2/LICENSE.md)
