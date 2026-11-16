# C3／C3X／C4 通用安裝入口

入口：<https://is.gd/tonyc4>；只讀診斷：<https://is.gd/tonyc4check>。
完整服務：<https://carrot-tw-install.tony-binhe-wu.chatgpt.site>。
目標固定為 `https://github.com/TonyBinheWu/sunnypilot.git`、`carrot-wip`。

三種機型使用同一個既有短網址 `is.gd/tonyc4`。`tici`、`tizi`、`mici` 分別對應 C3、C3X、C4。選擇、併發合併、快取與備援均以「裝置＋AGNOS 版本」為鍵。實際來源比對中，`19.6.3` 的 tici 回 current，tizi／mici 回 legacy，因此不能共用版本快取。

## 為何需要版本選擇

同一個 `i.carrotpilot.app/carrot-wip`，在 `AGNOSSetup-19.6.3` 與
`AGNOSSetup-19.8` 的 C4 請求下會回傳不同 ARM64 ELF。不能用一個 Wayland
包裝檔涵蓋所有 C4。上游也提供針對 `19.6.3-carrot` 的原生相容樣板；
其報告僅驗證該系統，不能擴大成所有 C4 已通過。

來源：[上游相容樣板與報告](https://github.com/ajouatom/openpilot-installer-generator/tree/df6f48de28e47afd6662e0a9184ac11d48733f26/agnos_compat)。

## 選擇與修改範圍

- 接受版本化 `AGNOSSetup-*` 與明確的 `tici`／`tizi`／`mici` 裝置標頭。
- 舊式無版本 `AGNOSSetup` 僅在裝置明確為 tici／tizi 時使用原有 sunnypilot fork 服務的固定 classic 樣板。該檔案原本已指向本倉庫與分支，只修改快取識別字；不變更倉庫欄位。缺少裝置代碼或 C4 無版本時停止，不猜測機型。
- 一般版本向固定上游網址詢問，只送版本與裝置類型；不轉送序號、Cookie、Authorization 或使用者提供的其他標頭。
- 回應大小、ARM64 ELF 標頭與 SHA-256 必須符合 `PROFILES`。改變的來源停止服務，人工檢查後才更新固定值。
- 僅 C4 的 `19.6.3-carrot` 直接使用固定原生相容樣板；C3／C3X 繼續向來源詢問。網路失敗時只有已核對的裝置／版本組合可用固定備援；來源完整性失敗不使用備援。
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

34 項案例覆蓋五個真實 ELF 的資料修改邊界、來源不變性、分支處理、快取識別字、
完整性拒絕、請求標頭過濾、併發合併、已知版本備援與只讀診斷。
另驗證裝置標頭轉送、同版本跨裝置快取隔離、C4 override 隔離、舊式 C3 請求與錯機型樣板拒絕。抓取腳本核對 18 組真實裝置／版本來源回應並保存 `routing-matrix.json`；來源變動會使檢查失敗。測試下載但不執行 ARM64 檔案。CI 每次推送重新抓取並檢查固定來源。

服務使用獨立 Sites 來源倉庫與 ESM Worker；五個固定樣板內嵌於建置產物，
來源附原始 SHA-256 與上游 MIT 授權。重新發布必須使用同一個
`.openai/hosting.json` 的專案 ID，保留存取權限並透過 Sites 流程保存、部署確切提交。
更新此處 Worker 後，也必須同步服務來源、測試、重建與重新部署；推送車機分支
不會自動更新下載服務。

公開後需透過原短網址匿名驗證三種裝置與已核對版本的狀態、實際 SHA-256、目標與設定欄位以外的內容，
並確認短網址保留 AGNOS 標頭及 `/check` 409 文字。這些都不是 C4 實機驗收。
目前使用者尚未回報新入口是否出現 Installing；若仍失敗，需實際版本或啟動日誌
繼續定位，不能宣稱根因已完全排除。

`19.8-carrot-bt1` 的實際上游回應與 compat 僅倉庫及分支欄位不同，SHA-256 固定為 `972678b20da245a1a1f68835b3705233e4ded63077ca610e45ed6bcf242d1fd0`。建置不重複內嵌程式碼，備援由 compat 原始資料重建兩個欄位，再通過相同精確雜湊檢查。獨立案例驗證線上下載與斷線備援逐位元組一致。應用程式不記錄序號，但主機平台的請求日誌可能含標頭；不可宣稱完全無平台紀錄。

C3／C3X 的 ELF 與下載分流已做主機驗證，仍待實機新安裝；不可把下載雜湊通過擴大為實機顯示或整個安裝流程已驗收。classic 來源：<https://install.sunnypilot.ai/fork/TonyBinheWu/carrot-wip>。
