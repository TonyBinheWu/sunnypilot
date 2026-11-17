param(
  [string]$DataDirectory = 'C:\ProgramData\FormosaLink',
  [string]$Origin = 'https://formosapilot.dinglu-t.com',
  [string]$Python = ''
)
$ErrorActionPreference = 'Stop'
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
  throw 'Run this script in an administrator PowerShell on the IIS server. SMB file access cannot update its private backend or restart its service.'
}
$dataRoot = [IO.Path]::GetFullPath($DataDirectory).TrimEnd('\')
$siteRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..')).TrimEnd('\')
if ($dataRoot.StartsWith('\\') -or $dataRoot.Equals($siteRoot,[StringComparison]::OrdinalIgnoreCase) -or $dataRoot.StartsWith($siteRoot+'\',[StringComparison]::OrdinalIgnoreCase)) {
  throw 'Training data and worker registration must stay on a private local disk outside the website.'
}
$registration = Join-Path $PSScriptRoot 'training-worker-registration.json'
if (-not (Test-Path -LiteralPath $registration)) { throw 'Missing training-worker public-key registration.' }
$incoming = Get-Content -LiteralPath $registration -Raw | ConvertFrom-Json
$workersPath = Join-Path $dataRoot 'training-workers.json'
$workers = @{}
if (Test-Path -LiteralPath $workersPath) {
  $existing = Get-Content -LiteralPath $workersPath -Raw | ConvertFrom-Json
  foreach ($property in $existing.PSObject.Properties) { $workers[$property.Name] = $property.Value }
}
foreach ($property in $incoming.PSObject.Properties) {
  [void][Guid]::Parse($property.Name)
  if ([Convert]::FromBase64String($property.Value).Length -ne 32) { throw 'Invalid Ed25519 worker public key.' }
  if ($workers.ContainsKey($property.Name) -and $workers[$property.Name] -ne $property.Value) { throw 'Existing worker key differs; inspect before replacing.' }
  $workers[$property.Name] = $property.Value
}
if (-not (Test-Path -LiteralPath $dataRoot)) { throw 'Existing FormosaLink private data directory required.' }
$temporary = Join-Path $dataRoot 'training-workers.json.pending'
$workers | ConvertTo-Json | Set-Content -LiteralPath $temporary -Encoding UTF8
Move-Item -LiteralPath $temporary -Destination $workersPath -Force
$arguments = @{ DataDirectory = $dataRoot; Origin = $Origin }
if ($Python) { $arguments.Python = $Python }
& (Join-Path $PSScriptRoot 'setup-server.ps1') @arguments
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw 'FormosaLink backend update failed.' }
Write-Output 'Training collection backend and scoped worker key installed. Vehicle uploads still require each owner to opt in.'
