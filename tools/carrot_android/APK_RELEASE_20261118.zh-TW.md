# 2026-11-18 APK 同步發行

- [Formosa 座艙 0.6.1 APK](https://github.com/TonyBinheWu/sunnypilot/releases/download/carrot-cockpit-tw-v0.6.1/CarrotCockpit-TW-0.6.1.apk)：版本代碼 9，套件 `me.shind0.carrotweb.tw.cockpit`。
- [CarrotAssist 繁中 0.2.20 APK](https://github.com/TonyBinheWu/sunnypilot/releases/download/carrot-assist-tw-v0.2.20/CarrotAssist-TW-0.2.20.apk)：版本代碼 27，套件 `me.shind0.carrotweb.tw`。

兩版沿用原本簽章、套件與各自更新頻道，能覆蓋安裝並保留資料，舊發行檔保持不變。座艙沒有新增麥克風權限，標準版繼續保留原有語音功能。

本次同步行車回放控制列自動收合、SEI 車況、影片比例與返回清理修正。介面由車機提供，先更新至 `carrot-wip` 的 `8ea7577b` 或更新版本並重新啟動；只更新 APK 不會更新車機網頁。舊影片沒有 SEI 時仍可播放，並顯示缺少資料的提示。

兩個 APK 來源均為 `ae7beb7cd32a171e9cf8b250ee5e04e73135bf17`。GitHub Actions 原生建置／測試與 v2／v3 簽章驗證通過：座艙 [44283979374](https://github.com/TonyBinheWu/sunnypilot/actions/runs/44283979374)，標準版 [44284050202](https://github.com/TonyBinheWu/sunnypilot/actions/runs/44284050202)。另獨立核對 v2 檔案內容摘要及 RSA 簽章、既有憑證、版本、ZIP CRC、權限未變與 SHA-256；草稿資產逐檔比對後才公開。

已驗證兩版 APK 與校驗檔可免登入下載，兩個 App 更新頻道均指向新版本。簽章憑證 SHA-256：`90e20971ea5792bd0fb3cee37e573fd15388ee7a84e84c83cf736967e6b051a8`。

| 版本 | APK SHA-256 |
|---|---|
| Formosa 座艙 0.6.1 | `59ac090824d91e915ff0f7d770a01d5e700da72e31eff6b330b7a925b64f85d1` |
| CarrotAssist 0.2.20 | `ccfa47e49720d2321ad54c68d8bd1d818cbfed37032a505557cf4c6c24750161` |

座艙 0.6.1 在 Samsung SM-A146P／Android 14 覆蓋安裝成功，原連線資料保留；實測停車車機的舊影片開啟、無 SEI 提示、第一次返回先關閉播放器、第二次返回主畫面。標準版完成建置與檔案驗證，本次未另安裝到手機，不宣稱已完成相同實機驗收。

手機、1920×720、16:9／4:3、大字、全螢幕與合成影片動態 SEI 的既有驗證見 [SEI 回放驗證](SEI_REPLAY_ACCEPTANCE.zh-TW.md)。未宣稱所有車用盒子、實車道路或 SIM 門號共享上網均已驗收。
