# Google 顯示／搜尋 + Mapbox 路徑與模型

更新 carrot-wip 並重新啟動後，網頁、CarrotAssist 與 Carrot Cockpit 的「導航地圖／Navigation」共用本功能。**預設仍為原有 Mapbox**；不會自動建立 Google 帳單、使用共用金鑰或觸發付費搜尋。

## 分工與路線一致性

| 工作 | 來源 |
| --- | --- |
| 使用者觀看的地圖／衛星圖層 | 選用 Google Maps JavaScript API |
| 地點搜尋與選取座標 | Google Places UI Kit 基本搜尋元件 |
| 路徑規劃、轉彎指引 | 原有 Mapbox 流程；外部導航的既有優先順序保留 |
| 給導航模型的圖資／影像 | 原有 Mapbox／mapsd，不改用 Google 圖層 |
| Google 地圖上畫出的路徑 | mapsd 正在使用的同一份 navRoute 座標，不向 Google 或 Mapbox另算第二條路徑 |

Google 搜尋只在按「搜尋」／Enter 後查詢，最多顯示5筆，使用原有 Google 元件與標示。選取後將座標交給原有目的地入口。沒有背景自動完成、Google Routes／Directions、額外 Place.fetchFields、私有圖磚網址或地圖截圖回灌模型。切換地圖不會更改轉向、縱向控制或導航模型設定。

顯示路線由獨立 tmpfs UI 副本取得，保留最多4096個原始點；最多每秒更新一次。資料超過3秒／連線失敗即清除顯示的路徑與車輛位置。它不是模型輸入，也不是車輛控制通道。停車時可以搜尋／設定目的地；路線及位置是否可見仍取決於車機提供的有效資料。

## 開啟方式

1. 建立自己的 Google Cloud 專案、連結帳單，啟用 **Maps JavaScript API、Places UI Kit API**。本方案不需要啟用 Google Routes 或 Geocoding API。
2. 建立**瀏覽器金鑰**，設定「網站／HTTP 參照網址」及上述兩項 API 限制。例：依實際車機地址加入 `http://192.168.1.55:7000/*`；IP／通訊埠更動也要更新限制。不要使用不受限制的共用金鑰。瀏覽器金鑰必然會送到觀看裝置，不應當成隱藏伺服器密鑰。
3. 開啟導航頁 →「地圖與搜尋來源」，選 Google、輸入金鑰後儲存。頁面重新載入，以清除舊的 SDK／金鑰狀態；原有 Mapbox Public Key 仍須保留供路徑使用。金鑰不必貼到聊天。
4. 搜尋可以直接使用；**按「載入 Google 地圖」後才建立動態地圖**。同一頁內重用同一個地圖，切換道路／衛星圖層、拖曳及回到車輛位置不會刻意重建地圖。關閉頁面再開、重新整理或另開分頁會有新的地圖載入。
5. Google 最愛保存**地點 ID 與使用者命名**，不持久保存 Google 座標／地址。點最愛時會以可見的 Places UI Kit 詳情元件重新取得座標，再送往 Mapbox；會產生一次查詢。既有 Mapbox 最愛及其編輯／刪除功能照常保留，兩種可並存。可在 Google 搜尋後按「儲存目前目的地」，或在新增最愛中搜尋、命名後儲存。
6. 「結束當前導航」沿用原有目的地清除流程；外部導航須在來源 App 結束。

API／帳單／來源限制不符時顯示繁中提示。Google 查詢失敗不會自動重送，也不會暗中改成另一套付費搜尋。原有導航預覽及原生 Carrot Navi 內容仍使用原來的模型地圖。

### 個人只用 FormosaLink 時

將瀏覽器金鑰的網站來源限制為 `https://formosapilot.dinglu-t.com/*`，API限制僅選 Maps JavaScript API 與 Places UI Kit API。不要加上任意網址、全部 IP 或全網域萬用字元。透過自己的已登入裝置設定儲存，金鑰不放入公開 APK、Git、README 或安裝網址。此限制的金鑰不能從區域網路IP、localhost或原生LAN版APK直接使用，這是預期的來源限制。

瀏覽器金鑰仍可由獲准使用的瀏覽器看見；來源限制不等於使用者身分驗證，也不是絕對防盜。FormosaLink登入／裝置所有權限制金鑰的提供範圍，Google端的API限制、配額及警報則控制濫用風險；洩漏時應停用並更換。降低可用配額可能讓地圖／搜尋達量後暫時無法使用，原有Mapbox流程可保留。是否有適用的每日硬配額須以實際Google服務頁確認，不能把每分鐘限制或通知冒稱為月費上限。

## 預算（2026-11-17 查核）

適用 Google 一般全球按量價格、美元未稅；不含 Mapbox 本身費用、地區差異或另行簽約價格。免費量是帳單帳戶依 SKU 計算的月額度，不是每位使用者各一份。

| SKU | 每月免費量 | 超過免費量後的第一級價格 |
| --- | --- | --- |
| Dynamic Maps | 10,000 次地圖載入 | US$7／1,000次 |
| Places UI Kit Query | 10,000 次查詢 | US$1／1,000次 |

例如一個月6,000次地圖載入＋6,000次基本搜尋，若帳戶沒有其他相同 SKU 用量，Google 這兩項可落在免費量內；20,000次地圖載入＋20,000次查詢則約 US$80。**這是依目前價格的估算，不是零費用保證。** 搜尋結果選取直接取得座標，不另加一般 Place Details 呼叫；再次開啟 Google 最愛需計入一次查詢。[Google 價目表](https://developers.google.com/maps/billing-and-pricing/pricing)、[UI Kit 計費事件](https://developers.google.com/maps/billing-and-pricing/sku-details/places#places-ui-kit-query)。

純 Embed 雖有不限量免費 SKU，但無法作為本方案可控的地圖來畫出同一份 Mapbox 路徑；Android 原生 Maps SDK 也有不同計費，但不是目前網頁與 APK 共用的 WebView 架構。因此目前選擇**按需建立一次動態地圖＋手動基本搜尋**，不反覆下載 Static Maps 圖片。

在 Cloud Console 設定預算通知，並在**實際支援的 API 配額**限制每日用量；先用低額度確認需求，再調高。**預算通知不會自動停用計費。** 多人共用同一專案時要計算總量，不能僅靠單機限制保證全體不超支。[Google 成本控制說明](https://developers.google.com/maps/billing-and-pricing/manage-costs)。

## 授權與已驗證範圍

Places UI Kit 明文允許搭配非 Google 地圖，座標暫存仍有30天限制；本方案不將它們存入長期最愛資料。[服務專用條款第15節](https://cloud.google.com/maps-platform/terms/maps-service-terms#15.-places-ui-kit)。地圖上的 Google 標示、搜尋元件標示與法律連結保留；Mapbox 路線另行標明來源。

**Google Maps 一般條款第3.2.3(f)排除嵌入式車載系統。** Android盒子、車機／CarPlay大螢幕的整合，須向 Google 確認適用的車載授權／合約；一般瀏覽器金鑰不能代替車載許可。這是實際部署條件，不代表本專案已取得 Google 的車載授權。[Google Maps Platform 條款](https://cloud.google.com/maps-platform/terms)。

已以隔離測試驗證按需載入、重用地圖、手動搜尋的選取座標、最愛 ID 存取、原始路線點與過期清除；Mapbox 既有測試通過。**尚未提供可用 Google 金鑰，因此沒有宣稱已完成真實 Google API、帳單、實體 Android 車載或實車驗收。**
