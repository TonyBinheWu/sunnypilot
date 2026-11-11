param(
  [string]$Destination = '\\192.168.20.145\htdocs\FormosaPilot',
  [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$webSource = Join-Path $repoRoot 'formosalink\web'
$destinationRoot = [IO.Path]::GetFullPath($Destination)
if (-not (Test-Path -LiteralPath $destinationRoot -PathType Container)) { throw "Destination must already exist: $destinationRoot" }
$files = @{}
Get-ChildItem -LiteralPath $webSource -Recurse -File | ForEach-Object {
  $relative = $_.FullName.Substring($webSource.Length).TrimStart('\')
  $files[$relative] = $_.FullName
}
$files.Remove('package.json')
$files['web.config'] = Join-Path $repoRoot 'formosalink\deploy\web.config'
$files['App_Data\start-server.ps1'] = Join-Path $repoRoot 'formosalink\deploy\start-server.ps1'
$files['App_Data\setup-server.ps1'] = Join-Path $repoRoot 'formosalink\deploy\setup-server.ps1'
$pythonPackage = Join-Path $repoRoot 'build\formosalink-python-3.14.10.zip'
if (Test-Path -LiteralPath $pythonPackage) { $files['App_Data\installers\python.3.14.10.nupkg'] = $pythonPackage }
$files['App_Data\README.md'] = Join-Path $repoRoot 'formosalink\README.md'
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'formosalink\docs') -Filter '*.md' -File | ForEach-Object {
  $files['App_Data\docs\' + $_.Name] = $_.FullName
}
$packagePrefix = 'App_Data\server-package\'
$files[$packagePrefix + 'formosalink\web\carrot-bridge.js'] = Join-Path $webSource 'carrot-bridge.js'
foreach ($relative in @('formosalink\__init__.py','formosalink\requirements.txt')) {
  $files[$packagePrefix + $relative] = Join-Path $repoRoot $relative
}
foreach ($sourceDir in @('formosalink\server','openpilot\sunnypilot\formosalink')) {
  $sourceRoot = Join-Path $repoRoot $sourceDir
  Get-ChildItem -LiteralPath $sourceRoot -Filter '*.py' -File | ForEach-Object {
    $files[$packagePrefix + $sourceDir + '\' + $_.Name] = $_.FullName
  }
}
# Refuse to replace an unrelated website. Subsequent deploys only touch our manifest-owned paths.
$marker = Join-Path $destinationRoot 'App_Data\formosalink-deployment.json'
$existing = @(Get-ChildItem -LiteralPath $destinationRoot -Force)
if ($existing.Count -gt 0 -and -not (Test-Path -LiteralPath $marker)) {
  throw 'Destination is not empty and has no FormosaLink deployment marker. Inspect it before deploying.'
}
foreach ($relative in $files.Keys) {
  $target = [IO.Path]::GetFullPath((Join-Path $destinationRoot $relative))
  if (-not $target.StartsWith($destinationRoot.TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Invalid destination path.' }
}
if ($CheckOnly) { Write-Output "Validated $($files.Count) deployment files for $destinationRoot"; return }
# Install IIS protection first; no credentials or runtime data are copied.
Copy-Item -LiteralPath $files['web.config'] -Destination (Join-Path $destinationRoot 'web.config') -Force
foreach ($relative in ($files.Keys | Sort-Object)) {
  $target = Join-Path $destinationRoot $relative
  New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($target)) -Force | Out-Null
  Copy-Item -LiteralPath $files[$relative] -Destination $target -Force
  if ((Get-FileHash -LiteralPath $target).Hash -ne (Get-FileHash -LiteralPath $files[$relative]).Hash) { throw "Hash mismatch: $relative" }
}
$manifest = @{ product = 'FormosaLink'; version = '0.8.0'; deployedAtUtc = [DateTime]::UtcNow.ToString('o'); files = @($files.Keys | Sort-Object) }
$manifest | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $marker -Encoding UTF8
Write-Output "Published and hash-verified $($files.Count) files to $destinationRoot. For a new installation, complete IIS and Python service setup."
