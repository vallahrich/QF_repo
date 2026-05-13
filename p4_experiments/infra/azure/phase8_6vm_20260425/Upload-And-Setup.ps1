param(
    [string]$AdminUser = 'azureuser',
    [switch]$SkipPackageBuild
)

$ErrorActionPreference = 'Stop'
$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Manifest = Get-Content (Join-Path $BundleDir 'manifest.json') -Raw | ConvertFrom-Json
$PackagePath = Join-Path $BundleDir 'qf_phase8_20260425.tar.gz'
$SetupScript = Join-Path $BundleDir 'setup_remote.sh'
$SshOptions = @('-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=20')
$SshCommandOptions = @('-n') + $SshOptions

if (-not $SkipPackageBuild) {
    & (Join-Path $BundleDir 'Build-Package.ps1')
}
if (-not (Test-Path $PackagePath)) {
    throw "Package not found: $PackagePath"
}

foreach ($vm in $Manifest.vms) {
    $target = "$AdminUser@$($vm.publicIp)"
    $envFile = Join-Path $BundleDir ("env\$($vm.name).env")
    Write-Host "--- Uploading to $($vm.name) $($vm.location) $($vm.publicIp) ---" -ForegroundColor Cyan
    & scp @SshOptions $PackagePath "${target}:~/qf_phase8_20260425.tar.gz"
    if ($LASTEXITCODE -ne 0) { throw "scp package failed for $($vm.name)" }
    & scp @SshOptions $SetupScript "${target}:~/setup_phase8_6vm_remote.sh"
    if ($LASTEXITCODE -ne 0) { throw "scp setup script failed for $($vm.name)" }
    & scp @SshOptions $envFile "${target}:~/phase8_6vm.env"
    if ($LASTEXITCODE -ne 0) { throw "scp env failed for $($vm.name)" }

    Write-Host "Starting background setup on $($vm.name)" -ForegroundColor Yellow
    $remote = 'chmod +x ~/setup_phase8_6vm_remote.sh; nohup bash ~/setup_phase8_6vm_remote.sh ~/phase8_6vm.env > ~/setup_phase8_6vm.log 2>&1 < /dev/null & echo setup_pid=$!'
    & ssh @SshCommandOptions $target $remote
    if ($LASTEXITCODE -ne 0) { throw "ssh setup launch failed for $($vm.name)" }
}

Write-Host 'All setup jobs launched. Run Check-Setup.ps1 until every VM reports setup_complete.' -ForegroundColor Green
