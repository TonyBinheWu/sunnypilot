# C3X／C4 模型選擇與感知畫面

## 選模型

停車後開啟裝置設定中的模型選擇器。「模型清單」可以切換全部、carrot-wip、sunnypilot 小模型或 sunnypilot 大模型。小模型使用內建 GPU，大模型使用相容的 USB eGPU。第一次選取 sunnypilot 模型需要網路和足夠的儲存空間。下載會驗證模型、兩種攝影機的校正影像轉換程式和執行環境。看到「下次開機」後，重新啟動裝置才會套用。

本版固定收錄 sunnypilot 官方清單中的 79 個小模型和 25 個大模型。部分名稱共用相同權重，裝置依 SHA-256 共用下載檔。原有 CD210、Michael RL V2、Rebel Legion 和 carrot-wip 的外接模型仍可選。兩類模型各自保留選擇，移除 eGPU 或推理失敗時，原有內建後備路徑會接手。

## 同時使用兩個模型

「重新開機後的 eGPU 用途」預設為「主駕駛模型」。選「輔助減速推理」並重新開機後，主模型在內建 GPU 執行，第二個駕駛模型在 eGPU 執行。可選 sunnypilot 大模型，或已安裝且支援獨立程序的 carrot-wip 預編譯大模型。兩者使用同一組主、廣角攝影機影格與校正轉換。狀態中的毫秒數是從相機影格結束到輔助模型產生結果的時間。

輔助結果須先累積 100 個連續且及時的影格。採用時須在 120 毫秒內，最多落後主模型一幀。車輛須在 D 檔以超過 4 m/s 行駛、縱向控制啟用，且駕駛沒有踩踏板或介入轉向。當主模型已規劃減速，兩個模型對前方路徑、速度與減速度亦相符時，輔助模型可將當次主模型的減速度最多增加 0.15 m/s²。方向、起步、停車判斷及 CAN 權限仍由原駕駛流程處理。持續逾時的 eGPU 會保留主模型的原始決策。

## 讀取 3D 畫面

在「駕駛畫面」切換原始鏡頭、原有 3D 或「模型感知 3D」。感知畫面中，駕駛模型提供路徑、標線、道路邊界及前車觀測。獨立的道路攝影機偵測器提供行人、自行車、機車、汽車、公車及卡車分類。

有地面定位、連續觀測和有效自車運動資料時，車體圖示和箭頭沿估計移動方向旋轉，可顯示同向、對向或橫向穿越。箭頭也可能指出倒車方向。靜止、方向不明或配對不確定的物件使用無方向圖示。僅有影像分類的物件列在「僅影像辨識」，畫面不會為它指定距離。

「可能的路口」標示兩側可見道路邊界同步變寬並再次收窄的位置。有已下載的區域圖資、可靠定位和車頭方向時，「路口圖資」會再畫出最近相連的道路分支。道路帶的寬度為示意值。資料來源標示為 OpenStreetMap，無法從這一層判斷通行權、紅綠燈狀態或橫向來車。高架與隧道不參與平面路口連接。這些顯示資料不送入駕駛控制。

## 驗證範圍與來源

已用 104 個實際發行檔的欄位定義和合成數值，通過本分支的解析及駕駛模型、相機姿態訊息序列化。另已完整下載 LAv2、Sharp Cheddar、ETCW Driving，核對 SHA-256，並為 C3X／C4 兩種相機格式讀取或組合模型與影像轉換程式。已用兩種裝置的原生繪圖配置渲染方向箭頭，也用實際下載的安道爾圖資讀取相連路口。上述驗證在桌機執行。車機推理耗時、連續運轉、交通辨識準確率與道路閉環行為仍待硬體驗證。

清單採用 sunnypilot-models 的固定版本。[小模型清單](https://github.com/sunnypilot/sunnypilot-models/blob/8f3dc68ceed4c328b2f0345eb19e82360a675196/docs/driving_models_v25.json) · [大模型清單](https://github.com/sunnypilot/sunnypilot-models/blob/8f3dc68ceed4c328b2f0345eb19e82360a675196/docs/driving_models_chestnut_v28.json)

模型讀取與執行介面依據 sunnypilot 的 modeld_v2 及該版配套的 tinygrad 子模組。This software is licensed under a custom license requiring permission for use. [上游原始碼](https://github.com/sunnypilot/sunnypilot/tree/abada6315d514715167377e3db1355abbc141ddf/openpilot/sunnypilot/modeld_v2) · [授權條款](../openpilot/sunnypilot/modeld_v2/LICENSE.md)
