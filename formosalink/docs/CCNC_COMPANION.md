# FormosaLink ccNC 區網版

## 手機連車機

1. 車機更新 `ccnc-port` 並重啟。Android 8.0 以上手機可從 FormosaLink 登入頁、儀表板或裝置首頁下載安裝檔。[從分支下載簽章 APK 1.1.0](https://github.com/TonyBinheWu/sunnypilot/raw/refs/heads/ccnc-port/formosalink/web/downloads/FormosaLink-ccNC-1.1.0.apk)
2. 手機和車機連上同一個 Wi-Fi，打開 App 就會搜尋附近的車機。停車後，在車機點「設定 → 裝置 → 區網手機配對」。C4 的設定首頁也有同名捷徑，C3X 可從 FormosaLink 分頁開啟。
3. 在 App 點選與車機畫面識別碼相同的裝置，輸入六位數配對碼。配對碼有效兩分鐘。已配對的手機下次開啟 App 會自動重新連線，即使車機的區網 IP 已變更。
4. 要加第二支手機，再點一次車機的「區網手機配對」。若網路過濾探索封包或韌體較舊，可用「手動連線」。訪客網路若隔離裝置，請改連允許裝置互通的 Wi-Fi。車機的「停用並解除配對」會撤銷所有手機的存取權。

模型、車型、導航目的地與各項停車設定由車機回報可用選項。按「儲存」後可看到車機回讀結果。「影音」可選路面或車內鏡頭。車機以 UDP 8787 回覆同一網段的搜尋；停車時可在首次配對前找到車機。配對與操作使用 TCP 8787 的 TLS 連線。搜尋回覆只含公開憑證指紋。

## 備份與還原

網頁與 APK 的裝置選單都有「設定檔」。按「匯出 JSON」即可儲存目前偏好。還原時選「匯入設定檔」，核對項目和新舊值，再按「套用差異」。車機每確認一項，才送出下一項。更換車型或儀表開關後依車機提示重啟。若中途離線，重新匯入同一檔案即可繼續處理剩餘差異。

檔案包含裝置支援的偏好、車型與選定的模型。帳號、手機配對、授權、位置、行程與一次性操作均由各裝置各自管理。

## 開發者建置

準備 Android SDK Platform 35、Build Tools 35.0.0、JDK 17 以上與發布用 keystore。建置程式從環境變數 `CCNC_APK_SIGNING_PASSWORD` 讀取簽署密碼，參數 `--alias` 預設為 `formosalink-ccnc`。同一套件後續更新需使用原簽署金鑰並遞增 AndroidManifest 的 versionCode。

```sh
python formosalink/android/build.py --sdk /path/to/android-sdk --jdk /path/to/jdk --keystore /path/to/release.p12 --output FormosaLink-ccNC-1.1.0.apk
```
