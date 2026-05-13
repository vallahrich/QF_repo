param(
    [string]$TaskName = 'QF Phase8 6VM Monitor'
)

$ErrorActionPreference = 'Continue'
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false | Out-Host