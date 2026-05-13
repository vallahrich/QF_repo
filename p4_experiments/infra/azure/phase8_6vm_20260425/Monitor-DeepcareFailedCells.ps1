param(
    [string]$AdminUser = 'azureuser',
    [int]$TailLines = 12
)

$ErrorActionPreference = 'Continue'
$SshOptions = @('-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=20')
$SshCommandOptions = @('-n') + $SshOptions

$Vms = @(
    [pscustomobject]@{ name = 'qf-dc-fx4-wus2'; ip = '40.65.93.57'; location = 'westus2' },
    [pscustomobject]@{ name = 'qf-dc-fx4-eus2'; ip = '20.242.33.50'; location = 'eastus2' },
    [pscustomobject]@{ name = 'qf-dc-fx4-weu'; ip = '20.105.248.87'; location = 'westeurope' },
    [pscustomobject]@{ name = 'qf-dc-fx4-neu'; ip = '52.138.253.127'; location = 'northeurope' },
    [pscustomobject]@{ name = 'qf-dc-fx4-frc'; ip = '20.216.131.43'; location = 'francecentral' },
    [pscustomobject]@{ name = 'qf-dc-fx4-gwc'; ip = '51.116.177.227'; location = 'germanywestcentral' },
    [pscustomobject]@{ name = 'qf-dc-fx4-sec'; ip = '20.91.136.252'; location = 'swedencentral' },
    [pscustomobject]@{ name = 'qf-dc-fx4-cus'; ip = '74.249.152.13'; location = 'centralus' }
)

foreach ($vm in $Vms) {
    $target = "$AdminUser@$($vm.ip)"
    Write-Host "--- $($vm.name) $($vm.location) ---" -ForegroundColor Cyan
    $remote = @'
RUN_ROOT="${PHASE8_RUN_ROOT:-$HOME/qf-phase8-20260425}"
REPO="$RUN_ROOT/quantum-finance"
RESULT_DIR="$REPO/p4_experiments/canonical/outputs/phase08d_qae_hhl_scout/results"
LOG_DIR="$RUN_ROOT/logs"
echo PROCESSES_BEGIN
pgrep -af '[p]hase8d_qae_hhl_scout' || true
pgrep -af '[r]un_failed_cells___VM_NAME__' || true
echo PROCESSES_END
echo "RESULT_COUNT=$(find "$RESULT_DIR" -maxdepth 1 -type f -name '*.json' 2>/dev/null | wc -l)"
echo LOG_BEGIN
tail -n __TAIL_LINES__ "$LOG_DIR/qae_hhl_failed___VM_NAME__.nohup.log" 2>/dev/null || true
echo LOG_END
'@
    $remote = $remote.Replace('__VM_NAME__', $vm.name).Replace('__TAIL_LINES__', $TailLines.ToString())
    $remote = $remote -replace "`r?`n", "`n"
    & ssh @SshCommandOptions $target $remote
}