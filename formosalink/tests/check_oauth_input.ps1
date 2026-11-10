param([Parameter(Mandatory=$true)][string]$Python)
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$setup = Get-Content -LiteralPath (Join-Path $repo 'formosalink\deploy\setup-server.ps1') -Raw -Encoding UTF8
$start = $setup.IndexOf('# Use PowerShell')
$end = $setup.IndexOf('if ($existing) { Stop-ScheduledTask', $start)
if ($start -lt 0 -or $end -lt 0) { throw 'Secure configuration block missing.' }
$ConfigureGitHub = $true
$source = $repo
$dataRoot = Join-Path $repo ('build\oauth-powershell-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $dataRoot | Out-Null
$pythonExe = [IO.Path]::GetFullPath($Python)
$Language = 'en'
$existing = $null
function Read-FormosaSecret {
  param([string]$Language)
  return ConvertTo-SecureString -String 'test-only-opaque-secret+1234567890' -AsPlainText -Force
}
# Test-only credentials. Exercise the actual installer block and real Python stdin,
# replacing only the interactive console input so CI cannot wait for a password.
function Read-Host {
  param([string]$Prompt,[switch]$AsSecureString)
  if ($AsSecureString) { return ConvertTo-SecureString -String 'test-only-opaque-secret+1234567890' -AsPlainText -Force }
  return 'test-client-id'
}
& ([ScriptBlock]::Create($setup.Substring($start,$end-$start)))
$saved = Get-Content -LiteralPath (Join-Path $dataRoot 'github.json') -Raw | ConvertFrom-Json
if ($saved.client_id -ne 'test-client-id' -or $saved.client_secret -ne 'test-only-opaque-secret+1234567890') { throw 'Secure stdin configuration did not round trip.' }
Write-Output ('PowerShell ' + $PSVersionTable.PSVersion + ': native secure input / Python stdin round trip OK')
