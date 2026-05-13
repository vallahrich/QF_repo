param(
    [string]$AdminUser = 'azureuser',
    [int]$HelperLabelsPerRun = 2
)

$ErrorActionPreference = 'Stop'
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $BundleDir '..\..')
$QfRoot = Resolve-Path (Join-Path $RepoRoot '..')
$Python = Join-Path $QfRoot '.venv\Scripts\python.exe'
$LogDir = Join-Path $BundleDir 'monitor_logs'
$LogPath = Join-Path $LogDir 'post_phase8_handoff.log'
$StatePath = Join-Path $LogDir 'post_phase8_handoff_state.json'
$LatestPath = Join-Path $LogDir 'latest.md'
$MonitorPy = Join-Path $BundleDir 'monitor_recover.py'
$SyncScript = Join-Path $BundleDir 'Sync-Results.ps1'

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message)
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    $line = "[$stamp] $Message"
    Add-Content -Path $LogPath -Value $line -Encoding UTF8
    Write-Host $line
}

function Read-State {
    if (-not (Test-Path $StatePath)) {
        return $null
    }
    try {
        return Get-Content $StatePath -Raw | ConvertFrom-Json
    }
    catch {
        return $null
    }
}

function Write-State {
    param(
        [string]$Status,
        [hashtable]$Extra = @{}
    )
    $state = @{
        status = $Status
        updated_utc = (Get-Date).ToUniversalTime().ToString('o')
    }
    foreach ($key in $Extra.Keys) {
        $state[$key] = $Extra[$key]
    }
    $state | ConvertTo-Json -Depth 8 | Set-Content -Path $StatePath -Encoding UTF8
}

function Invoke-NativeLogged {
    param(
        [string]$Name,
        [scriptblock]$Command
    )
    Write-Log "start $Name"
    $output = & $Command 2>&1
    $exitCode = $LASTEXITCODE
    foreach ($line in $output) {
        Write-Log "${Name}: $line"
    }
    if ($null -eq $exitCode) {
        $exitCode = 0
    }
    Write-Log "$Name exit=$exitCode"
    if ($exitCode -ne 0) {
        throw "$Name failed with exit code $exitCode"
    }
}

if (-not (Test-Path $Python)) {
    throw "Python not found: $Python"
}

$state = Read-State
if ($null -ne $state -and $state.status -in @('started', 'phase8b_complete')) {
    Write-Log "handoff already $($state.status); exiting"
    return
}

try {
    Write-Log 'checking Phase 8 readiness via monitor_recover.py'
    $monitorOutput = & $Python $MonitorPy --admin-user $AdminUser --recover --helpers --helper-labels-per-run $HelperLabelsPerRun 2>&1
    $monitorExit = $LASTEXITCODE
    foreach ($line in $monitorOutput) {
        Write-Log "monitor: $line"
    }
    if ($monitorExit -ne 0) {
        throw "monitor_recover.py failed with exit code $monitorExit"
    }

    if (-not (Test-Path $LatestPath)) {
        throw "latest monitor snapshot not found: $LatestPath"
    }
    $latest = Get-Content $LatestPath -Raw
    if ($latest -notmatch 'Total: `(?<done>\d+)/(?<expected>\d+)` results') {
        throw 'could not parse Phase 8 total from latest.md'
    }
    $done = [int]$Matches.done
    $expected = [int]$Matches.expected
    if ($done -lt $expected) {
        Write-Log "Phase 8 not ready: $done/$expected"
        Write-State 'waiting' @{ done = $done; expected = $expected }
        return
    }

    Write-Log "Phase 8 ready: $done/$expected"
    Write-State 'started' @{ done = $done; expected = $expected; started_utc = (Get-Date).ToUniversalTime().ToString('o') }

    Invoke-NativeLogged 'sync_phase8_results' { & $SyncScript -AdminUser $AdminUser -CleanDestination }

    Push-Location $RepoRoot
    try {
        Invoke-NativeLogged 'audit_phase8' { & $Python -m p4_experiments.canonical.audit_phase8 }
        Invoke-NativeLogged 'phase8b_classical_baselines' { & $Python -m p4_experiments.canonical.phase8b_classical_baselines --skip-existing }
        Invoke-NativeLogged 'phase8b_update_cohort' { & $Python -m p4_experiments.canonical.phase8b_update_cohort }
    }
    finally {
        Pop-Location
    }

    Write-State 'phase8b_complete' @{ completed_utc = (Get-Date).ToUniversalTime().ToString('o') }
    Write-Log 'post-Phase-8 handoff complete through phase8b_cohort'
}
catch {
    Write-State 'failed' @{ error = $_.Exception.Message }
    Write-Log "FAILED: $($_.Exception.Message)"
    throw
}