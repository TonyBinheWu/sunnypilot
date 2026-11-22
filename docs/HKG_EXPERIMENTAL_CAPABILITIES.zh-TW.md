# Hyundai、Kia 與 Genesis 實驗縱向配置

本表列出 carrot-wip 車型目錄在開發分支的離線配置結果。測試逐一呼叫 CarInterface.get_params，開啟實驗縱向，使用預設線組、未指定雷達或踏板改裝。車型資格、實際線組及 Panda 控制授權須同時成立。表中的「可選」只表示車型介面接受此配置。

| 車型代碼 | 匯流排 | 預設配置下的實驗縱向 |
| --- | --- | --- |
| `GENESIS_EQ900` | CAN | 此配置無法啟用 |
| `GENESIS_EQ900_L` | CAN | 此配置無法啟用 |
| `GENESIS_G70` | CAN | 此配置無法啟用 |
| `GENESIS_G70_2020` | CAN | 可選 |
| `GENESIS_G80` | CAN | 此配置無法啟用 |
| `GENESIS_G80_2ND_GEN_FL` | CAN-FD | 可選 |
| `GENESIS_G90` | CAN | 可選 |
| `GENESIS_G90_2019` | CAN | 此配置無法啟用 |
| `GENESIS_GV60_EV_1ST_GEN` | CAN-FD | 可選 |
| `GENESIS_GV70_1ST_GEN` | CAN-FD | 可選 |
| `GENESIS_GV70_ELECTRIFIED_1ST_GEN` | CAN-FD | 可選 |
| `GENESIS_GV70_EV_1ST_GEN` | CAN-FD | 可選 |
| `GENESIS_GV80` | CAN-FD | 可選 |
| `HYUNDAI_AZERA_6TH_GEN` | CAN | 可選 |
| `HYUNDAI_AZERA_7TH_GEN` | CAN-FD | 可選 |
| `HYUNDAI_AZERA_HEV_6TH_GEN` | CAN | 可選 |
| `HYUNDAI_CASPER` | CAN | 可選 |
| `HYUNDAI_CASPER_EV` | CAN | 可選 |
| `HYUNDAI_CUSTIN_1ST_GEN` | CAN | 可選 |
| `HYUNDAI_ELANTRA` | CAN | 此配置無法啟用 |
| `HYUNDAI_ELANTRA_2021` | CAN | 可選 |
| `HYUNDAI_ELANTRA_GT_I30` | CAN | 此配置無法啟用 |
| `HYUNDAI_ELANTRA_HEV_2021` | CAN | 可選 |
| `HYUNDAI_GENESIS` | CAN | 此配置無法啟用 |
| `HYUNDAI_GRANDEUR_IG` | CAN | 此配置無法啟用 |
| `HYUNDAI_GRANDEUR_IG_HEV` | CAN | 此配置無法啟用 |
| `HYUNDAI_IONIQ` | CAN | 可選 |
| `HYUNDAI_IONIQ_5` | CAN-FD | 可選 |
| `HYUNDAI_IONIQ_5_N` | CAN-FD | 可選 |
| `HYUNDAI_IONIQ_5_PE` | CAN-FD | 可選 |
| `HYUNDAI_IONIQ_6` | CAN-FD | 此配置無法啟用 |
| `HYUNDAI_IONIQ_9` | CAN-FD | 可選 |
| `HYUNDAI_IONIQ_EV_2020` | CAN | 可選 |
| `HYUNDAI_IONIQ_EV_LTD` | CAN | 此配置無法啟用 |
| `HYUNDAI_IONIQ_HEV_2022` | CAN | 此配置無法啟用 |
| `HYUNDAI_IONIQ_PHEV` | CAN | 可選 |
| `HYUNDAI_IONIQ_PHEV_2019` | CAN | 可選 |
| `HYUNDAI_KONA` | CAN | 可選 |
| `HYUNDAI_KONA_2022` | CAN | 可選 |
| `HYUNDAI_KONA_EV` | CAN | 可選 |
| `HYUNDAI_KONA_EV_2022` | CAN | 可選 |
| `HYUNDAI_KONA_EV_2ND_GEN` | CAN-FD | 此配置無法啟用 |
| `HYUNDAI_KONA_HEV` | CAN | 可選 |
| `HYUNDAI_KONA_HEV_2ND_GEN` | CAN-FD | 可選 |
| `HYUNDAI_NEXO` | CAN | 可選 |
| `HYUNDAI_NEXO_1ST_GEN` | CAN | 可選 |
| `HYUNDAI_PALISADE` | CAN | 可選 |
| `HYUNDAI_PORTER_II_EV` | CAN | 此配置無法啟用 |
| `HYUNDAI_SANTAFE_MX5` | CAN-FD | 可選 |
| `HYUNDAI_SANTAFE_MX5_HEV` | CAN-FD | 可選 |
| `HYUNDAI_SANTA_CRUZ_1ST_GEN` | CAN-FD | 可選 |
| `HYUNDAI_SANTA_FE` | CAN | 可選 |
| `HYUNDAI_SANTA_FE_2022` | CAN | 可選 |
| `HYUNDAI_SANTA_FE_HEV_2022` | CAN | 可選 |
| `HYUNDAI_SANTA_FE_PHEV_2022` | CAN | 可選 |
| `HYUNDAI_SONATA` | CAN | 可選 |
| `HYUNDAI_SONATA_2024` | CAN-FD | 可選 |
| `HYUNDAI_SONATA_HYBRID` | CAN | 可選 |
| `HYUNDAI_SONATA_LF` | CAN | 此配置無法啟用 |
| `HYUNDAI_STARIA_4TH_GEN` | CAN-FD | 可選 |
| `HYUNDAI_STARIA_EV` | CAN-FD | 可選 |
| `HYUNDAI_TUCSON` | CAN | 可選 |
| `HYUNDAI_TUCSON_4TH_GEN` | CAN-FD | 可選 |
| `HYUNDAI_VELOSTER` | CAN | 此配置無法啟用 |
| `KIA_CARNIVAL_4TH_GEN` | CAN-FD | 可選 |
| `KIA_CEED` | CAN | 此配置無法啟用 |
| `KIA_EV3` | CAN-FD | 可選 |
| `KIA_EV4` | CAN-FD | 可選 |
| `KIA_EV5` | CAN-FD | 可選 |
| `KIA_EV6` | CAN-FD | 可選 |
| `KIA_EV6_PE` | CAN-FD | 可選 |
| `KIA_EV9` | CAN-FD | 可選 |
| `KIA_EV_SK3` | CAN | 可選 |
| `KIA_FORTE` | CAN | 可選 |
| `KIA_K5` | CAN | 此配置無法啟用 |
| `KIA_K5_2021` | CAN | 可選 |
| `KIA_K5_DL3_24` | CAN-FD | 可選 |
| `KIA_K5_DL3_24_HEV` | CAN-FD | 可選 |
| `KIA_K5_HEV` | CAN | 此配置無法啟用 |
| `KIA_K5_HEV_2020` | CAN | 可選 |
| `KIA_K5_HEV_2022` | CAN | 此配置無法啟用 |
| `KIA_K7` | CAN | 此配置無法啟用 |
| `KIA_K7_HEV` | CAN | 此配置無法啟用 |
| `KIA_K7_HEV_PE` | CAN | 可選 |
| `KIA_K7_PE` | CAN | 可選 |
| `KIA_K8_HEV_1ST_GEN` | CAN-FD | 可選 |
| `KIA_K9` | CAN | 此配置無法啟用 |
| `KIA_MOHAVE` | CAN | 此配置無法啟用 |
| `KIA_NIRO_EV` | CAN | 可選 |
| `KIA_NIRO_EV_2ND_GEN` | CAN-FD | 可選 |
| `KIA_NIRO_HEV_2021` | CAN | 可選 |
| `KIA_NIRO_HEV_2ND_GEN` | CAN-FD | 可選 |
| `KIA_NIRO_PHEV` | CAN | 此配置無法啟用 |
| `KIA_NIRO_PHEV_2022` | CAN | 可選 |
| `KIA_OPTIMA_G4` | CAN | 此配置無法啟用 |
| `KIA_OPTIMA_G4_FL` | CAN | 此配置無法啟用 |
| `KIA_OPTIMA_H` | CAN | 此配置無法啟用 |
| `KIA_OPTIMA_H_G4_FL` | CAN | 此配置無法啟用 |
| `KIA_PV5` | CAN-FD | 可選 |
| `KIA_RAY_EV` | CAN | 需相符的踏板介面及有效回報 |
| `KIA_SELTOS` | CAN | 可選 |
| `KIA_SORENTO` | CAN | 此配置無法啟用 |
| `KIA_SORENTO_2024` | CAN-FD | 可選 |
| `KIA_SORENTO_4TH_GEN` | CAN-FD | 可選 |
| `KIA_SORENTO_HEV_4TH_GEN` | CAN-FD | 可選 |
| `KIA_SPORTAGE_5TH_GEN` | CAN-FD | 可選 |
| `KIA_STINGER` | CAN | 可選 |
| `KIA_STINGER_2022` | CAN | 可選 |

