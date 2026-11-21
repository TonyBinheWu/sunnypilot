# ccNC 線組與無原廠 SCC 車型的縱向驗收

2026-11-21 以 `carrot-wip` 的 `8fe4a0f0d` 為基準，比對 `hkg-enhanced` 的 opendbc `4ece3bb67` 與 `ccnc-port` 的 `23330cb5a`。本批新增 17 個平台、18 個車型與線組組合。以下的「接收」表示可解析車況供紀錄或顯示。全部新增平台目前均為 dashcam，Panda 使用 noOutput，實驗模式、Alpha 主機縱向、DEC 切換縱向及自動起步均未開放。原車巡航仍由原車操作。

## ccNC

線組字母沿用來源分支的 Hyundai harness 名稱。除另列的 K4 HDA II 外，表內 ccNC 規格均為無 HDA II。每格的 n/m 表示相同 m 段實車資料中有 n 段通過。A 欄重播來源控制命令，B 欄將同一段 carControl 交給目標分支控制器重新產生命令，再檢查 Panda 是否接受全部命令、接收資料是否有效。兩欄都是離線測試。

| 車型 | 線組 | 片段編號 | 來源記錄中的縱向 | 接收 | A | B |
| --- | --- | --- | --- | --- | --- | --- |
| Hyundai Kona 汽油 2024–25 | L | 2、6 | 主機縱向 | 2/2 | 0/2 | 0/2 |
| Hyundai Sonata HEV 2024–26 | A | 2、4 | 主機縱向 | 2/2 | 1/2 | 0/2 |
| Hyundai Santa Cruz 2025 | N | 2、14 | 原廠 SCC | 2/2 | 1/2 | 2/2 |
| Hyundai Tucson 汽油 2025–26 | N | 2、10 | 原廠 SCC | 2/2 | 1/2 | 1/2 |
| Hyundai Tucson HEV 2025–26 | N | 2、8 | 原廠 SCC | 2/2 | 2/2 | 2/2 |
| Hyundai Tucson PHEV 2025 | N | 待取得 | 未確認 | — | — | — |
| Kia K4 2025–26 | A | 2、4 | 主機縱向 | 2/2 | 1/2 | 2/2 |
| Kia K4 HDA II 2025 | R | 待取得 | 未確認 | — | — | — |
| Kia K5 2025–26 | M | 2、44 | 原廠 SCC | 2/2 | 1/2 | 2/2 |

7 組已回放的 ccNC 車輛都在鏡頭側收到原廠 SCC 訊息。來源相機的巡航請求與煞車控制器回報可能不同，已以後者的有效訊號顯示實際介入，並讓過期的速度、跟車間隔與介入回報失效。讀到同一個 CAN ID 不足以認定線組版本或轉向模式。

Tucson HEV 有一段巡航持續介入，兩段資料通過兩種主動相容性檢查。該車兩段都是原廠 SCC，尚無該線組主機縱向加速、減速、接管及解除的閉環證據。Kona、Sonata HEV 與 Tucson 汽油在目標控制器重播時，Panda 均曾拒收 LFA 轉向訊息；目前無法據此歸因為實車縱向故障。來源命令在 Panda 允許控制時仍被拒收的數量為 Kona 第 6 段 1 筆、Santa Cruz 第 14 段 52 筆、Sonata HEV 第 4 段 208 筆、K5 第 44 段 15 筆。目標控制器產生的 LFA 拒收則全部發生在 Panda 未允許控制時。原廠鏡頭線路與改裝線路在目標分支共用軟體旗標。針對本批原廠 ccNC 線組，已排除由主機重送轉向柱扭力、方向盤觸摸與煞車控制器回報；回放會逐筆檢查這三個訊息的發送者。仍需核對原廠訊息透過線組的實際轉送與 ECU 接收。即使 Panda 接受一批訊息，也無法證明原車 ECU 已依預期接手或解除控制。

### 接上同一趟行程的前一分鐘

上述 15 段獨立測試以外，另取得 6 段直接相鄰的實車 rlog，使 Panda 與車輛控制器能從前一段延續狀態。確認相鄰 CAN 時間戳後，重新統計表中列出的後段。因此共使用 21 個不同片段，6 組連續測試與單段表內的目標片段重疊。

| 車型、相鄰片段 | 重播來源命令 A | 重算目標命令 B |
| --- | --- | --- |
| Kona 汽油 5 → 6 | 通過 | 5,887 筆轉向訊息遭拒 |
| Santa Cruz 13 → 14 | 通過 | 通過 |
| Sonata HEV 3 → 4 | 通過 | 通過 |
| Tucson 汽油 9 → 10 | 1,976 筆轉向訊息遭拒 | 1,976 筆轉向訊息遭拒 |
| K4 3 → 4 | 1 筆轉向訊息遭拒 | 通過 |
| K5 43 → 44 | 通過 | 通過 |

兩種測法各有 4/6 通過。所有連續回放的後段均無無效 RX，必要訊息健康檢查也都通過。表內剩下的拒收全部發生在 Panda 未允許控制時。這讓單段起始歷史的影響可以區分出來；Kona 汽油更顯示，同樣的原始資料能讓來源命令通過，換目標控制器重算仍遭拒收。這六組均未測量實車煞車或加速度回應。

