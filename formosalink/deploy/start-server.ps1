param(
  [Parameter(Mandatory = $true)][string]$DataDirectory,
  [string]$Python = 'python',
  [int]$Port = 8765
)
$ErrorActionPreference = 'Stop'
$serverPackage = Join-Path $PSScriptRoot 'server-package'
if (-not (Test-Path -LiteralPath $serverPackage)) { throw 'Missing server-package; run publish-iis.ps1 first.' }
$siteRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..')).TrimEnd('\')
$dataRoot = [IO.Path]::GetFullPath($DataDirectory).TrimEnd('\')
if ($dataRoot.Equals($siteRoot, [StringComparison]::OrdinalIgnoreCase) -or $dataRoot.StartsWith($siteRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
  throw 'Runtime data must be outside the IIS website directory.'
}
Push-Location -LiteralPath $serverPackage
try { & $Python -m formosalink.server --data-dir $dataRoot --port $Port; if ($LASTEXITCODE -ne 0) { throw 'FormosaLink server exited unsuccessfully.' } }
finally { Pop-Location }
