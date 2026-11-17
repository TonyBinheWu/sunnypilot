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
if ($Restart) {
  & wsl.exe -d $Distribution --cd $workspace -- env STUDIO_RESTART=1 bash tools/training_studio/start.sh build/training-studio $Port
} else {
  & wsl.exe -d $Distribution --cd $workspace -- bash tools/training_studio/start.sh build/training-studio $Port
}
exit $LASTEXITCODE