## 沒有原廠 SCC 的車型

一般定速由車輛維持設定速度，本批接收邏輯依汽油、油電／插電與純電平台分別判讀。這九款均缺少本分支已驗證的主機加減速介面。來源分支標成 dashcam 的車型也列出，避免將車型登錄誤認為實車控制支援。

| 車型 | 線組 | 定速狀態／驗證進度 |
| --- | --- | --- |
| Hyundai Bayon 2021 | N | 汽油訊號，待實車片段；來源為 dashcam |
| Hyundai Elantra 2022 | K | 汽油訊號，待實車片段 |
| Hyundai Kona 2019 | B | 汽油訊號，待實車片段 |
| Hyundai Kona Electric 2019 | G | 純電訊號，待實車片段；已知韌體與有 SCC 版本重疊，未新增自動匹配規則 |
| Kia Ceed PHEV 2022 | I | 第 2 段原廠定速實際啟用與解除，接收 1/1；A、B 各 0/1。現有主動 Panda 設定要求車上缺少的 SCC 回報 |
| Kia Forte 2019 | G | 汽油訊號，來源車型無已定義的 FCA 回報；待實車片段 |
| Kia Forte 2021 | G | 汽油訊號，待實車片段；來源為 dashcam |
| Kia Seltos 2023–24 | L | 汽油訊號，待實車片段；來源為 dashcam |
| Genesis G70 2021 | F | 原廠 FCA 由動力總線讀取，待實車片段；來源為 dashcam |

Ceed 的有效比對區間有 5,699 次車況更新，其中 4,729 次一般定速已介入，巡航、檔位與煞車狀態皆與原紀錄一致。Panda 主動設定在同區間持續缺少必要回報。此結果不能證明可提供 ACC 跟車、煞停或 Alpha。Kona Electric 缺可獨立識別的特徵，尚不能據此把一台實車自動指派為無 SCC 版本。

## 已在目標分支登錄的相關平台

| 既有平台 | 此次核對的線組差異 |
| --- | --- |
| Kona HEV 二代 | 既有 L，未用汽油版的驗證替代油電版 |
| Kona Electric 二代 | 目標已列韓規 HDA II 的 R，來源另列無 HDA II 的 A；A 線組待取得可核對的實車紀錄 |
| Sonata 汽油 2024 | 既有 A，不能以 HEV 測試替代 |
| Ioniq 5 N | 目標列 M，來源的 HDA II 列 S；待核對實車線組與總線紀錄 |
| Sorento 2024 | 目標已列 A；沿用既有支援。本批片段未驗證先前回報的 30 km/h 現象 |

## 重現方式與驗收界線

8 個平台共 15 段公開實車 rlog。全部通過車型韌體精確比對、Panda 接收、車況有效性、檔位、煞車和巡航狀態比對，並確認 noOutput 拒絕了所有錄下的發送訊息。另以原生 Panda 檢查兩條主動路徑，A 為 7/15，B 為 9/15。判定要求零拒收且必要接收狀態健康。每段獨立從空狀態開始，若錄影起始時車輛已介入，缺少前一段的授權事件也可能造成拒收。要區分接合前歷史與真正不相容，必須覆蓋完整的進入、退出與駕駛接管，不能從單一片段推論道路上的因果。

[車型與錄製路線](../opendbc_repo/opendbc/car/tests/routes.py) · [逐幀驗證程式](../tools/signal_validation/test_hkg_harness_replay.py) · [平台能力與失效測試](../opendbc_repo/opendbc/car/hyundai/tests/test_harness_ports.py)

在已建立原生 CAN 與 Panda 測試函式庫的 Linux 環境，將授權使用的 rlog 放入同一目錄，依「平台列舉名稱.片段編號.rlog」命名。可讀取 zstd 或 bzip2。ccNC 路線可從 comma 路線收件服務取得，Ceed 的第 2 段來自 sunnypilot 公開資料集。[公開車輛片段](https://huggingface.co/datasets/sunnypilot/sunnypilotCarSegments)

```sh
export HKG_REPLAY_DIR=/path/to/recordings
python tools/signal_validation/run.py tools/signal_validation/test_hkg_harness_replay.py
HKG_ACTIVE_PROBE=recorded python tools/signal_validation/run.py tools/signal_validation/test_hkg_harness_replay.py
HKG_ACTIVE_PROBE=generated python tools/signal_validation/run.py tools/signal_validation/test_hkg_harness_replay.py
```

要重現連續測試，將上一段的 rlog 命名為「平台列舉名稱.上一段編號.pre」，再於 A 或 B 命令加上環境變數 `HKG_PREROLL=1`。程式會使用具備前段的目標片段；先確認車型與相鄰時間，再延續解析器、Panda 與控制器狀態。只有後段進入表中統計。

離線工作程序會封鎖車機 IPC、使用測試設定，依 rlog 傳入訊息與時間戳。兩種主動模式皆只在記憶體中執行。它們無法測到車輛 ECU 的實際回應、線組的物理轉送或實車煞車效果。
