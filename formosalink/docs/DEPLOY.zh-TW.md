# FormosaLink：IIS / Python 自架部署

目標：`https://formosapilot.dinglu-t.com`；網站實體目錄：`\\192.168.20.145\htdocs\FormosaPilot`。
需建立獨立 IIS 網站，掛在網域根目錄；第一版不支援 `/FormosaPilot/` 子路徑。UNC 目錄只提供檔案存取，不等於遠端執行權限。以下伺服器命令需在 192.168.20.145 本機執行。

## 1. IIS 前置設定

- 網域 DNS 指向對外主機；IIS 綁定此主機名稱與有效 HTTPS 憑證，開放 443。裝置須可驗證完整憑證鏈。
- 安裝 IIS Static Content、WebSocket Protocol、URL Rewrite 與 Application Request Routing (ARR)。PHP 可以保留，但此服務不依賴 PHP。
- 在 IIS **伺服器層級**的 ARR Server Proxy Settings 啟用 Proxy，開啟 `preserveHostHeader=true`。轉送時必須保留 `formosapilot.dinglu-t.com` 的 Host；後端會驗證 Host，錯誤時回傳 400。
- ARR 代理逾時設為至少 60 秒，確認 WSS Upgrade 可以透傳。若平台會壓縮代理回應，關閉 API 的壓縮以免影響 WebSocket。
- 網站目錄如果使用 UNC，設定應用程式集區／Connect As 的共享與 NTFS 讀取權限。網站帳號不需要寫入來源碼的權限。
- 本機 Python 僅監聽 `127.0.0.1:8765`，不將 8765 暴露到外部。

IIS `web.config` 會強制 HTTPS、代理 `/api/*`，並禁止下載 `App_Data`、Python、資料庫、金鑰檔。若 Rewrite/ARR 尚未安裝或設定區段被鎖定，網站可能回傳 500.19；先完成伺服器設定。不要透過移除保護規則來排除錯誤。

## 2. 複製部署檔

在開發電腦、儲存庫根目錄執行：

```powershell
.\tools\deploy\publish_formosalink_iis.ps1 -CheckOnly
.\tools\deploy\publish_formosalink_iis.ps1
```

腳本首次只接受空目錄；後續以 `App_Data/formosalink-deployment.json` 識別本服務。只複製程式、三語前端、logo 與部署設定，逐檔比對 SHA-256，不刪除其他檔案，不複製測試資料、帳號或私鑰。重新部署後需要重啟 Python 程序；不會自動重啟主機上的服務。

## 3. 初始化 Python 後端

也可在 **IIS 主機的系統管理員 PowerShell** 執行一次完整設定腳本：

```powershell
& '\\192.168.20.145\htdocs\FormosaPilot\App_Data\setup-server.ps1'
```

