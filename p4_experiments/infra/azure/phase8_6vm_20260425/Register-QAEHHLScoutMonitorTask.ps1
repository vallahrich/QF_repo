param(
    [string]$TaskName = 'QF Phase8d QAE-HHL Scout Monitor',
    [ValidateSet('any', 'canary', 'floquet', 'surface', 'all')]
    [string]$Plan = 'any',
    [string]$VmNames = 'qf-p8-vm1,qf-p8-vm2,qf-p8-vm3',
    [int]$IntervalMinutes = 30,
    [int]$DurationDays = 14
)

$ErrorActionPreference = 'Stop'
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$MonitorScript = Join-Path $BundleDir 'Monitor-QAEHHLScout.ps1'

if (-not (Test-Path $MonitorScript)) {
    throw "Monitor script not found: $MonitorScript"
}

$taskArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$MonitorScript`" -Plan $Plan -VmNames `"$VmNames`""
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
    -Description "Checks Phase 8d QAE/HHL scout status every $IntervalMinutes minutes on selected VMs." `
    -Force | Out-Host

Write-Host "Registered $IntervalMinutes-minute QAE/HHL scout monitor task: $TaskName" -ForegroundColor Green
Write-Host "Latest status will be written to: $(Join-Path $BundleDir 'monitor_logs\qae_hhl_scout_latest.md')" -ForegroundColor Cyan
