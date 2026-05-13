param(
    [string]$AdminUser = 'azureuser'
)

$ErrorActionPreference = 'Continue'
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Manifest = Get-Content (Join-Path $BundleDir 'manifest.json') -Raw | ConvertFrom-Json
$SshOptions = @('-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=20')

Write-Host 'Azure VM state' -ForegroundColor Cyan
az vm list -d --query '[].{name:name,resourceGroup:resourceGroup,location:location,powerState:powerState,size:hardwareProfile.vmSize,os:storageProfile.osDisk.osType,publicIp:publicIps}' -o table

foreach ($vm in $Manifest.vms) {
    $target = "$AdminUser@$($vm.publicIp)"
    Write-Host "`n--- $($vm.name) $($vm.location) $($vm.publicIp) ---" -ForegroundColor Cyan
    $remote = 'echo HOST=$(hostname); echo KERNEL=$(uname -srmo); echo CPU=$(nproc); grep MemTotal /proc/meminfo | sed "s/^/MEM_/"; if [ -f ~/qf-phase8-20260425/setup_status.txt ]; then echo STATUS=$(cat ~/qf-phase8-20260425/setup_status.txt); else echo STATUS=missing; fi; if [ -f ~/qf-phase8-20260425/setup_summary.json ]; then cat ~/qf-phase8-20260425/setup_summary.json; else echo LOG_TAIL=; tail -n 40 ~/setup_phase8_6vm.log 2>/dev/null || true; fi'
    & ssh @SshOptions $target $remote
}
