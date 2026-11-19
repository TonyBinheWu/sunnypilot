# carrotpilot ｜繁體中文

以 openpilot 為基礎的駕駛輔助軟體，搭配 Carrot Web 與 Android CarrotAssist 使用。

| 倉庫／來源 | 位置 |
|---|---|
| 本分支 | [TonyBinheWu/sunnypilot · carrot-wip](https://github.com/TonyBinheWu/sunnypilot/tree/carrot-wip) |
| 上游來源 | [ajouatom/openpilot · carrot-wip](https://github.com/ajouatom/openpilot/tree/carrot-wip) |
| 工作分支 | `carrot-wip` 與本倉庫的 `hkg-enhanced` 分開維護 |

[下載與安裝](#下載與安裝) · [中文語音](#繁體中文語音指令) · [介面語言](#繁體中文介面) · [手機功能](#手機操作功能) · [車機安裝](#安裝與發行策略) · [Jetson](#jetson-連接與安裝) · [車輛支援](#車輛支援範圍) · [法律聲明](#法律聲明)

## 上游合併（2026-11-14）

已合併上游 `carrot-wip` 至 [`f89f40a3`](https://github.com/ajouatom/openpilot/commit/f89f40a37965b8a75f6a313e879cee02d8cff610)，保留本分支的繁體中文、CarrotAssist、FormosaLink、導航最愛、語音音量及停車 Vision 等功能。合併前版本保存在 [`carrot-wip-backup-2026-11-14`](https://github.com/TonyBinheWu/sunnypilot/tree/carrot-wip-backup-2026-11-14)。

- 更新 B1 第 5 版回訊處理與方向燈判斷，保留原有車型適用條件與保護。
- 新增「Tesla 自動滾輪調速」及繁中詳細指南，預設關閉；符合硬體及縱向控制條件後，須明確開啟並完整重新啟動。
- 整合 Jetson MAXN_SUPER 設定、首次開機韌體準備及 SD 映像檢查流程；僅在符合條件的 Jetson 上執行。

原有設定的預設值不變；現有 CarrotAssist 0.2.17 可繼續使用。軟體測試不代表已完成實車、韌體升級或道路驗證。

<p align="center">
  <img src="https://github.com/user-attachments/assets/4d80d256-7e66-4473-a289-04a50733b7e0" alt="carrotpilot" width="640">
</p>

## 道路辨識（網頁／APK）

駕駛視覺可顯示有足夠影像證據的燈色與方向箭頭，座艙「視覺與物件辨識 → 模擬路口」可分方向查看模擬號誌。同批 232 張影像正確辨識由 135 張提升至 204 張。[測試結果與未確認原因](docs/TRAFFIC_SIGNAL_VALIDATION.zh-TW.md)

修正 C4 標準前鏡頭串流比例造成的「3D 定位資料不足／影像規格不符」，並分開提示辨識運算過慢、校正缺失與資料過期。定位不足時保留真實影像分類，不虛構物件距離。既有 APK 可沿用，須停車更新並重啟車機的原生編碼器。[修正原因與繁中檢查方式](tools/carrot_android/OBJECT_DISPLAY_RECOVERY.zh-TW.md)。此修正不代表 N16 導航偏移已通過實車驗證。

導航模型底圖失效時，現在立即撤銷底圖與路線有效標記，並拒收舊版的全黑失效影像。另修正單觸方向燈熄滅後，反向施力可能無法取消進行中變道的缺陷。[修正與驗證範圍](docs/NAVIGATION_MAP_VALIDITY.zh-TW.md)。CAN 錯誤退出與個別導航偏移仍須依當次紀錄分別判斷。

車機與網頁／APK 駕駛視覺新增變道預告、進度及完成狀態。觀察跨線並在目標車道穩定置中後，結束此次模型變道意圖；資料不足則標示「完成未確認」。預告不代打方向燈或啟動轉向。[繁中詳細說明與確認條件](docs/LANE_CHANGE_NOTICES.zh-TW.md)。

座艙依提供的示意圖改為[Formosa 分區與字體排版](tools/carrot_android/FORMOSA_REFERENCE_LAYOUT.zh-TW.md)，駕駛視覺下方已移除重複的聲音卡片。觀看地圖採 [OSM、搜尋／模型維持 Mapbox](docs/NAVIGATION_MAPBOX_OSM.zh-TW.md)；新錄製的攝影機 H.264／HEVC 影片加入[同步車況 SEI](tools/carrot_android/DRIVING_SEI.zh-TW.md)，既有 0.6.0 APK 可沿用。

網頁與 APK 的行車記錄回放可直接顯示 SEI 車況，跟隨影片時間同步；播放控制列閒置時自動收起，輕觸即可叫出。啟用 [`HotspotOnBoot`（SIM 行動網路分享）](docs/HOTSPOT_ON_BOOT.zh-TW.md)後，SIM 數據連線就緒時自動啟動既有熱點，供已連線裝置上網。

Formosa 座艙已補強手機精簡版面，並完成[停車實車連線、100%／200% 大字、旋轉與全螢幕操作實測](tools/carrot_android/LIVE_DEVICE_ACCEPTANCE.zh-TW.md)。現有 0.6.0 APK 可沿用；更新車機後重新開啟 App 即可取得介面修正。

新增預設關閉的「三角錐與斑馬線辨識」，保留原有人車／動物辨識與繁中功能。三角錐可作近似地面定位；斑馬線為影像提示。**停止線與機車停等區仍缺可部署且授權明確的權重，尚未完成辨識**。需更新車機網頁；[開啟方式、模型來源、效能及後續條件](tools/carrot_road_models/README.md)。僅顯示，不介入駕駛控制。

## 下載與安裝

新版駕駛視覺以後上方視角顯示本車、藍色路徑箭紋與灰色路側。網頁與 Formosa 座艙共用車機上的新版畫面。[車色、日夜模式與路徑配色](tools/carrot_android/VEHICLE_DISPLAY.zh-TW.md#車款與顏色)

駕駛視覺會逐組顯示前鏡頭辨識到的紅、黃、綠燈與方向箭頭，同一燈頭可以顯示多個燈號。[路口號誌與箭頭燈](tools/carrot_android/VEHICLE_DISPLAY.zh-TW.md#路口號誌與箭頭燈)

路口車流可連續追蹤，轉動視角時仍會更新。通用 GLB 模型會依距離及顯示效能切換細節。[動態物件與車型判定](tools/carrot_android/VEHICLE_DISPLAY.zh-TW.md#路口的動態物件)

**[⬇ 下載 CarrotAssist 繁體中文版 0.2.20（Android APK）](https://github.com/TonyBinheWu/sunnypilot/releases/download/carrot-assist-tw-v0.2.20/CarrotAssist-TW-0.2.20.apk)**

**[下載 Formosa 座艙 繁中 0.6.3（獨立 APK）](https://github.com/TonyBinheWu/sunnypilot/releases/download/carrot-cockpit-tw-v0.6.3/CarrotCockpit-TW-0.6.3.apk)**：座艙版更名並採獨立藍色圖示；滿版 3D 道路、分類物件立體模型、浮動儀表與固定底列，控制頁採分區操作。修正 4:3 與大字版面、左右座標及橫縱向獨立狀態，顯示台灣日期與即時秒數；本版移除語音／麥克風權限，原 CarrotAssist 保留。既有繁中搜尋、詳細指南、設定確認與回讀、導航最愛、依車速縮放、拖曳視角、車型外觀、燈號及連線恢復延續。[操作說明](tools/carrot_android/COCKPIT.md)／[Android 實測與限制](tools/carrot_android/FORMOSA_COCKPIT_0.6.0_ACCEPTANCE.zh-TW.md)。先更新並重啟 carrot-wip 車機，再覆蓋安裝 APK；可與原版並存。 已補強[安卓手機直向／橫向主畫面](tools/carrot_android/PHONE_DISPLAY.zh-TW.md)：小尺寸、大字、導航鍵盤與設定操作；現有 0.6.0 APK 可沿用。已在 Samsung Android 手機以模擬 1920×720／4:3 驗證，尚未完成實體車用盒子或實車驗收。 另完成[介面與操作缺失修正](tools/carrot_android/INTERFACE_AUDIT.zh-TW.md)：大字頂列、車況卡片、彈窗與返回、載入重試及導航狀態同步；0.6.0 APK 可沿用。

座艙 0.6.3 在已啟用影像辨識時會自動連接可用前鏡頭。3D 模型依持續追蹤編號移動，淡色模型表示短暫預測。「應用 → 鏡頭與物件辨識 → 即時追蹤診斷」可查看各來源幀率、延遲與物件狀態。[追蹤指南](tools/carrot_android/COCKPIT.md#063-即時-3d-追蹤)

座艙 0.6.2 的寬螢幕會依導航狀態展開地圖，未導航時給駕駛視覺完整寬度。在「應用」開啟子選單，關閉後可繼續從原位置操作。首次連線輸錯 IP 可以直接修正。[操作驗證與螢幕尺寸](tools/carrot_android/INTERFACE_AUDIT.zh-TW.md)

0.2.20／0.6.1 已同步發布至 GitHub，App 內更新來源也已更新。搭配更新後的車機提供回放控制列自動收合、同步 SEI 與返回清理；新座艙 APK 已完成覆蓋安裝及實車舊影片回放檢查。[發行、簽章與下載驗證](tools/carrot_android/APK_RELEASE_20261118.zh-TW.md)。既有 0.6.0 仍可載入新版車機介面；安裝新 APK 也必須先更新車機。

| 項目 | 說明 |
|---|---|
| 版本 | **0.2.20**（版本代碼 27） |
| 安裝需求 | Android 8.0 以上 |
| 手機直接語音 | Android 12 以上、可用的裝置端語音辨識服務與國語語音模型 |
| 套件名稱 | `me.shind0.carrotweb.tw`，手機顯示為 **CarrotAssist 繁中** |
| 發行與驗證 | [發行頁面](https://github.com/TonyBinheWu/sunnypilot/releases/tag/carrot-assist-tw-v0.2.20) · [SHA-256 校驗檔](https://github.com/TonyBinheWu/sunnypilot/releases/download/carrot-assist-tw-v0.2.20/SHA256SUMS.txt) |
| 更新來源 | 本倉庫 `TonyBinheWu/sunnypilot` 的繁中發行頻道 |

### 安裝步驟

1. 使用 Android 手機下載上方 APK，完成後點選檔案。
2. 若 Android 要求，允許目前的瀏覽器或檔案管理員「安裝未知應用程式」，再返回安裝。
3. 開啟 **CarrotAssist 繁中**。手機系統語言設為繁體中文時，原生介面會顯示繁體中文。
4. 手機與 comma 連到相同 Wi-Fi／熱點，搜尋裝置或手動輸入 IP。
5. 更新車機至本倉庫的 `carrot-wip`，停車後完整重新啟動，再於網頁「工具 → 語言 → 繁體中文」選擇網頁語言。

**從既有繁中版更新：** 使用相同套件與簽章，可直接覆蓋安裝並保留 App 設定，不需先解除安裝。中文語音與新版 Vision 顯示需要 App 與車機程式一起更新。

**與上游原版並存：** 繁中版使用獨立套件及專用簽章，可與原版 CarrotAssist 並存，原版資料會保留。新 App 的設定與 ChatGPT 授權獨立，可能需要重新連線。

APK 經建置、測試與簽章驗證；尚未在實體手機或實車驗證。iPhone 請使用 [Carrot Web](docs/CARROT_MOBILE.zh-TW.md)。

**選錯初始設定時：** 更新車機後，網頁與 APK 可由「工具 → 重新執行設定引導」重選語言、車型、HDA 與控制方式。選項先暫存，最後確認才套用；取消會保留原值，也可逐項選擇保留目前設定。須停車關閉控制或熄火操作；變更車輛配置後依提示完整重啟。[繁中操作說明](docs/CARROT_MOBILE.zh-TW.md#重新執行設定引導)。

## 錯誤自我診斷與修復

網頁與 APK 的「工具 → 錯誤自我診斷與修復」可檢查 CAN、處理延遲、程序、溫度、儲存空間、模型與 FormosaLink。網頁請求／影像連線失敗時會限頻自動做唯讀檢查；需要修復時，先確認操作內容，且由車機重新確認停車狀態。資料不足會明確顯示，CAN、轉向、煞車與校正參數不會自動更改。

**0.2.19 APK** 另提供「上方裝置名稱 → 連線自我診斷與修復」，即使車機網頁打不開，也能檢查區域網路、驗證選取的 Carrot Web、重新搜尋、輸入 IP，以及開啟 Wi-Fi／中文語音檢查。更新並重啟車機後再使用完整診斷。[繁中操作與修復範圍](docs/CARROT_MOBILE.zh-TW.md#錯誤自我診斷與修復0219)。

## Carrot Vision 顯示版面

**0.2.18：字體大小與 Vision 畫質。** 工具 → 網頁設定可調整網頁／APK 內容字體 80–200%、道路串流 360p／540p／720p 與獨立繪製清晰度。App 裝置名稱選單另提供原生介面字體大小；串流解析度須結束所有觀看後重新連線套用。[繁中設定指南](docs/CARROT_MOBILE.zh-TW.md#字體大小與-vision-畫質0218)。

**0.2.17：APK 即時 Vision 自動全螢幕。** 與車機一併更新後，隱藏上方 CarrotPilot／裝置 IP 列、浮動語音鈕與 Android 系統列，以 Live View 完整影像比例顯示；畫面內退出鍵或 Android 返回鍵可恢復。側邊新增可收合的「當前事件」，逐項顯示目前有資料的控制、方向燈、盲區及警示，資料過期即移除。支援橫向 Android 盒子的大螢幕版面，當次視野切換不覆寫原有偏好。[繁中使用方式與實機驗證限制](docs/CARROT_MOBILE.zh-TW.md#carrot-visionapp-全螢幕與當前事件0217)。

0.2.16 參考提供的 CommaView APK 結構，新增可收合工具列、車速面板顯示切換、視野切換與獨立影像狀態／統計；長按 App 上方 **▣** 可收合工具列。影像正常以實際呈現的新影格判定，與 HUD 資料狀態分開。

新增參考 CommaView 配置的 **Live View 道路影像**：底部車速／定速／速限、側邊工具列、繁中詳細資訊，以及手機直向配置。原有儀表仍可切回。更新車機與新版 App 後，開啟 Carrot Vision，按 App 上方 **▣**，或由 **工具 → 網頁設定 → Carrot Vision → Vision 顯示版面** 選擇。這是顯示版面，影像及車道／路徑沿用既有資料，不改變駕駛控制。[操作方式與限制](docs/CARROT_MOBILE.zh-TW.md#carrot-visionlive-view-道路影像版面0216)。

停車時也可觀看：更新車機並重新啟動一次，開啟「啟用 Carrot Vision」後進入 Vision。有觀看會話才啟動鏡頭與專用串流編碼器，結束後釋放；不需要診斷模式，也不啟動駕駛模型或行車控制。現有 0.2.16 APK 可使用。[停車觀看說明](docs/CARROT_MOBILE.zh-TW.md#停車時觀看-carrot-vision)。

## 導航地圖與我的最愛

APK 與網頁的「導航地圖／Navigation」支援命名最愛、地址新增／編輯／刪除及點一下名稱導航。最愛儲存在車機，重新啟動與一般更新後保留；「清除 Mapbox 目的地」已改為 **結束當前導航**。更新車機並重新開啟導航頁即可使用，既有 0.2.16 APK 可沿用。[繁中操作指南與 Mapbox 地址儲存條件](docs/CARROT_MOBILE.zh-TW.md#導航地圖與目的地)。

導航統一採用 **Mapbox 搜尋／路徑＋車機 Mapbox／OpenStreetMap·Protomaps 地圖**，與導航模型共用既有 mapsd 預覽；Google 圖層、Places 搜尋及金鑰入口已移除。舊 Google 最愛保留名稱，可明確重新搜尋並選定地址。[繁中設定與舊最愛轉換指南](docs/NAVIGATION_MAPBOX_OSM.zh-TW.md)。

### 預先下載台灣離線地圖

1. 車機連上網際網路後，在網頁或座艙 APK 開啟「導航」，展開「地圖與搜尋來源」，按「下載台灣離線地圖」。座艙版先點「搜尋目的地／最愛」即可看到這個選單。
2. 下載完成後，畫面會顯示圖資大小與安裝日期。台灣全區圖資約 175 MiB，車機會另外預留 512 MiB 可用空間。日後可在同一處按「更新台灣離線地圖」。
3. 行動網路中斷時，讓手機或車用盒子保持連到車機的區域網路，即可平移、縮放台灣地圖，並查看車機仍提供的目前位置及既有路線。地址搜尋與新路線規劃仍需連網使用 Mapbox。

圖資儲存在車機，網頁與 APK 共用。更新中斷時會保留已安裝的版本。台灣向量底圖由 Geofabrik 提供，地圖資料來自 OpenStreetMap 貢獻者。[台灣圖資](https://download.geofabrik.de/asia/taiwan.html) · [地圖授權](https://www.openstreetmap.org/copyright)

## 繁體中文語音指令

0.2.13 新增國語直接語音，不需 ChatGPT 帳號或配對碼。手機為繁體中文語系時會要求 `zh-TW` 辨識，需有可用的裝置端國語語音模型；語音辨識能力依手機與辨識服務而定。

### 中文語音模型檢查與安裝（0.2.14）

點 App 上方的**裝置名稱 → 中文語音檢查與安裝**，不需先連接車機。缺少麥克風權限、語音模型或裝置端辨識服務時，也會自動顯示繁體中文引導。

| 顯示狀態 | 下一步 |
|---|---|
| 麥克風未允許 | 按「授予麥克風權限」；若曾拒絕或系統不再詢問，按「開啟 App 權限設定」，將麥克風設為使用期間允許 |
| 權限允許但不能收音 | 檢查快速設定／隱私設定的「麥克風存取」總開關，以及語音服務本身的權限 |
| 模型可下載、尚未安裝 | Android 13 以上可按「下載中文語音模型」；系統可能另外要求確認下載 |
| 等待下載／下載中 | 保持網路連線，等待服務處理後按「重新檢查」；Android 14 以上且服務支援時會顯示進度 |
| zh-TW 模型已安裝 | 關閉引導，再手動點麥克風試用；此狀態不等於已完成實際辨識測試 |
| 無法確認／服務未提供 zh-TW | 按「開啟語音輸入設定」，尋找「中文（台灣）／國語／zh-TW」的離線語音模型；選單依手機及服務不同 |
| 沒有裝置端辨識服務 | 在系統啟用語音辨識服務，或由手機官方商店更新；服務仍未提供國語模型時，App 無法強制安裝 |

Android 12 沒有模型清單查詢與下載 API，會顯示手動設定步驟；Android 13 的下載請求不會回報進度，所以「已送出下載請求」不會顯示成「安裝完成」。模型下載、權限授予及回到 App 都不會自動聆聽或執行先前指令。

已有 0.2.13 對應車機程式時，模型檢查只需更新 App；首次使用中文語音仍須更新本倉庫車機 `carrot-wip`。技術依據：[Android 模型查詢與下載 API](https://developer.android.com/reference/android/speech/SpeechRecognizer#triggerModelDownload(android.content.Intent))。

### 開始使用

1. 在 App 上方裝置名稱的選項中啟用「優先在此手機聆聽指令」，並授予麥克風權限。
2. 修改設定前，在 Carrot Web「工具 → ChatGPT 助手」允許讀取與修改設定值。
3. 變換車道或調整巡航前，另行允許語音變換車道與設定車速。首次授權須停車並退出駕駛輔助。
4. 保持 Carrot Web 顯示於前景，點麥克風說出指令。

| 操作 | 語音範例 | 行為 |
|---|---|---|
| 搜尋設定 | 「搜尋加速度設定」、「搜尋螢幕亮度」 | 開啟並顯示符合的設定 |
| 修改設定 | 「把螢幕亮度設為八十」 | 驗證設定名稱、範圍及權限後修改，並回讀結果 |
| 修改搜尋結果 | 「把第一個設為二百四十」 | 操作目前畫面上的第 1 個結果，回覆實際設定名稱 |
| 變換車道 | 「向左變換車道」、「請往右換一個車道」 | 請求變換一個車道，保留既有車輛條件檢查 |
| 指定巡航速度 | 「巡航速度設為一百公里」、「把定速速度調到100」 | 設定巡航目標，單位為 km/h |
| 降低巡航速度 | 「巡航速度降低十公里」、「定速減速」 | 前者減少 10 km/h；未指定數字時沿用減少 10 km/h |
| 提高巡航速度 | 「巡航加速」 | 相當於既有 RES/+ 一次；若要指定增幅，請改說絕對目標速度 |
| 停止聆聽 | 「停止聆聽」 | 結束本次手機聆聽 |

### 辨識與執行條件

- 支援阿拉伯數字、全形數字、國語數字與逐字讀數。`一百二` 有歧義，請說 `一百二十` 或 `一百零二`。
- 設定修改限裝置允許的整數值，仍受範圍、生效時機、受限設定及權限檢查約束；模糊名稱不會被猜成某個參數。
- 缺少巡航指令的可信度分數時，App 會要求覆誦同動作、同數值的「確認…」句子，例如「確認巡航速度設為100公里」。提示播完後六秒內有效，不能只說「是」。
- 否定句、問句、複合駕駛指令、候選衝突、過期或不相符的確認不會送出駕駛請求；離開畫面或其他指令會使待確認狀態失效。
- 車道變換仍受輔助狀態、車速、車道、盲點、轉向扭矩及駕駛優先權限制。車速操作要求已啟用且受支援的 openpilot 縱向控制，不會自行啟用輔助。
- 巡航回覆是**設定速度**，不是實際車速；「已收到請求」與「已套用」分開回覆。不確定結果不會自動重試執行。
- 語音有辨識與處理延遲，不能當作緊急控制介面。既有韓文、英文的設定與車道指令保留；新增巡航句型列於上表。

詳細限制見 [繁體中文手機操作指南](docs/CARROT_MOBILE.zh-TW.md)；語音服務需求見 [Android 官方文件](https://developer.android.com/reference/android/speech/SpeechRecognizer)。

## 繁體中文介面

**BEV（鳥瞰）標註：** 新增等比例距離格線、30／50／75 公尺視距、車道機率／邊界不確定度與前車數值標註。停車或回放時可凍結快照、人工補點／修正線條，匯出含來源的 JSON 與 BEV PNG。所有標註保留待驗證狀態，不自動訓練或改動控制。[繁中操作、座標與資料限制](docs/CARROT_MOBILE.zh-TW.md#bev鳥瞰標註與匯出)。

**即時環境視覺：** 網頁／CarrotAssist 支援行駛中的 BEV 與特斯拉風格淺色立體畫面，顯示來源提供的前車及左右車道目標；可另開前方影像辨識，在觀看端辨識汽車、機車、行人等類別，位置為校正後的地面估算，沒有側後方完整涵蓋。C3X／C4 原生行車畫面另提供 `RainbowMode`「彩虹道路（SP 風格）」開關，免重新啟動，僅改變顯示。[辨識條件、操作與限制](docs/CARROT_MOBILE.zh-TW.md#行駛中的即時鳥瞰與特斯拉風格畫面)。

**車道建圖研究工具：** 網頁／APK「工具 → 車道建圖與多趟比對」支援離線 3D／BEV 候選圖、趟次篩選、來源／分散度、版本差異與人工審查。工作站可擷取指定 rlog 模型車道，配合外部最佳化位姿產生多車／多趟 JSON／PLY。需先完成時間同步、校正與跨趟配準；未新增 VIO 求解器、車隊自動上傳、雨夜訓練或經驗證的高精度地圖，不改動行車控制。[繁中操作、格式及配套清單](docs/carrot_mapping_zh-TW.md)。

**Carrot View 顯示與錄影：** 新增可選的特斯拉風格模型俯視畫面、可個別拖曳／縮放的當前時速／道路限速／巡航設定速度，以及彩虹行駛路徑。網頁與既有 APK 共用；編輯限停車或回放。另提供預設關閉的錄影循環配額，routes 與車機畫面錄影共用儲存容量百分比，超額依序清理可刪舊紀錄。[繁中操作與清理範圍](docs/CARROT_MOBILE.zh-TW.md#俯視視覺速度資訊配置與彩虹路徑)。

**轉向學習進度：** 網頁／CarrotAssist「工具 → 轉向學習進度」、車機「設定 → 設備（裝置）→ 轉向學習進度」可查看延遲與扭力的資料進度、驗證狀態與數值，並區分即時／過期／保存紀錄。僅供查看，不會重設或修改調校。既有 0.2.18 APK 重新開啟更新後的車機網頁即可。[繁中說明](docs/CARROT_MOBILE.zh-TW.md#轉向延遲與扭力學習進度)。

**強制非行車模式（限 P 檔）：** 裝置「設定 → 裝置」及 Carrot Web「工具 → 使用者／系統」皆可操作。啟閉都需有效的即時 P 檔、靜止且已退出轉向／巡航輔助；行駛或資料不明時鎖定。離開 P 檔、車況失效或熄火時自動取消，重新啟動後恢復關閉。此模式會停止一般行車程序與錄影。[繁中詳細指南](docs/FORCED_OFFROAD.zh-TW.md)。

| 介面 | 支援內容與選擇方式 |
|---|---|
| 裝置主介面 | 既有「中文（繁體）」（`zh-CHT`），涵蓋 C3X／C4 設定、教學、網路、更新、行車提示與啟動復原畫面；在裝置設定選擇，依提示重新啟動 |
| Carrot Web | 獨立「繁體中文」（`zh-tw`），涵蓋選單、對話框、操作狀態、首次引導、設定名稱、摘要、分類、選項及 212 項本地詳細說明；選「工具 → 語言 → 繁體中文」 |
| Android CarrotAssist | 原生繁中介面，依手機繁體語系顯示；APK 從本頁下載 |
| 自動偵測 | 辨識 `zh-TW`、`zh-Hant`、`zh-HK`、`zh-MO` 及裝置繁中設定；已儲存語言優先，舊使用者請手動切換一次 |
| 外部內容 | 外連的上游 Wiki 與第三方服務依其提供語言顯示；車機提示音檔不因介面翻譯而新增繁中版本 |

## 手機操作功能

手機與 comma 連至相同 Wi-Fi／熱點，掃描裝置白色胡蘿蔔圖示的 QR Code，或開啟 `http://裝置IP:7000`。

| 類別 | 可操作內容 |
|---|---|
| 駕駛畫面 | 即時道路影像、HUD、導航、AR、畫面分割、螢幕錄影 |
| 設定 | 搜尋與調整設定、收藏、設定檔、變更歷程、設定說明 |
| 記錄 | 行程影片與資料回放、行程報告、記錄下載／上傳、錄影播放 |
| 工具 | 車型與語言、裝置資訊、Git 更新／切換分支、備份還原、校正與重新啟動 |
| 維護 | 終端機、診斷記錄、遠端支援、eGPU／Jetson 與外部模型狀態 |
| Android CarrotAssist | 尋找裝置、手機直接語音、另行授權的 ChatGPT 設定與駕駛指令 |

完整操作項目與限制見 [手機操作指南](docs/CARROT_MOBILE.zh-TW.md)。網頁「工具 → 繁體中文完整操作說明」可直接開啟完整功能指南。

C3X／C4 共用的文字排版已加入快取，滑動只改變位置時不再重複量測與解析文字；換行快取上限為 1024 筆。已通過桌面測試，實機流暢度仍需更新車機後驗證。

網頁、設定及維護操作請先安全停車；語音操作保留既有權限、車輛條件與駕駛優先權限制。

## FormosaLink 雲端操作與 LIVE

已配對車主可以在「道路環境研究」分享前方車道、道路邊緣、物件與定位，查看台灣 OSM 道路疊圖，並下載自己的場景。支援的車型可記錄原廠雙黃線分類。[繁中操作指南與佔用模型實測](docs/ROAD_SCENE_RESEARCH.zh-TW.md)

Carrot Web 與 FORMOSA 座艙可在駕駛視覺開啟「3D 環境佔用（研究）」。前鏡頭模型將可見表面畫成公尺尺度的方格，估距較不確定的區域則以範圍線表示。初次使用需由車機下載約 36 MB 的模型。[開啟方式、畫面圖例與光達對照結果](docs/FRONT_OCCUPANCY.zh-TW.md)

本分支支援 [FormosaLink](https://formosapilot.dinglu-t.com)：配對裝置後，可選「遠端 Carrot 網頁」進入原生網頁操作設定，或選「雙鏡頭 LIVE」觀看前廣角／車內鏡頭。

C3X 在「裝置 → FormosaLink」、C4 在「設定 → FormosaLink」掃描 QR 配對。完整網頁需在車機另開「遠端 Carrot 網頁」權限，且保持停車熄火與網路連線；開始行車或停用授權會中斷通道。LIVE 沿用所有者短效觀看租約，目標 8 fps、最大 640×360，不含音訊。

車機與 IIS 後端都須更新。操作、限制、IIS 更新指令及實機待驗項目見 [FormosaLink 整合說明](formosalink/docs/CARROT_REMOTE.md)。原生 Carrot WebRTC 仍受 NAT／ICE 限制，雲端鏡頭監看請使用 FormosaLink LIVE。

## 專案簡介

carrotpilot 是一個基於 [openpilot](https://github.com/commaai/openpilot) 的獨立駕駛輔助軟體專案，主要面向 Hyundai（現代）·Kia（起亞）·Genesis 車輛的相容性、縱向控制品質和真實駕駛體驗進行開發與改進。

carrotpilot 不是由 comma.ai 開發、審查、批准或正式支援的 openpilot 發行版。它包含與上游 openpilot 不同的車輛控制、安全策略和 Driver Monitoring 邏輯，因此不能假設這兩個專案在行為和支援要求上完全相同。

## 安裝與發行策略

**C3／C3X／C4 通用安裝入口（自動依裝置與 AGNOS 版本選擇）：**

```text
https://is.gd/tonyc4
```

三種機型都在「自訂軟體安裝網址」輸入同一網址，無須手動選擇機型。短網址雖保留原名 `tonyc4`，已供 C3、C3X、C4 通用。此公開入口固定安裝本倉庫 `TonyBinheWu/sunnypilot` 的 `carrot-wip`；不是安裝上游。完整入口為 [CarrotPilot 繁中分支安裝](https://carrot-tw-install.tony-binhe-wu.chatgpt.site)。

`https://is.gd/tonyc4check` 是**只讀版本檢查**，回傳 HTTP 409 與 `AGNOS: 版本` 文字，不提供安裝檔。受影響 C4 已回報僅顯示 `download failed`，因此不要反覆嘗試檢查入口，直接使用上方正式安裝網址。這個檢查結果不能判定正式安裝成功或失敗；若介面能顯示版本文字，再記下供診斷。

**停止使用 `is.gd/carrotc4`、`is.gd/carrotc4v2` 與 v1/v2 發行檔。** 實機回報這兩版和 `TonyBinheWu/carrot-wip` 官方簡寫仍在 Installing 出現前回 Start，尚無該台 C4 的日誌可確認根因。上游入口會依 Setup 回報的 AGNOS 版本提供不同檔案，不能只按「C4」選一個固定安裝器。新入口保留上游版本選擇與分支處理，核對固定來源的 SHA-256，只修改倉庫／分支預留欄位；不會重新包裝顯示程式。

`19.8-carrot-bt1` 已依實際車機請求核對並加入固定樣板，修正先前雜湊未收錄導致的 HTTP 409／`download failed`。C4 的 `19.6.3-carrot` 使用上游針對該系統驗證過的原生相容樣板。舊版樣板另改用同長度的獨立快取識別字，避開沿用工廠倉庫來源；不搬移或改寫工廠快取檔案。已確認的版本才有離線樣板備援，未知來源雜湊會停止並顯示診斷，不能把新樣板未經檢查直接送給車機。服務程式不轉送車機序號；主機平台可能保留請求標頭紀錄，不接受任意倉庫或上傳。

服務依安裝畫面回報的裝置代碼與 AGNOS 版本選擇樣板；不同機型的快取與備援分開。舊式 C3／C3X 若僅回報 `AGNOSSetup`，會使用已核對的原有 C3 安裝器；缺少裝置代碼時停止，避免猜錯機型。下載與雜湊驗證已涵蓋三種裝置，C3／C3X 尚待實機新安裝驗收。

CI 會核對五種實際 ARM64 樣板、18 組裝置／版本來源回應與 34 項測試、允許修改的資料範圍、版本選擇、快取策略及診斷路徑；另檢查 comma 官方檔案的動態函式庫、DRM 顯示通道與目標設定並保存報告。這些檢查不執行下載檔，也不代表已完成實機驗收。先前 v1/v2 留下的 `/data/carrot-installer-error.txt`、`/data/carrot-installer.log` 可供診斷；新入口不使用這兩個包裝程式日誌。維護與驗證方式見 [通用安裝入口說明](tools/carrot_installer/GATEWAY.md)。

**C3／C3X 原有安裝入口（保留備用，平常使用上方通用短網址）：**

```text
install.sunnypilot.ai/fork/TonyBinheWu/carrot-wip
```

此安裝服務會取得 `TonyBinheWu/sunnypilot` 的 `carrot-wip`。首次啟動可能先更新 AGNOS，再安裝本地依賴與編譯；請維持供電與網路。已修正乾淨安裝時，AGNOS 更新畫面載入失敗而停在啟動畫面的問題。若更新失敗，會進入獨立的啟動復原畫面，並提供 `6999` 連接埠的復原入口；AGNOS 更新日誌為 `/data/agnos-updater-ui.log`。

C4 冷啟動另修正了尚無字型圖集時，載入過大的完整 CJK 字集問題：改用包含目前繁中介面與語言選單的實際字元，實測來源字型圖集由 16384×16384 降至 8192×8192。依賴準備及設定登錄編譯會顯示目前階段；啟動鎖逾時與模型選擇初始化失敗也會轉入復原畫面，不再停在無提示的等待迴圈。這些修正已做冷啟動匯入、實際字型打包與失敗路徑測試，仍需受影響 C4 的啟動紀錄驗證是否為同一原因。

每次分支推送會執行全新環境檢查，刻意不安裝 `pyserial` 或保留 SCons 產物，並同時測試 Raylib 5.5 與 6 的 C3／C4 更新畫面相依圖及字型圖集大小。若更新後仍停留，請記下最後畫面、等待時間及車機 IP；使用區域網路 `http://車機IP:6999` 查看可用的復原入口。一般啟動錯誤保留在 `/tmp/carrot_startup_failure.log`，重新開機前應先取得；請勿把尚在執行的編譯當成失敗而反覆斷電。


原上游安裝地址保留如下：

```text
i.carrotpilot.app/carrot-wip
```

**上述 `i.carrotpilot.app` 網址安裝上游版本，不會安裝本倉庫的繁中修改。** 本倉庫使用上方 sunnypilot 安裝服務，未建立獨立安裝服務。

`carrot-wip` 是持續開發和釋出同步進行的 rolling branch。為了解決車輛特定問題、風險點和錯誤，程式碼會經常更新，它並不像傳統穩定版那樣長期凍結不變。更新前請確認改動內容，更新後請在能夠立即接管車輛控制的環境中進行驗證。

公開的預構建 `carrot` 分支也存在，但沒有積極維護，因此當前推薦的釋出分支是 `carrot-wip`。

## Jetson 連接與安裝

原始韓文說明記載：2026-09-27 整合後，`carrot-wip` 已包含 Jetson 推論連線、USB 導航影像與儀表、Wi-Fi 資訊傳遞、IP／溫度／錯誤顯示及簽章更新，不需另裝 `carrot-jetlink` 分支。既有 eGPU 的 Cinque v3 與 Jetson 的獨立 Cinque v2 各自保留。

[Windows 安裝指南（韓文）](https://github.com/ajouatom/carrot-jetson/blob/main/docs/INSTALL-WINDOWS-KO.md)說明下載 ZIP、解壓縮並依序執行 **01 → 02** 批次檔，自動準備、修正 USB-C、寫入與驗證映像。

M.2 NVMe SSD 提供相同映像加 **03 共用修補**的實驗路徑，見 [microSD／NVMe 共用修補說明](https://github.com/ajouatom/carrot-jetson/blob/main/docs/jetson_sd_nvme_patch.md)。原始文件註明修補媒體實際開機及 PC 離線修補卡首次實機啟動仍待驗證，見 [整合與驗證範圍](docs/jetson_wip_integration_20260927.md)。

## 支援裝置

- comma three (C3)
- comma 3X (C3X)
- comma four (C4)

部分非原廠或克隆裝置也提供有限相容性，但其硬體配置和品質並不一致。特別是部分裝置沒有可用的朝向駕駛的攝影機，或者其攝影機支援不正常。這些配置不推薦使用，也不保證裝置相容性或 Driver Monitoring 行為。

“實驗性”或“有限相容”標籤僅用於描述技術成熟度和驗證範圍，並不免除法律要求、安全標準或使用者責任。

## 車輛支援範圍

carrotpilot 的開發和實際回饋主要聚焦 Hyundai（現代）·Kia（起亞）·Genesis（HKG）車輛。

倉庫中也包含從 upstream openpilot 繼承來的其他製造商車輛程式碼和支援列表，但這並不意味著這些車輛都已被 carrotpilot 單獨驗證或被積極支援。沒有使用者回饋的製造商和車型無法保證其可用性和品質。

在安裝前，請先查閱 [使用說明書](https://g4iwnl.gitbook.io/carrotpilot) 和 [Wiki](https://github.com/ajouatom/openpilot/wiki)，確認車輛相容性、所需線束和已知限制。

## Hyundai（現代）·Kia（起亞）·Genesis 線束與縱向控制

| 車輛配置 | 常見連線與控制方式 |
|---|---|
| CAN 車輛 | 使用 comma 原廠線束，連線攝影機 |
| CAN-FD 普通車輛 | 使用 comma 原廠線束，連線攝影機 |
| 配備 ADAS 模組的 CAN-FD HDA2 車輛 | 使用單獨線束，連線 ADAS 模組 |

在受支援的 CAN-FD HDA2 配置中，裝置連線到 ADAS 模組，carrotpilot 的 openpilot 縱向控制會直接生成加速和減速指令。這不同於完全依賴原廠 SCC 進行縱向控制的方式。

並非所有車輛和車型年都受支援。即使車名相同，線束、連線位置和縱向控制相容性也可能因平臺、ECU、攝影機和 ADAS 配置而不同，因此請務必確認車輛具體支援資訊。

## 與 upstream openpilot 的差異

### 車輛安全與 CAN 策略

carrotpilot 會在部分安全策略和 CAN 接受條件上與 upstream openpilot 不同。這些調整考慮了受支援車輛上已確認的 CAN 訊息週期、計數器、控制方式以及車輛故障案例。倉庫中包含針對特定訊息或時序條件進行調優的程式碼，旨在避免干擾車輛正常控制流程。

這意味著 carrotpilot 與 comma.ai 官方 safety model 並不完全一致，也不能保證它在所有車輛和場景下都更安全，或滿足特定的功能安全標準。安全相關修改應基於記錄、可重現案例和本倉庫中的測試來評估。

### 駕駛監控（Driver Monitoring）

carrotpilot 會調整 Driver Monitoring 行為，以減少當駕駛確實在看前方時仍反覆觸發告警的問題。

Driver Monitoring 預設開啟。但在一些無法使用朝向駕駛的攝影機的硬體上（包括部分非原廠裝置），也提供關閉選項。關閉後，將無法使用基於攝影機的駕駛狀態檢測，以及相關的告警和減速功能，因此不推薦使用此配置。無論 Driver Monitoring 是否啟用，駕駛都應始終注視道路，並準備好隨時接管車輛控制。

## 開發與驗證範圍

本倉庫包含從 openpilot 繼承來的測試，以及 carrotpilot 自有的車輛控制、設定和安全相關測試。但這並不等同於 comma.ai 的官方釋出驗證或內部 HIL（硬體迴路測試）體系，也不意味著所有車輛、線束和裝置組合都已完成驗證。

`carrot-wip` 會根據實際使用回饋持續更新。對於文件中未說明的配置或沒有回饋的車輛，應視為未驗證狀態。

## 法律聲明

在車輛中安裝或修改軟體，可能會受到司法管轄區和車輛配置相關法律、汽車安全要求、檢查規定及保險條款的約束。

以下為原始 README 法律聲明的翻譯：韓國《汽車管理法》限制對可能影響車輛安全行駛的軟體進行任意修改、安裝、增設或刪除。詳細內容請參考 [韓國官方法規資料庫的《汽車管理法》](https://www.law.go.kr/lsInfoP.do?chrClsCd=010102&lsId=001747&lsiSeq=260419&viewCls=lsRvsDocInfoR)。

carrotpilot 是一個正在開發中的駕駛輔助軟體，而不是經認證的車輛零件或自動駕駛產品。本倉庫不對特定場景下的車輛適配性、法律合規性或安全性做出擔保。使用者應自行確認適用法律法規，並對自身裝置、安裝、設定和使用承擔責任。本聲明不構成法律意見。

## 文件

- [CarrotPilot 使用說明書](https://g4iwnl.gitbook.io/carrotpilot)
- [本分支設定 Wiki（含繁體中文）](https://github.com/TonyBinheWu/sunnypilot/wiki)
- [語音播報音量 SoundLanguageVolume 繁中詳細指南](https://github.com/TonyBinheWu/sunnypilot/wiki/ZH-TW-語音播報音量)
- [上游 CarrotPilot Wiki](https://github.com/ajouatom/openpilot/wiki)

carrotpilot 的官方公開說明主要以上述使用說明書和 Wiki 為主。請先查閱這些文件，確認車輛要求和設定說明。

## 署名與授權條款

carrotpilot 基於 comma.ai 和 openpilot 貢獻者開發的 [openpilot](https://github.com/commaai/openpilot)。openpilot 以 MIT License 釋出，部分元件可能適用其他授權條款。詳細資訊請檢視 [LICENSE](LICENSE) 和各元件的授權條款聲明。

“openpilot”與 comma 硬體名稱均屬於其相應權利人。carrotpilot 不屬於 comma.ai 的關聯專案，也未獲得 comma.ai 的背書。

FormosaLink 新增 [管理者診斷台與行車紀錄分享](formosalink/docs/SUPPORT_LOGS.md)：可取得的診斷日誌與另行同意上傳的完整 rlog 都保留 30 天，提供搜尋、下載、停用與刪除。需同時更新車機、網站及 IIS 後端；未配對／未同意者不會自動上傳。
