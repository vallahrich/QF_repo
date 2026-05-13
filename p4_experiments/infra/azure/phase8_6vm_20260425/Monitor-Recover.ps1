param(
    [string]$AdminUser = 'azureuser',
    [switch]$Recover,
    [switch]$Helpers,
    [int]$HelperLabelsPerRun = 2
)

$ErrorActionPreference = 'Stop'
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$QfRoot = Resolve-Path (Join-Path $BundleDir '..\..\..')
$Python = Join-Path $QfRoot '.venv\Scripts\python.exe'
$Monitor = Join-Path $BundleDir 'monitor_recover.py'

if (-not (Test-Path $Python)) {
    throw "Python not found: $Python"
}

$ArgsList = @($Monitor, '--admin-user', $AdminUser)
if ($Recover) {
    $ArgsList += '--recover'
}
if ($Helpers) {
    $ArgsList += '--helpers'
    $ArgsList += '--helper-labels-per-run'
    $ArgsList += $HelperLabelsPerRun.ToString()
}

& $Python @ArgsList