## 如何判讀

- 「自動適配實驗縱向」使用本次辨識的車型及線組。Camera SCC 模式 3 保留原廠巡航，與模型接管加減速互斥。
- 開啟實驗模式時可使用模型縱向規劃；啟用 DEC 後，規劃器會依觀測狀態在 ACC 與模型規劃間切換。雷達資料是否可用取決於該車實際接收到的訊息。
- 原廠 AEB 的可用性取決於煞車控制權與原廠 ECU 的運作狀態。接收雷達目標或成功回放 CAN 訊息，均不足以驗證 AEB 會介入。

## HKG Panda 相容範圍

比對基準是 HKG 的 Panda `5e0eb6e` 和 opendbc `4ece3bb`。車機與 Panda 的通訊、韌體建置方式沿用 carrot-wip。

| 配置 | 此分支的處理 |
| --- | --- |
| 傳統 CAN 儀表 | 依前攝影機匯流排實際出現的 LFAHDA 訊息，選用 4 或 8 位元組。舊設定沿用 8 位元組。 |
| 原廠巡航 | 恢復鍵須已有控制授權。自動降低設定速度另須有新鮮輪速、有效巡航狀態及駕駛未接管。 |
| 早期傳統 CAN | 在辨識到原廠 SCC12 的線組上驗證巡航訊息。無此訊號的早期線組沿用原先的接收條件。 |
| 攝影機 SCC 接管縱向 | 實際收到原廠緊急煞車命令時，優先轉送原廠訊息，限制主機同時送出巡航加速度。Casper EV 的儀表相容處理另外核對攝影機來源、時效、計數和警示狀態。 |
| 原廠訊息轉送 | 依訊息分別記錄主機最後一次獲准發送的時間。開機、切換模式及主機停止更新後，可恢復原廠訊息轉送。 |

傳統 CAN 錄影回放須含 `sendcan` 才能檢查實車當時送出的命令。檢查原廠 AEB 實際介入還需對應線組的原廠請求和煞車回應。ccNC 及無原廠 SCC 車型的主動控制能力，仍須逐車核對。
