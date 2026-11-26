# FormosaLink ccNC 區網版

## 手機連車機

1. 車機更新 `ccnc-port` 並重啟。Android 8.0 以上手機可從 FormosaLink 登入頁或「軟體」下載安裝檔。[下載 FormosaLink ccNC 1.0.0](https://formosapilot.dinglu-t.com/downloads/FormosaLink-ccNC-1.0.0.apk)
2. 手機和車機連到彼此可以通訊的同一個 Wi-Fi。停車後，在車機進入「FormosaLink → 區網 APK → 產生配對碼」。
3. 開啟手機上的 FormosaLink ccNC，輸入車機顯示的 IP、12 碼憑證碼及六位數配對碼，按「連線」。配對碼有效兩分鐘。
4. 下次連線只需車機目前的 IP。要加第二支手機，在車機再按「產生配對碼」。車機的「停用並解除配對」會撤銷所有區網手機。

模型、車型、導航目的地與各項停車設定由車機回報可用選項。按「儲存」後可看到車機回讀結果。「影音」可選路面或車內鏡頭。區網連線直接使用車機的 TCP 8787 與綁定的 TLS 憑證。

## 備份與還原

網頁與 APK 的裝置選單都有「設定檔」。按「匯出 JSON」即可儲存目前偏好。還原時選「匯入設定檔」，核對項目和新舊值，再按「套用差異」。車機每確認一項，才送出下一項。更換車型或儀表開關後依車機提示重啟。若中途離線，重新匯入同一檔案即可繼續處理剩餘差異。

檔案包含裝置支援的偏好、車型與選定的模型。帳號、手機配對、授權、位置、行程與一次性操作均由各裝置各自管理。

## 開發者建置

準備 Android SDK Platform 35、Build Tools 35.0.0、JDK 17 以上與發布用 keystore。建置程式從環境變數 `CCNC_APK_SIGNING_PASSWORD` 讀取簽署密碼，參數 `--alias` 預設為 `formosalink-ccnc`。同一套件後續更新需使用原簽署金鑰並遞增 AndroidManifest 的 versionCode。

```sh
python formosalink/android/build.py --sdk /path/to/android-sdk --jdk /path/to/jdk --keystore /path/to/release.p12 --output FormosaLink-ccNC-1.0.0.apk
```
