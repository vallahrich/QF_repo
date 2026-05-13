$ErrorActionPreference = 'Stop'

$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Manifest = Get-Content (Join-Path $BundleDir 'manifest.json') -Raw | ConvertFrom-Json

foreach ($vm in $Manifest.vms) {
    Write-Host "Starting $($vm.name) in $($vm.resourceGroup)" -ForegroundColor Cyan
    az vm start --resource-group $vm.resourceGroup --name $vm.name --no-wait | Out-Null
}

Write-Host 'Start requests submitted. Use Check-Setup.ps1 or az vm list -d to confirm running state.' -ForegroundColor Green
