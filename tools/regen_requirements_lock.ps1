# Phase 7 - Regenerate the canonical pinned lockfile.
#
# Captures the active interpreter's full transitive package graph into
# p4_experiments/canonical/requirements.lock. Edit p4_experiments/canonical/
# requirements.in (direct deps) before running this if you need to add or
# remove a package.
#
# Usage (from repo root):
#   pwsh -File tools/regen_requirements_lock.ps1
#
# Optional:
#   -Python <path>    Use a specific interpreter.

param(
    [string]$Python = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$lockfile = Join-Path $repoRoot "p4_experiments\canonical\requirements.lock"

if (-not $Python) {
    $workspaceRoot = Split-Path -Parent $repoRoot
    $venvPython = Join-Path $workspaceRoot ".venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        $Python = $venvPython
    } else {
        $Python = "python"
    }
}

if ($Python -ne "python" -and -not (Test-Path $Python)) {
    throw "Python interpreter not found: $Python"
}

Write-Host "[regen] Using interpreter: $Python"
& $Python --version

$tempLock = New-TemporaryFile
& $Python -m pip freeze | Out-File -Encoding utf8 $tempLock.FullName

$header = @(
    "# Phase 7 - Canonical environment lockfile"
    "# Generated UTC: " + (Get-Date -AsUTC -Format o)
    "# Python: " + (& $Python --version)
    "# Source: pip freeze on " + $Python
    "# Reproduce with:"
    "#   python -m venv .canonical-venv"
    "#   .canonical-venv/Scripts/python -m pip install -r requirements.lock"
    "# All transitive dependencies are pinned. Do NOT edit by hand;"
    "# regenerate via tools/regen_requirements_lock.ps1."
    ""
)

$body = Get-Content -Raw -Encoding UTF8 $tempLock.FullName
$body = $body -replace "^\xEF\xBB\xBF", ""

$out = ($header -join "`n") + "`n" + $body
[System.IO.File]::WriteAllText($lockfile, $out, [System.Text.UTF8Encoding]::new($false))

Remove-Item $tempLock.FullName

$lineCount = (Get-Content $lockfile | Measure-Object -Line).Lines
Write-Host "[regen] Wrote $lockfile ($lineCount lines)"
