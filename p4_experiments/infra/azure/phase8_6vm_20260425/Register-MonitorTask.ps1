param(
    [string]$TaskName = 'QF Phase8 6VM Monitor'
)

$ErrorActionPreference = 'Stop'
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$MonitorScript = Join-Path $BundleDir 'Monitor-Recover.ps1'
$Action = New-ScheduledTaskAction `
    -Execute 'powershell.exe' `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$MonitorScript`" -Recover -Helpers"
$Trigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 10) `
    -RepetitionDuration (New-TimeSpan -Days 30)
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 8)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description 'Checks six Phase 8 Azure VM shards every 10 minutes and relaunches stopped incomplete shards.' `
    -Force | Out-Host
Write-Host "Registered 10-minute monitor task: $TaskName" -ForegroundColor Green
Write-Host "Latest status will be written to: $(Join-Path $BundleDir 'monitor_logs\latest.md')" -ForegroundColor Cyan