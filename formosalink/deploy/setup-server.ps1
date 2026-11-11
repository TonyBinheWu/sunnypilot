param(
  [string]$DataDirectory = 'C:\ProgramData\FormosaLink',
  [string]$Origin = 'https://formosapilot.dinglu-t.com',
  [string]$Python = '',
  [switch]$InstallPython,
  [switch]$ConfigureGitHub,
  [ValidateSet('zh-TW','en','ja')][string]$Language = 'zh-TW',
  [switch]$CheckOnly
)
# Run on the IIS host, not the developer PC. Never accepts a password argument.
$ErrorActionPreference = 'Stop'
$messages = @{
  'zh-TW' = @{ admin='請在 IIS 主機上以系統管理員身分開啟 PowerShell 後執行。'; python='需要 Python 3.12 或更新版本（小於 3.15）。'; initialize='接下來請在本機輸入管理者密碼；密碼不會傳送至聊天。'; ready='後端已啟動，本機健康檢查通過。請回到聊天，讓我驗證外部登入與配對。'; failed='後端尚未通過健康檢查，請查看資料目錄內的 server.log。'; wrongHost='請在 IIS 主機本機執行，不能從開發電腦透過 UNC 執行。' }
  'en' = @{ admin='Run PowerShell as administrator on the IIS host.'; python='Python >=3.12 and <3.15 is required.'; initialize='Enter the owner password locally. It is never sent to this chat.'; ready='Backend started; local health check passed. Return to the chat for external login and pairing verification.'; failed='Health check failed. See server.log in the state directory.'; wrongHost='Run on the IIS host itself, not from the developer PC over UNC.' }
  'ja' = @{ admin='IIS サーバーで管理者として PowerShell を開いて実行してください。'; python='Python 3.12 以上、3.15 未満が必要です。'; initialize='管理者パスワードを本体で入力してください。チャットには送信しません。'; ready='バックエンドを起動し、本体の正常性を確認しました。外部からのログインとペアリングの確認のためチャットに戻ってください。'; failed='正常性の確認に失敗しました。データ保存先の server.log を確認してください。'; wrongHost='開発 PC の UNC 経由ではなく、IIS サーバー本体で実行してください。' }
}
$text = $messages[$Language]
$appData = $PSScriptRoot
if ($appData.StartsWith('\\')) {
  $parts = $appData.TrimStart('\').Split('\')
  $serverName = $parts[0]
  $localAddresses = @(Get-NetIPAddress -AddressFamily IPv4 | Select-Object -ExpandProperty IPAddress)
  if ($serverName -notin @($env:COMPUTERNAME,'localhost') -and $serverName -notin $localAddresses) { throw $text.wrongHost }
  $share = Get-SmbShare -Name $parts[1] -ErrorAction Stop
  $appData = Join-Path $share.Path ($parts[2..($parts.Length-1)] -join '\')
}
$appData = [IO.Path]::GetFullPath($appData)
$siteRoot = [IO.Path]::GetDirectoryName($appData).TrimEnd('\')
$source = Join-Path $appData 'server-package'
if (-not (Test-Path -LiteralPath (Join-Path $source 'formosalink\server\app.py'))) { throw 'Missing FormosaLink server-package.' }
$dataRoot = [IO.Path]::GetFullPath($DataDirectory).TrimEnd('\')
if ($dataRoot.StartsWith('\\') -or $dataRoot.Equals($siteRoot,[StringComparison]::OrdinalIgnoreCase) -or $dataRoot.StartsWith($siteRoot+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'State must be on a local disk outside the website.' }
$codeRoot = $dataRoot + '-code'
$venvRoot = $dataRoot + '-venv'
$runtimeRoot = $dataRoot + '-python'
if ($InstallPython -and -not $CheckOnly) {
  $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
  if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw $text.admin }
  if (-not [Environment]::Is64BitOperatingSystem) { throw 'The isolated runtime requires 64-bit Windows.' }
  $package = Join-Path $appData 'installers\python.3.14.10.nupkg'
  if (-not (Test-Path -LiteralPath $package)) {
    New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($package)) -Force | Out-Null
    Invoke-WebRequest -Uri 'https://api.nuget.org/v3-flatcontainer/python/3.14.10/python.3.14.10.nupkg' -OutFile $package -UseBasicParsing
  }
  if ((Get-FileHash -LiteralPath $package -Algorithm SHA256).Hash -ne 'F54BA67C9951C3D773EA47D2BB095150C037C399F0423A968BCDA22809241784') { throw 'Python package integrity verification failed.' }
  $privatePython = Join-Path $runtimeRoot 'tools\python.exe'
  if (-not (Test-Path -LiteralPath $privatePython)) {
    if (Test-Path -LiteralPath $runtimeRoot) { throw 'Incomplete isolated runtime directory; inspect it before retrying.' }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [IO.Compression.ZipFile]::ExtractToDirectory($package,$runtimeRoot)
  }
  $signature = Get-AuthenticodeSignature -FilePath $privatePython
  if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'Python Software Foundation') { throw 'Python publisher verification failed.' }
  & icacls.exe $runtimeRoot /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F' '*S-1-5-19:(OI)(CI)RX' | Out-Null
  if ($LASTEXITCODE -ne 0) { throw 'Runtime ACL setup failed.' }
  $basePython = $privatePython
}
elseif (Test-Path -LiteralPath (Join-Path $runtimeRoot 'tools\python.exe')) { $basePython = Join-Path $runtimeRoot 'tools\python.exe' }
elseif ($Python) { $basePython = (Get-Command $Python -ErrorAction Stop).Source }
elseif (Get-Command py.exe -ErrorAction SilentlyContinue) { $basePython = & py.exe -3 -c 'import sys; print(sys.executable)'; if ($LASTEXITCODE -ne 0) { throw $text.python } }
else { $basePython = (Get-Command python.exe -ErrorAction Stop).Source }
$version = & $basePython -c "import sys; print(str(sys.version_info.major)+'.'+str(sys.version_info.minor))"
if ($LASTEXITCODE -ne 0 -or [version]$version -lt [version]'3.12' -or [version]$version -ge [version]'3.15') { throw $text.python }
if ($CheckOnly) { [pscustomobject]@{ Host=$env:COMPUTERNAME; Python=$basePython; Version=$version; Source=$source; State=$dataRoot; Origin=$Origin }; return }
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw $text.admin }
# WebSocket upgrades share the existing HTTPS/443 ARR route; no public Python port.
# Install before stopping the current task so a missing Windows feature cannot cause downtime.
if (Get-Command Get-WindowsFeature -ErrorAction SilentlyContinue) {
  $webSocketFeature = Get-WindowsFeature -Name Web-WebSockets
  if (-not $webSocketFeature.Installed) {
    $featureResult = Install-WindowsFeature -Name Web-WebSockets
    if (-not $featureResult.Success) { throw 'IIS WebSocket installation failed; existing backend was not stopped.' }
    if ($featureResult.RestartNeeded -eq 'Yes') { throw 'IIS WebSocket requires a host restart. Restart Windows, then rerun this script; existing backend was not stopped.' }
  }
}
else {
  $webSocketFeature = Get-WindowsOptionalFeature -Online -FeatureName IIS-WebSockets
  if ($webSocketFeature.State -ne 'Enabled') {
    $featureResult = Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebSockets -All -NoRestart
    if ($featureResult.RestartNeeded) { throw 'IIS WebSocket requires a host restart. Restart Windows, then rerun this script; existing backend was not stopped.' }
  }
}
$taskName = 'FormosaLink'
$description = 'FormosaLink managed Python backend'
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing -and $existing.Description -ne $description) { throw 'An unrelated task already uses the FormosaLink name.' }
foreach ($path in @($dataRoot,$codeRoot)) { New-Item -ItemType Directory -Path $path -Force | Out-Null }
# State is private. Code and venv are read-only to the unprivileged service account.
& icacls.exe $dataRoot /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F' '*S-1-5-19:(OI)(CI)M' | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'State ACL setup failed.' }
& $basePython -m venv $venvRoot
if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
$pythonExe = Join-Path $venvRoot 'Scripts\python.exe'
& $pythonExe -m pip install --disable-pip-version-check -r (Join-Path $source 'formosalink\requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
function Read-FormosaSecret {
  param([string]$Language)
  Add-Type -AssemblyName System.Windows.Forms
  Add-Type -AssemblyName System.Drawing
  $labels = @{
    'zh-TW' = @('請先在 GitHub 複製完整 Client Secret，再按「貼上 Secret」。','貼上 Secret','確認','取消','已輸入字元：')
    'en' = @('Copy the full Client Secret from GitHub, then click Paste Secret.','Paste Secret','Confirm','Cancel','Characters entered: ')
    'ja' = @('GitHub で完全な Client Secret をコピーし、貼り付けボタンを押してください。','Secret を貼り付け','確認','キャンセル','入力文字数：')
  }
  $words = $labels[$Language]
  $form = New-Object Windows.Forms.Form
  $form.Text = 'FormosaLink - GitHub Client Secret'
  $form.ClientSize = New-Object Drawing.Size(540,210)
  $form.StartPosition = 'CenterScreen'
  $form.FormBorderStyle = 'FixedDialog'
  $form.MaximizeBox = $false
  $form.MinimizeBox = $false
  $form.TopMost = $true
  $description = New-Object Windows.Forms.Label
  $description.Text = $words[0]
  $description.Location = New-Object Drawing.Point(16,16)
  $description.Size = New-Object Drawing.Size(505,42)
  $secretBox = New-Object Windows.Forms.TextBox
  $secretBox.Location = New-Object Drawing.Point(16,68)
  $secretBox.Size = New-Object Drawing.Size(505,28)
  $secretBox.UseSystemPasswordChar = $true
  $secretBox.ShortcutsEnabled = $true
  $secretBox.MaxLength = 512
  $status = New-Object Windows.Forms.Label
  $status.Location = New-Object Drawing.Point(16,106)
  $status.Size = New-Object Drawing.Size(505,25)
  $status.Text = $words[4] + '0'
  $pasteButton = New-Object Windows.Forms.Button
  $pasteButton.Text = $words[1]
  $pasteButton.Location = New-Object Drawing.Point(16,155)
  $pasteButton.Size = New-Object Drawing.Size(160,36)
  $pasteButton.Add_Click({
    if ([Windows.Forms.Clipboard]::ContainsText()) { $secretBox.Text = [Windows.Forms.Clipboard]::GetText().Trim(); $secretBox.Focus() }
  }.GetNewClosure())
  $confirmButton = New-Object Windows.Forms.Button
  $confirmButton.Text = $words[2]
  $confirmButton.Location = New-Object Drawing.Point(305,155)
  $confirmButton.Size = New-Object Drawing.Size(100,36)
  $confirmButton.DialogResult = [Windows.Forms.DialogResult]::OK
  $confirmButton.Enabled = $false
  $secretBox.Add_TextChanged({ $status.Text = $words[4] + $secretBox.TextLength; $confirmButton.Enabled = $secretBox.TextLength -ge 20 }.GetNewClosure())
  $cancelButton = New-Object Windows.Forms.Button
  $cancelButton.Text = $words[3]
  $cancelButton.Location = New-Object Drawing.Point(420,155)
  $cancelButton.Size = New-Object Drawing.Size(100,36)
  $cancelButton.DialogResult = [Windows.Forms.DialogResult]::Cancel
  $form.AcceptButton = $confirmButton
  $form.CancelButton = $cancelButton
  $form.Controls.AddRange(@($description,$secretBox,$status,$pasteButton,$confirmButton,$cancelButton))
  try {
    if ($form.ShowDialog() -ne [Windows.Forms.DialogResult]::OK) { throw 'OAuth configuration cancelled; backend remains available.' }
    return ConvertTo-SecureString -String $secretBox.Text.Trim() -AsPlainText -Force
  }
  finally { $secretBox.Clear(); $form.Dispose() }
}
# Use PowerShell's native secure input: Python msvcrt/getpass can lose pasted text on older consoles.
# Configure before stopping the service, and transmit only through stdin (not arguments or temporary files).
if ($ConfigureGitHub) {
  Push-Location -LiteralPath $source
  try {
    $githubClientId = Read-Host 'GitHub Client ID'
    $githubSecureSecret = Read-FormosaSecret -Language $Language
    $githubBstr = [IntPtr]::Zero
    try {
      $githubBstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($githubSecureSecret)
      $githubSecretPlain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($githubBstr)
      $githubPayload = @{client_id=$githubClientId.Trim();client_secret=$githubSecretPlain.Trim()} | ConvertTo-Json -Compress
      $githubPayload | & $pythonExe -m formosalink.server.oauth --data-dir $dataRoot --lang $Language --stdin
      $githubExitCode = $LASTEXITCODE
    }
    finally {
      if ($githubBstr -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($githubBstr) }
      $githubSecretPlain = $null
      $githubPayload = $null
      if ($githubSecureSecret) { $githubSecureSecret.Dispose() }
    }
    if ($githubExitCode -ne 0) {
      if ($existing -and $existing.State -ne 'Running') { Start-ScheduledTask -TaskName $taskName }
      throw 'GitHub OAuth configuration failed; existing backend preserved. Existing credentials are unchanged.'
    }
  }
  finally { Pop-Location }
}
if ($existing) { Stop-ScheduledTask -TaskName $taskName; Start-Sleep -Seconds 2 }
# A venv launcher may leave its child interpreter alive after a task stop.
# Only terminate listeners whose command and executable identify this service.
$listeners = @(Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique)
foreach ($processId in $listeners) {
  $running = Get-CimInstance Win32_Process -Filter "ProcessId=$processId"
  $allowedExecutables = @([IO.Path]::GetFullPath($pythonExe),[IO.Path]::GetFullPath($basePython))
  if (-not $running -or $running.CommandLine -notmatch '\-m\s+formosalink\.server\b' -or $running.CommandLine -notmatch [regex]::Escape($dataRoot) -or $running.ExecutablePath -notin $allowedExecutables) {
    throw 'Port 8765 is held by an unidentified process; refusing to stop it.'
  }
  Stop-Process -Id $processId -Force
}
if ($listeners.Count) { Start-Sleep -Seconds 1 }
$sourcePrefix = $source.TrimEnd('\') + '\'
Get-ChildItem -LiteralPath $source -Recurse -File | ForEach-Object {
  $relative = $_.FullName.Substring($sourcePrefix.Length)
  $destination = Join-Path $codeRoot $relative
  New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($destination)) -Force | Out-Null
  Copy-Item -LiteralPath $_.FullName -Destination $destination -Force
  if ((Get-FileHash -LiteralPath $_.FullName).Hash -ne (Get-FileHash -LiteralPath $destination).Hash) { throw "Runtime copy verification failed: $relative" }
}
foreach ($path in @($codeRoot,$venvRoot)) {
  & icacls.exe $path /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F' '*S-1-5-19:(OI)(CI)RX' | Out-Null
  if ($LASTEXITCODE -ne 0) { throw 'Service code ACL setup failed.' }
}
Push-Location -LiteralPath $codeRoot
try {
  if (-not (Test-Path -LiteralPath (Join-Path $dataRoot 'config.json'))) {
    Write-Output $text.initialize
    & $pythonExe -m formosalink.server.config --data-dir $dataRoot --origin $Origin --lang $Language
    if ($LASTEXITCODE -ne 0) { throw 'Owner initialization did not complete.' }
  }
  & $pythonExe -c "import sys; from formosalink.server.config import load; assert load(sys.argv[1])[1]['origin'] == sys.argv[2].rstrip('/')" $dataRoot $Origin
  if ($LASTEXITCODE -ne 0) { throw 'Existing server origin differs; refusing to replace credentials.' }
}
finally { Pop-Location }
$taskAction = New-ScheduledTaskAction -Execute $pythonExe -Argument ('-m formosalink.server --data-dir "'+$dataRoot+'" --log-file "'+(Join-Path $dataRoot 'server.log')+'"') -WorkingDirectory $codeRoot
$taskPrincipal = New-ScheduledTaskPrincipal -UserId 'S-1-5-19' -LogonType ServiceAccount -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 20 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Description $description -Action $taskAction -Trigger (New-ScheduledTaskTrigger -AtStartup) -Principal $taskPrincipal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
$hostHeader = ([Uri]$Origin).Authority
for ($attempt=0; $attempt -lt 20; $attempt++) {
  try {
    $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8765/api/v1/health' -Headers @{Host=$hostHeader} -TimeoutSec 2
    if ($health.service -eq 'FormosaLink' -and $health.features -contains 'live-camera-stream-v1' -and $health.features -contains 'carrot-web-v1' -and $health.database_version -eq 3) { Write-Output $text.ready; return }
  } catch { }
  Start-Sleep -Seconds 1
}
throw $text.failed
