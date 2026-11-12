param([string]$DataDirectory = 'C:\ProgramData\FormosaLink')
$ErrorActionPreference = 'Stop'
# setup-server.ps1 installs a private runtime copy outside the IIS website.
# The gateway reads this one asset per request, so no service restart is needed.
$siteRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'formosalink-deployment.json') -Raw | ConvertFrom-Json
if ($manifest.product -ne 'FormosaLink') { throw 'Unexpected deployment marker.' }
$dataRoot = [IO.Path]::GetFullPath($DataDirectory).TrimEnd('\')
if ($dataRoot.StartsWith('\\') -or $dataRoot.Equals($siteRoot,[StringComparison]::OrdinalIgnoreCase) -or $dataRoot.StartsWith($siteRoot+'\',[StringComparison]::OrdinalIgnoreCase)) {
  throw 'Use the installed local data directory outside the IIS website.'
}
$codeRoot = $dataRoot + '-code'
$source = Join-Path $PSScriptRoot 'server-package\formosalink\web\carrot-bridge.js'
$target = [IO.Path]::GetFullPath((Join-Path $codeRoot 'formosalink\web\carrot-bridge.js'))
if (-not $target.StartsWith($codeRoot+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Invalid runtime target.' }
if (-not (Test-Path -LiteralPath $source -PathType Leaf) -or -not (Test-Path -LiteralPath $target -PathType Leaf)) {
  throw 'Installed bridge not found; run this on the IIS host with its original DataDirectory.'
}
if ((Get-FileHash -LiteralPath $source).Hash -eq (Get-FileHash -LiteralPath $target).Hash) {
  Write-Output 'Bridge is already current; no restart needed.'
  return
}
$backup = $target + '.before-' + [DateTime]::UtcNow.Ticks
Copy-Item -LiteralPath $target -Destination $backup
Copy-Item -LiteralPath $source -Destination $target -Force
if ((Get-FileHash -LiteralPath $source).Hash -ne (Get-FileHash -LiteralPath $target).Hash) { throw 'Runtime bridge hash mismatch.' }
Write-Output 'Runtime bridge updated and hash verified; no restart or account/pairing/settings changes.'
