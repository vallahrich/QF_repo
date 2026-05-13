param(
    [string]$AdminUser = 'azureuser'
)

$ErrorActionPreference = 'Continue'
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Manifest = Get-Content (Join-Path $BundleDir 'manifest.json') -Raw | ConvertFrom-Json
$SshOptions = @('-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=20')

foreach ($vm in $Manifest.vms) {
    $target = "$AdminUser@$($vm.publicIp)"
    Write-Host "`n--- $($vm.name) $($vm.location) expected=$($vm.expected_cells) ---" -ForegroundColor Cyan
    $remote = 'source ~/phase8_6vm.env 2>/dev/null || true; echo PROC=$(pgrep -fc phase8_big_run); echo UNIT_PROC=$(pgrep -fc "python.*run_unit"); echo RESULTS=$(ls ~/qf-phase8-20260425/quantum-finance/p4_experiments/common/output/results/*.json 2>/dev/null | wc -l); echo EXPECTED=${PHASE8_EXPECTED_CELLS:-unknown}; echo LOG_TAIL=; tail -n 25 ~/qf-phase8-20260425/logs/phase8_nohup.log 2>/dev/null || tail -n 25 ~/qf-phase8-20260425/logs/run_*.log 2>/dev/null || true'
    & ssh @SshOptions $target $remote
}
