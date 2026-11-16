# C4 版本相容安裝入口

入口：<https://is.gd/tonyc4>；只讀診斷：<https://is.gd/tonyc4check>。
完整服務：<https://carrot-tw-install.tony-binhe-wu.chatgpt.site>。
目標固定為 `https://github.com/TonyBinheWu/sunnypilot.git`、`carrot-wip`。

## 為何需要版本選擇

同一個 `i.carrotpilot.app/carrot-wip`，在 `AGNOSSetup-19.6.3` 與
`AGNOSSetup-19.8` 的 C4 請求下會回傳不同 ARM64 ELF。不能用一個 Wayland
包裝檔涵蓋所有 C4。上游也提供針對 `19.6.3-carrot` 的原生相容樣板；
其報告僅驗證該系統，不能擴大成所有 C4 已通過。

來源：[上游相容樣板與報告](https://github.com/ajouatom/openpilot-installer-generator/tree/df6f48de28e47afd6662e0a9184ac11d48733f26/agnos_compat)。

## 選擇與修改範圍

- 僅接受版本化 `AGNOSSetup-*` 與 `X-openpilot-device-type: mici`。
- 一般版本向固定上游網址詢問，只送版本與裝置類型；不轉送序號、Cookie、Authorization 或使用者提供的其他標頭。
- 回應大小、ARM64 ELF 標頭與 SHA-256 必須符合 `PROFILES`。改變的來源停止服務，人工檢查後才更新固定值。
- `19.6.3-carrot` 直接使用固定原生相容樣板。網路失敗時只有已核對的 `19.6.3`、`19.8`、`20.0` 可用固定備援；來源完整性失敗不使用備援。
- 修改預留的倉庫欄位；相容樣板另修改預留分支欄位。保留一般樣板原有的條件式 `--no-single-branch`。
- 舊版 `legacy`／`compat` 沒有複製工廠快取後的 `git remote set-url`。將其同長度資料字串 `/data/.openpilot_cache` 改成 `/data/.carrot_cache_v3`，使正常首次安裝重新 clone 目標倉庫；服務不建立此識別檔，也不修改或搬移工廠檔案。若手動建立該私人識別檔，不再保證走全新 clone。
- 明確逐位元組檢查上述範圍以外保持原樣；不改指令碼、字型、動態載入器或 ELF 程式指令。

`/check` 回 HTTP 409 與 ASCII 版本資訊，不下載或執行安裝器。新版 Setup
會顯示 409 文字，受影響 C4 的舊版介面尚待驗證。一般瀏覽器看到繁中說明，
`/manifest` 提供固定來源雜湊；沒有裝置請求列表、資料庫或上傳功能。
版本快取與併發受限制，不保存裝置識別資料。

## 測試與發布

```sh
python tools/carrot_installer/fetch_profiles.py --output /tmp/carrot-fixtures
CARROT_INSTALLER_FIXTURES=/tmp/carrot-fixtures node --test tools/carrot_installer/test_gateway.mjs
```

9 項案例覆蓋三個真實 ELF 的資料修改邊界、來源不變性、分支處理、快取識別字、
完整性拒絕、請求標頭過濾、併發合併、已知版本備援與只讀診斷。
測試下載但不執行 ARM64 檔案。CI 每次推送重新抓取並檢查固定來源。

服務使用獨立 Sites 來源倉庫與 ESM Worker；三個固定樣板內嵌於建置產物，
來源附原始 SHA-256 與上游 MIT 授權。重新發布必須使用同一個
`.openai/hosting.json` 的專案 ID，保留存取權限並透過 Sites 流程保存、部署確切提交。
更新此處 Worker 後，也必須同步服務來源、測試、重建與重新部署；推送車機分支
不會自動更新下載服務。

公開後需匿名驗證四個版本的狀態、實際 SHA-256、目標與設定欄位以外的內容，
並確認短網址保留 AGNOS 標頭及 `/check` 409 文字。這些都不是 C4 實機驗收。
目前使用者尚未回報新入口是否出現 Installing；若仍失敗，需實際版本或啟動日誌
繼續定位，不能宣稱根因已完全排除。
