param(
    [string]$AdminUser = 'azureuser',
    [ValidateSet('any', 'canary', 'floquet', 'surface', 'all')]
    [string]$Plan = 'any',
    [string]$VmNames = 'qf-p8-vm1,qf-p8-vm2,qf-p8-vm3',
    [int]$TailLines = 20
)

$ErrorActionPreference = 'Continue'
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $BundleDir '..\..')
$Manifest = Get-Content (Join-Path $BundleDir 'manifest.json') -Raw | ConvertFrom-Json
$SshOptions = @('-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=20')
$SshCommandOptions = @('-n') + $SshOptions
$LogDir = Join-Path $BundleDir 'monitor_logs'
$LatestPath = Join-Path $LogDir 'qae_hhl_scout_latest.md'
$HistoryPath = Join-Path $LogDir 'qae_hhl_scout_history.log'
$LocalResultDir = Join-Path $RepoRoot 'p4_experiments\canonical\outputs\phase08d_qae_hhl_scout\results'

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$selected = @()
$vmNameList = @($VmNames -split '[,;]' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
foreach ($name in $vmNameList) {
    $vm = $Manifest.vms | Where-Object { $_.name -eq $name } | Select-Object -First 1
    if ($null -eq $vm) {
        Write-Warning "VM not found in manifest: $name"
    } else {
        $selected += $vm
    }
}

$utc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$localCount = 0
if (Test-Path $LocalResultDir) {
    $localCount = @(Get-ChildItem -Path $LocalResultDir -File -Filter '*.json' -ErrorAction SilentlyContinue).Count
}

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# Phase 8d QAE/HHL Scout Monitor")
$lines.Add("")
$lines.Add("- UTC: $utc")
$lines.Add("- Plan: $Plan")
$lines.Add("- VMs: $($selected.name -join ', ')")
$lines.Add("- Local JSON results: $localCount")
$lines.Add("")

$azTable = (& az vm list -d --query "[?starts_with(name, 'qf-p8-vm')].{name:name,resourceGroup:resourceGroup,powerState:powerState,publicIp:publicIps}" -o table 2>&1) -join "`n"
$lines.Add("## Azure Power State")
$lines.Add("")
$lines.Add('```')
$lines.Add($azTable)
$lines.Add('```')
$lines.Add("")

$anyRunning = $false
foreach ($vm in $selected) {
    $target = "$AdminUser@$($vm.publicIp)"
    $remoteCommand = @'
PLAN="__PLAN__"
TAIL_LINES=__TAIL__
RUN_ROOT="${PHASE8_RUN_ROOT:-$HOME/qf-phase8-20260425}"
REPO="$RUN_ROOT/quantum-finance"
RESULT_DIR="$REPO/p4_experiments/canonical/outputs/phase08d_qae_hhl_scout/results"
LOG_DIR="$RUN_ROOT/logs"
echo "REMOTE_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo PROCESSES_BEGIN
pgrep -af '[p]4_experiments.canonical.phase8d_qae_hhl_scout|[r]un_qae_hhl_scout' || true
echo PROCESSES_END
echo "REMOTE_RESULT_COUNT=$(find "$RESULT_DIR" -maxdepth 1 -type f -name '*.json' 2>/dev/null | wc -l)"
echo LATEST_LOG_BEGIN
if [ "$PLAN" = "any" ]; then
    latest=$(find "$LOG_DIR" -maxdepth 1 -type f \( -name 'qae_hhl_scout_*.log' -o -name 'qae_hhl_scout_*.nohup.log' \) -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -n 1 | cut -d' ' -f2-)
else
    latest=$(find "$LOG_DIR" -maxdepth 1 -type f \( -name "qae_hhl_scout_${PLAN}_*.log" -o -name "qae_hhl_scout_${PLAN}_*.nohup.log" -o -name "qae_hhl_scout_overnight_${PLAN}_*.log" -o -name "qae_hhl_scout_overnight_${PLAN}_*.nohup.log" \) -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -n 1 | cut -d' ' -f2-)
fi
if [ -n "$latest" ]; then
    echo "LOG_FILE=$latest"
    tail -n "$TAIL_LINES" "$latest"
else
    echo NO_LOG
fi
echo LATEST_LOG_END
'@
        $remoteCommand = $remoteCommand.Replace('__PLAN__', $Plan).Replace('__TAIL__', $TailLines.ToString()) -replace "`r?`n", "`n"
    $output = (& ssh @SshCommandOptions $target $remoteCommand 2>&1) -join "`n"
    if ($output -match 'phase8d_qae_hhl_scout|run_qae_hhl_scout') {
        $anyRunning = $true
    }

    $lines.Add("## $($vm.name)")
    $lines.Add("")
    $lines.Add('```')
    $lines.Add($output)
    $lines.Add('```')
    $lines.Add("")
}

$status = if ($anyRunning) { 'running' } else { 'no-active-process' }
$lines.Add("## Summary")
$lines.Add("")
$lines.Add("- Scout process status: $status")
$lines.Add("- Checked at: $utc")

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText($LatestPath, ($lines -join "`r`n"), $utf8NoBom)
[System.IO.File]::AppendAllText($HistoryPath, "$utc`tplan=$Plan`tstatus=$status`tlocal_json=$localCount`tvm_count=$($selected.Count)`r`n", $utf8NoBom)

Write-Host "QAE/HHL scout monitor status=$status local_json=$localCount latest=$LatestPath" -ForegroundColor Green
