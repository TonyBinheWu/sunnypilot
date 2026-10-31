# C3X／C4 版本與更新說明

`hkg-enhanced` 與 `ccnc-port` 都使用以下發布流程。兩分支可使用相同的維護版號，但更新說明第一行必須標示自己的分支。

## 每次發布

1. 更新 `openpilot/sunnypilot/common/version.h` 的 `SUNNYPILOT_VERSION`。
2. 在 `CHANGELOG.md` 最前面新增該分支的繁體中文更新說明，版號與標頭檔相同，日期使用實際發布日期。
3. 列出 C3X、C4 的變更；未變更時明確寫出。不要把其他分支的功能列成此次新增功能。
4. 最新一筆內不要留空白行，直到下一個版本前才空一行。這讓尚未安裝新版程式的舊更新器也能讀完全部項目。
5. 執行 `python tools/release/check_release_notes.py` 與 `python -m unittest openpilot.common.tests.test_release_notes -v`。
6. 發布前分別在 C3X 與 C4 查看下載完成後的版本及更新項目，安裝重開機後再確認目前版本與說明。此項需實機驗證。

格式範例（另一分支改用 `ccnc-port`）：

```text
sunnypilot hkg-enhanced Version 2026.003.001 (2026-10-31)
========================
* C3X：本次修正與功能說明。
* C4：本次修正與功能說明。
```

## 資料流

* 裝置顯示的 sunnypilot 版本來自 `openpilot/sunnypilot/common/version.h`。`openpilot/common/version.h` 是 openpilot 基底版號，不用它代替本分支版號。
* `openpilot/common/release_notes.py` 擷取最新說明，供 build metadata 與 updated 共用；以 UTF-8 讀取。
* updated 分別讀取目前安裝目錄與已下載完成的 FINALIZED 目錄，寫入 `UpdaterCurrentDescription`／`UpdaterCurrentReleaseNotes` 和 `UpdaterNewDescription`／`UpdaterNewReleaseNotes`。
* C3X 的大型介面沿用軟體設定與更新通知；C4 的小型介面新增待更新與目前版本說明按鈕，以直向捲動閱讀內容。
* 將裝置語言設為繁體中文，才能同時使用中文介面與對應的中文字型。
* GitHub Release／release-drafter 不會自動取代裝置讀取的 `CHANGELOG.md`，兩者需分別維護。

若製作 prebuilt 或 stripped 套件，必須保留版本標頭、CHANGELOG 與 release_notes 模組；若打包流程覆寫版號，需同步更新對應說明，不能沿用來源版本的標頭。

GitHub Actions 的 Device release notes 工作會檢查版號、分支標示、C3X／C4 說明與舊更新器格式相容性；文字是否正確使用繁體中文仍需人工審閱。
