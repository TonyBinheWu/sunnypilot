# C4 Chestnut 與 PhysicalAI 駕駛 VLA

這個分支以 **PhysicalAI-reason-VLA 4B** 評估額外的視覺、語言與動作模型。工具讀取前方 ROAD 影像與截至該影格的兩秒自車運動，另向模型詢問縱向行為、橫向行為與移動方向。有方向的動作需要明確的左或右回答。模型自由選出的詞若無法辨認，對應欄位會顯示 `null`。這是本專案的簡短提問方式，上游的完整生成模式另可輸出未來軌跡。駕駛控制程序不會載入這個回放工具。[模型說明](https://huggingface.co/mjf-su/PhysicalAI-base-VLA) · [原始權重](https://huggingface.co/mjf-su/PhysicalAI-reason-VLA/tree/d3da993ddddd10cfc24884059d491fdcaf3c1ba4)

## 模型與顯存

文字與動作模型採 Q4_K_M，影像投影器採 Q8_0。兩檔合計 2,950,729,728 位元組，執行時還需顯存放置相機特徵、各層中間結果、驅動配置及主駕駛模型。工具會先核對兩檔的 SHA-256。權重存放在專案目錄外。[量化檔案與固定版本](https://huggingface.co/mradermacher/PhysicalAI-reason-VLA-GGUF/tree/841fac174b8e3da0d5ca7ee56a2b15c879b1fb29)

## C4 內建小模型搭配 RX 9060

1. 將 RX 9060 8 GB 透過 Chestnut USB 連到 C4。停車、關閉點火，在 Carrot 手機網頁或 App 開啟「工具 → sunnypilot 駕駛模型選擇器」。Formosa 座艙的入口是「應用程式 → 工具／診斷」。
2. 將「重新開機後的主駕駛模型」設為內建小模型，再將「PhysicalAI-reason-VLA 4B · C4 Chestnut 決策比對」設為「與內建主模型比對」。等下載驗證完成、設定顯示已開啟，再重啟 C4。功能預設關閉。
3. 行程中，小模型使用 C4 內建 GPU，VLA 的獨立程序使用 Chestnut。下次停車後可在同一頁查看本次比對的有效／逾時筆數、上次從影格曝光到推理完成的時間，以及最近一次有效停車判斷的比對。重新開機會清除這份暫存紀錄。

觀察程序使用 ROAD 相機與兩秒歷史車速、姿態，依影格編號和曝光時間配對主模型。最多每秒送兩張，每次只允許一筆推理。結果須在曝光後 500 毫秒內返回才算有效。主模型明確的停車判斷能與 VLA 的停車、維持車速或通過判讀比對；方向不明的動作保留為未知。這個版本由主模型負責實車轉向與加減速，VLA 結果供診斷。

觀察程序檢查 C4、USB 供電、GPU 架構 gfx1200、8 GiB 顯存、主模型健康、溫度與記憶體使用。主模型無法維持健康條件時會結束觀察。VLA 連續三筆逾時或工作程序失敗時，會釋放顯卡並停止該次行程的觀察。有效筆數若一直為零，代表這次沒有可用的即時觀察。

## 大模型與 VLA 共用同一張顯卡

Chestnut 的驅動由單一程序持有 GPU。大模型也用 RX 9060 時，這版提供停車台架測試。先在選擇器下載並選取一個 sunnypilot 大模型，並透過上述開關完成 VLA 權重安裝。關閉點火，退出強制停駛模式，在 C4 專案根目錄執行：

```sh
python -m openpilot.tools.vla.shared_bench --iterations 3
```

工具先以選定大模型執行 100 筆 20 Hz 基準量測，再於同一個 tinygrad 環境載入 VLA。每個視覺層、語言層及詞表分塊完成後同步 GPU，檢查是否已到主模型的下一次排程時間。這個測試無法搶占正在執行的 GPU 核心。錯過的影格計入統計，按最新時段繼續執行。兩路相機使用固定灰色輸入，VLA 搭配靜止歷史姿態，適合量測計算負載。

輸出包含主模型從排程到產生結果的 P95、最大延遲、跳過與逾時數、每筆 VLA 耗時及執行期間取樣的 AMD 張量配置量。張量取樣未涵蓋驅動和配置器保留的全部顯存。只有基準及並行主模型均無跳幀或超過 50 毫秒、每筆 VLA 均低於 500 毫秒時，計時測試才通過。結果只寫到終端。這個入口適用於選擇器中的 sunnypilot 大模型；carrot-wip 原有的大模型使用各自的執行環境。

## 已量到的表現

使用 PhysicalAI-reason-US 的 GRPO 分割中 13 張公開道路影格，每張搭配該次曝光的真實歷史位姿。原始影像為 640 × 360，本次推理縮放至 320 × 192。提示只含當下影像、歷史位置與固定問題。資料集的動作標註僅在推理後用於比對。[資料集版本與座標定義](https://huggingface.co/datasets/mjf-su/PhysicalAI-reason-US/tree/3f6c213462259664fe3f7a6a3eb3cf59a26db909)

| RTX 5080 桌機，VLA 單獨執行 | 第一次判讀 | 後續 12 次中位數 | 縱向、橫向均符合資料標註 |
| --- | ---: | ---: | ---: |
| tinygrad CUDA，與 Chestnut 入口共用模型程式 | 21.07 秒 | 6.96 秒 | 2 / 13 |
| llama.cpp b12676 Vulkan 參考執行器 | 0.28 秒 | 0.21 秒 | 2 / 13 |

計時從已解碼的 RGB 影像進入推理到兩軸結果可讀為止，載入權重與檔案解碼另計。兩種後端在 12 / 13 張給出相同的兩軸結果。各後端均有 4 張縱向、8 張橫向符合標註，3 張橫向棄答。3 張標為右轉的影格均未得到右轉。這些是此量化版本、解析度與提示在小樣本上的觀察。台灣路況、C3X／C4 上 RX 9060 8 GB 的執行時間，以及大模型並行時的顯存與主模型影格延遲均尚待驗證。

另用兩筆合成行車紀錄分別啟動兩個後端，以 `nvidia-smi` 取樣整張 RTX 5080 的顯存用量。Vulkan 從 965 MiB 升至 4,395 MiB，增量約 3.35 GiB。tinygrad CUDA 從 945 MiB 升至 7,552 MiB，增量約 6.45 GiB。這是桌機取樣峰值，包含驅動及其他桌面程序波動。當時由回放讀取已記錄的主模型結果。

另外在 Windows 工作站用實際的 CD210 ONNX 主模型與 VLA 同時執行。CD210 使用四執行緒 ONNX Runtime CPU、固定輸入及 20 Hz 排程；VLA 使用公開道路影格和歷史姿態。以下耗時從已解碼 RGB 到動作輸出，不包含相機擷取或 USB 傳輸。

| VLA 後端 | VLA 耗時 | 同時執行的 CD210 | CD210 從排程到輸出的 P95 |
| --- | --- | --- | ---: |
| tinygrad CUDA，RTX 5080，逐層同步 | 兩張分別為 21.89 秒、9.86 秒 | 完成 631 幀，其中 79 幀超過 50 毫秒，另跳過 6 幀 | 58.24 毫秒 |
| llama.cpp Vulkan，RTX 5080 | 13 張介於 190–281 毫秒，中位數 236 毫秒 | 完成 63 幀，逾時與跳幀均為 0 | 14.91 毫秒 |

桌機 tinygrad 測試在同一 Python 程序以不同執行緒執行兩個模型，Vulkan 使用獨立服務。C4 內建主模型與 VLA 使用獨立程序。RX 9060、Chestnut USB 頻寬、車機 CPU 以及兩個模型共用 8 GB 時的延遲均須在指定硬體上量測。桌機 Vulkan 的成績尚未在 Chestnut 執行環境重現。

## 回放當下的主模型

使用此分支記錄的同一段 `rlog`（亦支援 bz2／zst）與 `fcamera.hevc`。工具按 ROAD 編碼索引的顯示順序讀取影像，以相同的 `frameId` 及奈秒 `timestampEof` 配對有效的 `modelV2`。同一段最多每秒取一張。輸出包含主模型當時的運算來源、期望加速度、曲率及停車判斷。影像來源不明、只有廣角、時鐘無法配對或缺少連續車速／姿態資料的樣本會略過。主模型的紀錄只用於輸出比對。曾以兩個實際編碼的合成紀錄樣本驗證內建與外接主模型的配對。

在專案 Python 環境中從根目錄執行。以下為有可用 Vulkan 顯卡的工作站範例，先用 `llama-server --list-devices` 確認 Radeon 對應的裝置編號，再替換範例中的 Vulkan0 與檔案路徑。首次加入 `--fetch` 下載固定版本。參考執行器須使用 llama.cpp b12676，程式會在本機建立和關閉推理服務。[llama.cpp b12676](https://github.com/ggml-org/llama.cpp/releases/tag/b12676)

```sh
python -m openpilot.tools.vla.replay --backend vulkan --server /path/to/llama-server --device Vulkan0 --weights /path/to/vla-weights --fetch --segment /path/to/segment
```

Chestnut 測試入口使用專案內的 tinygrad、`USB+AMD:LLVM` 及原有的 eGPU 獨占鎖。在 AGNOS 上限停車台架使用，車機進入行車狀態就終止回放。此入口尚未在實體 Chestnut 或 RX 9060 驗證。桌機 CUDA 測試可使用 `--backend cuda`。

```sh
python -m openpilot.tools.vla.replay --backend chestnut --weights /data/vla-weights --segment /data/vla-test-segment
```

已有獨立影格與真實運動紀錄時，可用 `--manifest frames.jsonl` 取代 `--segment`。每列須包含相對於清單位置的本機影像路徑 `image`、相機時間 `timestamp_us`，以及由早到晚的九筆 `egomotion`。各筆是相對於該影格自車座標的 `[前向公尺, 左向公尺, 逆時針弧度]`，間隔 0.25 秒，最後一筆為原點。
