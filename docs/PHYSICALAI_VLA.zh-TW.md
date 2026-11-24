# PhysicalAI 駕駛 VLA 回放

這個分支以 **PhysicalAI-reason-VLA 4B** 評估額外的視覺、語言與動作模型。工具讀取前方 ROAD 影像與截至該影格的兩秒自車運動，另向模型詢問縱向行為、橫向行為與移動方向。有方向的動作需要明確的左或右回答。模型自由選出的詞若無法辨認，對應欄位會顯示 `null`。這是本專案的簡短提問方式，上游的完整生成模式另可輸出未來軌跡。駕駛控制程序不會載入這個回放工具。[模型說明](https://huggingface.co/mjf-su/PhysicalAI-base-VLA) · [原始權重](https://huggingface.co/mjf-su/PhysicalAI-reason-VLA/tree/d3da993ddddd10cfc24884059d491fdcaf3c1ba4)

## 模型與顯存

文字與動作模型採 Q4_K_M，影像投影器採 Q8_0。兩檔合計 2,950,729,728 位元組，執行時還需顯存放置相機特徵、各層中間結果、驅動配置及主駕駛模型。工具會先核對兩檔的 SHA-256。權重存放在專案目錄外。[量化檔案與固定版本](https://huggingface.co/mradermacher/PhysicalAI-reason-VLA-GGUF/tree/841fac174b8e3da0d5ca7ee56a2b15c879b1fb29)

## 已量到的表現

使用 PhysicalAI-reason-US 的 GRPO 分割中 13 張公開道路影格，每張搭配該次曝光的真實歷史位姿。原始影像為 640 × 360，本次推理縮放至 320 × 192。提示只含當下影像、歷史位置與固定問題。資料集的動作標註僅在推理後用於比對。[資料集版本與座標定義](https://huggingface.co/datasets/mjf-su/PhysicalAI-reason-US/tree/3f6c213462259664fe3f7a6a3eb3cf59a26db909)

| RTX 5080 桌機，VLA 單獨執行 | 第一次判讀 | 後續 12 次中位數 | 縱向、橫向均符合資料標註 |
| --- | ---: | ---: | ---: |
| tinygrad CUDA，與 Chestnut 入口共用模型程式 | 21.07 秒 | 6.96 秒 | 2 / 13 |
| llama.cpp b12676 Vulkan 參考執行器 | 0.28 秒 | 0.21 秒 | 2 / 13 |

計時從已解碼的 RGB 影像進入推理到兩軸結果可讀為止，載入權重與檔案解碼另計。兩種後端在 12 / 13 張給出相同的兩軸結果。各後端均有 4 張縱向、8 張橫向符合標註，3 張橫向棄答。3 張標為右轉的影格均未得到右轉。這些是此量化版本、解析度與提示在小樣本上的觀察。台灣路況、C3X／C4 上 RX 9060 8 GB 的執行時間，以及大模型並行時的顯存與主模型影格延遲均尚待驗證。

另用兩筆合成行車紀錄分別啟動兩個後端，以 `nvidia-smi` 取樣整張 RTX 5080 的顯存用量。Vulkan 從 965 MiB 升至 4,395 MiB，增量約 3.35 GiB。tinygrad CUDA 從 945 MiB 升至 7,552 MiB，增量約 6.45 GiB。這是桌機取樣峰值，包含驅動及其他桌面程序波動。當時由回放讀取已記錄的主模型結果。

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
