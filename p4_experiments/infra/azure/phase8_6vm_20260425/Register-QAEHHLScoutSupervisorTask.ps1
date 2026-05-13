param(
    [string]$TaskName = 'QF Phase8d QAE-HHL Scout Supervisor',
    [ValidateSet('all')]
    [string]$Plan = 'all',
    [string]$VmNames = 'qf-p8-vm1,qf-p8-vm2,qf-p8-vm3',
    [int]$TimeoutSeconds = 36000,
    [int]$CheckIntervalSeconds = 300,
    [int]$IntervalMinutes = 30,
    [int]$DurationDays = 14
)

$ErrorActionPreference = 'Stop'
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SupervisorScript = Join-Path $BundleDir 'Start-QAEHHLScoutSupervisor.ps1'

if (-not (Test-Path $SupervisorScript)) {
    throw "Supervisor script not found: $SupervisorScript"
}

$taskArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$SupervisorScript`" -Plan $Plan -VmNames `"$VmNames`" -TimeoutSeconds $TimeoutSeconds -CheckIntervalSeconds $CheckIntervalSeconds"
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
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Keeps Phase 8d QAE/HHL scout supervisors running every $IntervalMinutes minutes on selected VMs." `
    -Force | Out-Host

Write-Host "Registered $IntervalMinutes-minute QAE/HHL scout supervisor task: $TaskName" -ForegroundColor Green
Write-Host "Remote supervisors check their assigned shards every $CheckIntervalSeconds seconds." -ForegroundColor Cyan
