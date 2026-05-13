param(
    [string]$AdminUser = 'azureuser'
)

$ErrorActionPreference = 'Stop'
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Manifest = Get-Content (Join-Path $BundleDir 'manifest.json') -Raw | ConvertFrom-Json
$SshOptions = @('-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=20')
$SshCommandOptions = @('-n') + $SshOptions

foreach ($vm in $Manifest.vms) {
    $target = "$AdminUser@$($vm.publicIp)"
    Write-Host "--- Launching Phase 8 on $($vm.name) labels=$($vm.labels.Count) cells=$($vm.expected_cells) ---" -ForegroundColor Cyan
    $remote = 'test -f ~/qf-phase8-20260425/setup_complete.ok; nohup bash ~/qf-phase8-20260425/run_phase8.sh > ~/qf-phase8-20260425/logs/phase8_nohup.log 2>&1 < /dev/null & echo run_pid=$!'
    & ssh @SshCommandOptions $target $remote
    if ($LASTEXITCODE -ne 0) { throw "launch failed for $($vm.name)" }
}

Write-Host 'All Phase 8 runs launched. Use Probe-Runs.ps1 to monitor.' -ForegroundColor Green
