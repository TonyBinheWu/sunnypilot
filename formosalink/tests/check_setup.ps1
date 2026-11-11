param([Parameter(Mandatory=$true)][string]$ScriptPath)
$tokens = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile($ScriptPath,[ref]$tokens,[ref]$errors) | Out-Null
if ($errors.Count) { $errors | ForEach-Object { Write-Output $_.Message }; exit 1 }
Write-Output ('PowerShell ' + $PSVersionTable.PSVersion + ': setup script parse OK')
