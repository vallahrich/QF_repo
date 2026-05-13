param(
    [string]$TaskName = 'QF Phase8d Deepcare Auto Helpers',
    [int]$IntervalMinutes = 5,
    [int]$DurationDays = 3,
    [int]$TimeoutSeconds = 36000,
    [int]$MaxCellsPerHelper = 5,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AutoScript = Join-Path $BundleDir 'Auto-DeepcareHelpers.ps1'

if (-not (Test-Path $AutoScript)) {
    throw "Auto helper script not found: $AutoScript"
}

$taskArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$AutoScript`" -TimeoutSeconds $TimeoutSeconds -MaxCellsPerHelper $MaxCellsPerHelper"
if ($DryRun) {
    $taskArgs += ' -DryRun'
}

$Action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $taskArgs
$Trigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) `
    -RepetitionDuration (New-TimeSpan -Days $DurationDays)
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Activates newly idle Deepcare FX4 VMs as Phase 8d helper lanes every $IntervalMinutes minutes." `
    -Force | Out-Host

Write-Host "Registered $IntervalMinutes-minute Deepcare auto-helper task: $TaskName" -ForegroundColor Green
Write-Host "Latest state: $(Join-Path $BundleDir 'monitor_logs\deepcare_auto_helpers_latest.json')" -ForegroundColor Cyan