若主機停用 PowerShell 腳本，只對這次程序放行：`powershell.exe -NoProfile -ExecutionPolicy Bypass -File "\\192.168.20.145\htdocs\FormosaPilot\App_Data\setup-server.ps1"`，不設定永久執行原則。若既有 Python 版本不符，在指令最後加入 `-InstallPython`。它會使用已釘選 SHA-256、驗證 PSF 簽章的官方 Python 3.14.10 NuGet 發行包，解壓到網站外的專用目錄，不改 PATH、既有 Python 或啟動器註冊。執行環境不需要 PHP。來源與發行方式見 [Python 官方 Windows 文件](https://docs.python.org/3.14/using/windows.html)。

它會辨識共享目錄的本機位置、檢查 Python 3.12～3.14、建立虛擬環境與私有資料目錄、安裝相依套件，並在需要時停下來讓你親自輸入管理者密碼。程式碼移至網站外，使用 LocalService 的開機排程、單一執行個體、失敗重試與循環日誌。請使用 LocalService 可讀取的系統層 Python 安裝。已有帳號不會被覆寫。`-CheckOnly` 僅顯示環境；可用 `-Python 'C:\Python312\python.exe'` 明確指定直譯器。設定腳本不會開放 WinRM／SSH、不改防火牆、不替其他網站變更 IIS 全域設定。完成後回到聊天，由開發端驗證外部 API 與登入／配對。

在 IIS 主機開 PowerShell。以下 `D:\htdocs\FormosaPilot` **需替換成共享目錄在主機上的真實路徑**，不是已確認的磁碟位置。

```powershell
$siteRoot = 'D:\htdocs\FormosaPilot'
$dataRoot = 'C:\ProgramData\FormosaLink'
Set-Location "$siteRoot\App_Data\server-package"
py -3.12 -m venv C:\ProgramData\FormosaLink-venv
$python = 'C:\ProgramData\FormosaLink-venv\Scripts\python.exe'
& $python -m pip install -r formosalink\requirements.txt
& $python -m formosalink.server.config --data-dir $dataRoot --origin https://formosapilot.dinglu-t.com
```

密碼由互動提示輸入，至少 14 字，不會寫入命令列或網站目錄。`config.json` 與 SQLite 放在 `$dataRoot`，以 NTFS ACL 僅授權後端服務帳號與系統管理員。程式的 POSIX mode 不能替代 Windows ACL。已有設定時初始化會拒絕覆寫。

啟動：

```powershell
& "$siteRoot\App_Data\start-server.ps1" -DataDirectory $dataRoot -Python $python
```

先前景確認啟動正常，再使用 Windows 工作排程器建立開機啟動工作，執行同一支啟動腳本，選「不論使用者是否登入都執行」，設定失敗後重試。限一個執行個體，不要使用多 worker。服務帳號應能讀取 App_Data 與虛擬環境、寫入資料目錄。SQLite 必須放在主機本機磁碟，不放 SMB 分享。

## 4. 車上配對

先安裝包含本次修改、已正常建置的 `hkg-enhanced` 或 `ccnc-port`。停駛時在裝置終端、openpilot 根目錄執行：

```bash
python -m openpilot.sunnypilot.formosalink.cli --lang zh-TW pair --url https://formosapilot.dinglu-t.com --enable
```

瀏覽手機網站登入管理者帳號，選「配對裝置」，填入本機顯示的 12 位配對碼、24 位指紋與名稱。配對碼十分鐘內有效且僅可使用一次。啟用後 manager 自動管理 agent；手機沒有啟用駕駛或修改 Params 的功能。

裝置身分存於 `/data/formosalink/identity.json`，權限 0600，獨立於 comma/sunnylink。不要上傳、複製到另一台裝置或納入一般設定備份。撤銷後此身分永久不可再連線；重新加入須在本機停用 agent、備存並移走舊身分檔，再重新配對，不能只在雲端取消撤銷。

```bash
python -m openpilot.sunnypilot.formosalink.cli --lang zh-TW status
python -m openpilot.sunnypilot.formosalink.cli --lang zh-TW disable
```

## 5. 驗收與備份

- `/api/v1/health` 回傳 FormosaLink；未登入 `/api/v1/devices` 回傳 401。
- `/App_Data/server-package/formosalink/server/app.py` 與任何資料／私鑰網址均不可下載。
- 手機以行動網路登入、配對；三語切換完整且保留選擇，可加入主畫面。
- 裝置斷線顯示離線；資料超過 20 秒或來源無效則過期，不顯示舊值為即時數值。
- 撤銷時當前連線中止；舊金鑰不能重新連線。
- 雲端關閉時，裝置原有行車程序不依賴此平台。
- 分別驗證 C3X／C4、兩分支的啟停、狀態有效性、CPU／記憶體負載與熱狀態。
- 停止 Python 後備份整個資料目錄至受保護位置。還原 config 與資料庫後重啟；裝置重新連線。遺失資料庫後需重新配對。來源碼與 logo 可由部署包恢復。

只有 SMB 檔案存取時，可以完成檔案部署，但不能宣稱已完成 IIS、憑證、後端工作排程與對外連線驗證。

## 本機開發與示範

在獨立測試目錄初始化 `--origin http://127.0.0.1:8765`，執行 `python -m formosalink.server --data-dir <測試目錄>`。原生伺服器可直接提供前端。需要示範資料時用 CLI 的獨立 `--state-dir <示範目錄>` 進行 pair，再 `run --demo`；畫面標為示範裝置。預設不建立示範裝置。

Linux 可用 `docker compose -f formosalink/deploy/compose.yaml run --rm -it formosalink python -m formosalink.server.config --data-dir /state --origin https://formosapilot.dinglu-t.com` 初始化，再 `up -d`。此骨架使用 Linux host networking，需另設本機 HTTPS 反向代理，不能直接套用於 Windows Docker。
