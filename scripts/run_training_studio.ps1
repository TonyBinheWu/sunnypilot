param(
  [string]$Distribution = 'Ubuntu-22.04',
  [ValidateRange(1024,65535)][int]$Port = 8890,
  [switch]$FetchModel,
  [switch]$Restart
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$receipt = Join-Path $projectRoot 'build/official-sim/workspace.json'
if (-not (Test-Path -LiteralPath $receipt)) { throw 'Missing isolated WSL workspace. Run scripts/run_sim.ps1 -Mode Setup first.' }
$workspace = (Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json).workspace
$source = (& wsl.exe -d $Distribution -- wslpath -a ($projectRoot.Replace('\','/'))).Trim()
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& wsl.exe -d $Distribution -- mkdir -p "$workspace/tools/training_studio" "$workspace/openpilot/sunnypilot/formosalink"
& wsl.exe -d $Distribution -- cp -r "$source/tools/training_studio/." "$workspace/tools/training_studio/"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
foreach ($file in @('training_protocol.py','identity.py','protocol.py','service_policy.py')) {
  & wsl.exe -d $Distribution -- cp "$source/openpilot/sunnypilot/formosalink/$file" "$workspace/openpilot/sunnypilot/formosalink/"
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
if ($FetchModel) {
  & wsl.exe -d $Distribution --cd $workspace -- build/official-sim/venv/bin/python -m tools.training_studio.engine fetch-model --root build/training-studio
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
# Keep wsl.exe alive for the server lifetime: its interop environment is required by
# the existing Windows TCP proxy used to reach the DGX from WSL NAT networking.
$launchArgs = @('-d', $Distribution, '--cd', $workspace, '--', 'env', 'STUDIO_FOREGROUND=1')
if ($Restart) { $launchArgs += 'STUDIO_RESTART=1' }
$launchArgs += @('bash', 'tools/training_studio/start.sh', 'build/training-studio', [string]$Port)
$launchId = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfff')
$previousWorker = $null
try { $previousWorker = (Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/state" -TimeoutSec 2).worker.pid } catch { }
$hostLog = Join-Path $projectRoot "build/training-studio-host-$launchId.log"
$hostError = Join-Path $projectRoot "build/training-studio-host-$launchId.err.log"
$launcher = Start-Process -FilePath 'wsl.exe' -ArgumentList $launchArgs -WindowStyle Hidden -PassThru -RedirectStandardOutput $hostLog -RedirectStandardError $hostError
for ($attempt = 0; $attempt -lt 80; $attempt++) {
  Start-Sleep -Milliseconds 500
  $launcher.Refresh()
  if ($launcher.HasExited -and $launcher.ExitCode -ne 0) {
    throw "Studio launcher failed. Inspect $hostLog and $hostError"
  }
  try {
    $ready = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/state" -TimeoutSec 2
    if ($ready.worker.fresh -and (!$Restart -or $ready.worker.pid -ne $previousWorker)) {
      Write-Host "Training Studio ready: http://127.0.0.1:$Port"
      exit 0
    }
  } catch { }
}
throw "Studio startup timed out. Inspect $hostLog and $hostError"
