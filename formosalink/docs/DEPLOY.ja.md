# FormosaLink：IIS / Python 導入手順

GitHub OAuth / [MULTI_USER.md](MULTI_USER.md)

URL は `https://formosapilot.dinglu-t.com`、配置先は `\\192.168.20.145\htdocs\FormosaPilot` です。専用 IIS サイトのルートで運用します。仮想サブディレクトリには対応しません。SMB はファイルの配置用であり、サーバー側の処理を実行する機能ではありません。

スクリプトが無効の場合は、今回のプロセスだけ許可します：`powershell.exe -NoProfile -ExecutionPolicy Bypass -File "\\192.168.20.145\htdocs\FormosaPilot\App_Data\setup-server.ps1" -Language ja`。既存 Python が未対応の場合は `-InstallPython` を追加します。SHA-256 と PSF 署名を検証した公式 Python 3.14.10 NuGet 版を Web ルート外へ配置し、PATH、既存 Python、ランチャー登録、恒久的な実行ポリシーは変更しません。

自動設定：IIS 本体で管理者 PowerShell を開き、`& '\\192.168.20.145\htdocs\FormosaPilot\App_Data\setup-server.ps1' -Language ja` を実行します。共有先のローカルパスと Python 3.12～3.14 を確認し、仮想環境と依存関係を準備します。必要な場合だけ本体でパスワードを入力します。実行コードを Web ルートの外へコピーし、LocalService の起動タスク、再試行、循環ログを設定します。LocalService から読めるシステム用 Python を使用してください。既存認証情報は上書きしません。`-CheckOnly` は確認のみ、`-Python 'C:\Python312\python.exe'` で実行環境を指定できます。リモート管理・ファイアウォール・IIS 全体設定は変更しません。完了したらチャットに戻り、外部 API を確認します。以下は手動設定です。

1. DNS、443 番ポート、有効な HTTPS 証明書を設定します。IIS Static Content、WebSocket Protocol、URL Rewrite、ARR を導入します。サーバーレベルで ARR Proxy と `preserveHostHeader=true` を有効にし、60 秒以上のタイムアウトと WebSocket Upgrade の転送を設定します。Python は `127.0.0.1:8765` のみにバインドします。PHP は不要です。UNC と NTFS を含め、IIS のアカウントにサイトの読み取り権限を付与します。
2. 開発 PC のリポジトリで `tools/deploy/publish_formosalink_iis.ps1 -CheckOnly` を実行し、確認後に `-CheckOnly` を外して実行します。初回の配置先は空である必要があります。再配置では管理用マーカーを確認し、各ファイルのハッシュを照合します。実行時の秘密情報はコピーしません。更新後は Python を再起動します。
3. IIS サーバー本体で、共有先に対応する実際のローカルパスを確認します。以下の `D:\htdocs\FormosaPilot` は例です。

```powershell
$siteRoot = 'D:\htdocs\FormosaPilot'
$dataRoot = 'C:\ProgramData\FormosaLink'
Set-Location "$siteRoot\App_Data\server-package"
py -3.12 -m venv C:\ProgramData\FormosaLink-venv
$python = 'C:\ProgramData\FormosaLink-venv\Scripts\python.exe'
& $python -m pip install -r formosalink\requirements.txt
& $python -m formosalink.server.config --data-dir $dataRoot --origin https://formosapilot.dinglu-t.com --lang ja
& "$siteRoot\App_Data\start-server.ps1" -DataDirectory $dataRoot -Python $python
```

14 文字以上の管理者パスワードを対話形式で入力します。データは Web ルートの外側にあるローカルディスクへ保存し、SMB に SQLite を置かないでください。Windows ACL でバックエンドのアカウントと管理者だけにアクセスを制限します。POSIX モードだけでは Windows のアクセス制御になりません。既存設定の上書きは拒否します。ワーカーは 1 個だけにします。前景で動作確認した後、Windows タスクスケジューラに同じ引数で起動タスクを登録し、ログインの有無にかかわらず実行、失敗時再起動、並列起動禁止を設定します。

4. 変更を含むソフトウェアをビルドしてデバイスへ導入し、停車中に本体で実行します。

```bash
python -m openpilot.sunnypilot.formosalink.cli --lang ja pair --url https://formosapilot.dinglu-t.com --enable
python -m openpilot.sunnypilot.formosalink.cli --lang ja status
```

スマートフォンでログインし、10 分以内に 12 文字のワンタイムコードと 24 文字のフィンガープリントを照合して入力します。有効化すると既存 manager が任意の agent を管理します。認証情報は `/data/formosalink/identity.json` に 0600 で保存し、comma/sunnylink とは独立しています。複製や一般設定バックアップへの混入は禁止してください。解除した ID では再接続できません。再登録には本体で agent を停止し、旧 ID を安全に保管して元の場所から移動した後、新規ペアリングを行います。停止コマンドは `python -m openpilot.sunnypilot.formosalink.cli --lang ja disable` です。

5. HTTPS の health、未ログイン API の 401、App_Data・Python・秘密ファイルのダウンロード拒否、携帯回線からの配対、3 言語表示、ホーム画面への追加を確認します。切断時はオフライン、無効な値や 20 秒以上前の値は古いデータとして表示します。解除時の即時切断と再接続拒否も確認します。C3X／C4 と両保守ブランチで起動・停止、値の有効性、負荷を検証します。クラウド停止が運転支援の起動条件にならないことを確認します。

Python を停止してから、保護されたデータディレクトリ全体をバックアップします。設定と SQLite を一緒に復元して再起動すると、デバイスは再接続します。登録情報を失った場合は再配対が必要です。IIS の 500.19 はモジュール不足や設定ロックを確認し、保護規則を削除して回避しないでください。ARR で Host を保持しない場合は 400 になります。ファイルの配置だけでは IIS、証明書、起動タスク、外部接続の検証は完了しません。

ローカル開発では、別のテスト用ディレクトリに `--origin http://127.0.0.1:8765` で初期化し、`python -m formosalink.server --data-dir <ディレクトリ>` を実行します。明示的な CLI `--state-dir <デモ用ディレクトリ>` で配対後、`run --demo` を使うとデモ表示のデータを送信できます。標準状態ではデモデータを作成しません。

Linux の任意構成：`docker compose -f formosalink/deploy/compose.yaml run --rm -it formosalink python -m formosalink.server.config --data-dir /state --origin https://formosapilot.dinglu-t.com` で初期化後、`up -d` を実行します。ホスト側に HTTPS リバースプロキシが必要です。Linux の host networking 用であり、Windows Docker 用ではありません。
