# pre_zip_check.ps1 — final hand-in readiness gate
#
# Runs all checks that must pass before zipping QF_repo for thesis submission.
# Read-only: makes no edits, deletes nothing. Exits non-zero on any blocker.
#
# Usage:
#   pwsh -NoProfile -ExecutionPolicy Bypass -File .\pre_zip_check.ps1
#
[CmdletBinding()]
param()
$ErrorActionPreference = "Continue"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

$blockers = @()
$warnings = @()

function Section($name) { Write-Host ""; Write-Host "=== $name ===" -ForegroundColor Cyan }
function Ok($msg)       { Write-Host "  [OK]    $msg" -ForegroundColor Green }
function Warn($msg)     { Write-Host "  [WARN]  $msg" -ForegroundColor Yellow; $script:warnings += $msg }
function Block($msg)    { Write-Host "  [BLOCK] $msg" -ForegroundColor Red;    $script:blockers += $msg }

# --- 1. Verifier suite ---
Section "1. verify.ps1 (v1-v9)"
& pwsh -NoProfile -ExecutionPolicy Bypass -File .\verify.ps1 *> $null
if ($LASTEXITCODE -eq 0) { Ok "All verifiers passed (v1-v9)" }
else { Block "verify.ps1 exited $LASTEXITCODE — rerun manually to inspect" }

# --- 2. Headline counts vs FREEZE ---
Section "2. Headline counts"
$counts = @{
    'p1 s1_extractions JSON'   = (Get-ChildItem p1_framework_synthesis\s1_extractions -Filter *.json -ErrorAction SilentlyContinue | Measure-Object).Count
    'p2 processed (md+json)'   = (Get-ChildItem p2_systematic_review\output\processed -ErrorAction SilentlyContinue | Measure-Object).Count
    'p2 processed *.md'        = (Get-ChildItem p2_systematic_review\output\processed -Filter *.md -ErrorAction SilentlyContinue | Measure-Object).Count
    'p3 s2 quantitative files' = (Get-ChildItem p3_thematic_synthesis\s2_quantitative\output -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
}
$counts.GetEnumerator() | ForEach-Object { Ok ("{0,-30} = {1}" -f $_.Key,$_.Value) }
if ($counts['p2 processed *.md'] -ne 777) { Warn "p2 processed *.md = $($counts['p2 processed *.md']); FREEZE expects 777 + paper_base.md template" }

# --- 3. Required artifacts present ---
Section "3. Required artifacts"
$required = @(
    'README.md','FREEZE.md','LICENSE','verify.ps1','pyproject.toml',
    'docs\SUBMISSION_TRUTH_MAP.md','docs\AUDIT_INDEX.md','docs\PIPELINE.md',
    'docs\ARCHITECTURE.md','docs\PROJECT_STATE.yaml','docs\PROJECT_TIMELINE.md',
    'p1_framework_synthesis\FREEZE.md','p2_systematic_review\FREEZE.md',
    'p3_thematic_synthesis\FREEZE.md','p4_experiments\FREEZE.md',
    'p4_experiments\canonical\cohort.json',
    'p4_experiments\canonical\release\zenodo_bundle.tar.gz',
    'p4_experiments\canonical\release\zenodo_bundle.tar.gz.sha256',
    'p3_thematic_synthesis\s3_quantum_advantage\combined\output\triangulation_matrix.filtered.json'
)
foreach ($p in $required) {
    if (Test-Path $p) { Ok $p } else { Block "missing: $p" }
}

# --- 4. Zenodo bundle hash matches sidecar ---
Section "4. Phase-11 release bundle integrity"
$tar  = 'p4_experiments\canonical\release\zenodo_bundle.tar.gz'
$side = 'p4_experiments\canonical\release\zenodo_bundle.tar.gz.sha256'
if ((Test-Path $tar) -and (Test-Path $side)) {
    $actual = (Get-FileHash -Algorithm SHA256 $tar).Hash.ToLower()
    $expected = (Get-Content $side -Raw).Trim().Split()[0].ToLower()
    if ($actual -eq $expected) { Ok "SHA-256 matches: $actual" }
    else { Block "SHA-256 MISMATCH  tar=$actual  sidecar=$expected" }
}

# --- 5. Credential / secret scan ---
Section "5. Secret scan"
$secretPatterns = @(
    'sk-[A-Za-z0-9]{32,}','AKIA[0-9A-Z]{16}','ghp_[A-Za-z0-9]{30,}','gho_[A-Za-z0-9]{30,}',
    'github_pat_[A-Za-z0-9_]{40,}','xox[pbar]-[A-Za-z0-9-]{20,}',
    '-----BEGIN [A-Z ]*PRIVATE KEY-----',
    'AccountKey=[A-Za-z0-9+/=]{40,}','DefaultEndpointsProtocol=https;AccountName=',
    'eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}'
)
$pattern = $secretPatterns -join '|'
$skipExt = @('.png','.jpg','.jpeg','.pdf','.gz','.zip','.tar','.pyc','.bin','.npy','.parquet','.whl','.exe','.dll','.so','.tgz','.7z','.ico','.svg','.woff','.woff2','.ttf','.eot')
$skipDir = '\\(\.venv|\.git|__pycache__|\.pytest_cache|node_modules|\.mypy_cache)\\'
$secretHits = Get-ChildItem -Recurse -File -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -lt 2MB -and $skipExt -notcontains $_.Extension.ToLower() -and $_.FullName -notmatch $skipDir -and $_.Name -ne 'pre_zip_check.ps1' } |
    Select-String -Pattern $pattern -List -ErrorAction SilentlyContinue
if (-not $secretHits) { Ok "0 credential patterns found" }
else { foreach ($h in $secretHits) { Block "secret-pattern hit: $($h.Path):$($h.LineNumber)" } }

# Check for stray .env (not .env.example)
$envFiles = Get-ChildItem -Recurse -Force -File -Include '.env','.env.local','.env.production' -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -notlike '*.example' }
if (-not $envFiles) { Ok "no live .env files" }
else { foreach ($f in $envFiles) { Block "live .env file present: $($f.FullName)" } }

# --- 6. Forbidden artifact types (PDFs, large media, source full-text dumps) ---
Section "6. Forbidden / unexpected artifact types"
$forbidden = Get-ChildItem -Recurse -File -Force -ErrorAction SilentlyContinue -Include '*.pdf','*.epub','*.docx','*.doc','*.pptx','*.ppt' |
    Where-Object { $_.FullName -notmatch $skipDir }
if (-not $forbidden) { Ok "no PDF/Office docs (IP-clean)" }
else { foreach ($f in $forbidden) { Warn "office/PDF doc present: $($f.FullName) ($([int]($f.Length/1KB)) KB)" } }

# --- 7. Dev caches that should not ship ---
Section "7. Dev caches and venvs"
$caches = Get-ChildItem -Recurse -Directory -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -in '.venv','venv','node_modules','__pycache__','.pytest_cache','.mypy_cache','.ipynb_checkpoints','.vs','.idea' }
if (-not $caches) { Ok "no dev caches" }
else {
    $caches | Group-Object Name | ForEach-Object {
        Warn ("{0}: {1} dirs (will inflate zip; consider removing)" -f $_.Name, $_.Count)
    }
}

# --- 8. .git presence (we expect NONE in the hand-in copy) ---
Section "8. .git directory"
if (Test-Path .git) { Warn ".git/ directory present (~$([int]((Get-ChildItem .git -Recurse -Force -File | Measure-Object -Sum Length).Sum/1MB)) MB) — typically excluded from hand-in zip" }
else { Ok "no .git/ (expected for detached hand-in copy)" }

# --- 9. Repo size & file count summary ---
Section "9. Repo size summary"
$all = Get-ChildItem -Recurse -File -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch $skipDir }
$totalMB = [math]::Round(($all | Measure-Object -Sum Length).Sum / 1MB, 1)
Ok ("$($all.Count) files, $totalMB MB (excluding caches/.git/.venv)")

# --- 10. Stale-doc banners present (sample check) ---
Section "10. Historical-status banners (sample)"
$bannerChecks = @{
    'p3_thematic_synthesis\docs\PRODUCTION_ARCHITECTURE.md'  = 'Status note \(2026-05-'
    'p3_thematic_synthesis\docs\B2_MANUSCRIPT_READINESS.md'  = 'Status note \(2026-05-'
    'p3_thematic_synthesis\docs\C2_DISPOSITION_LOG.md'       = 'Status note \(2026-05-'
    'p3_thematic_synthesis\docs\C2_GROUNDING_REPORT.md'      = 'Status note \(2026-05-'
    'p3_thematic_synthesis\docs\B1_B2_COALESCENCE_REPORT.md' = 'Status note \(2026-05-'
    'p3_thematic_synthesis\docs\THEME_CROSSWALK_SHORTLIST.md'= 'Status note \(2026-05-'
    'p4_experiments\docs\MIGRATION_PLAN.md'                  = 'Status note \(2026-05-'
}
foreach ($kv in $bannerChecks.GetEnumerator()) {
    if ((Test-Path $kv.Key) -and (Select-String -Path $kv.Key -Pattern $kv.Value -Quiet)) { Ok $kv.Key }
    else { Warn "banner missing in $($kv.Key)" }
}

# --- Summary ---
Write-Host ""
Write-Host "================ SUMMARY ================" -ForegroundColor Cyan
Write-Host "Blockers: $($blockers.Count)" -ForegroundColor $(if ($blockers.Count) {"Red"} else {"Green"})
Write-Host "Warnings: $($warnings.Count)" -ForegroundColor $(if ($warnings.Count) {"Yellow"} else {"Green"})
if ($blockers.Count) {
    Write-Host ""; Write-Host "BLOCKERS:" -ForegroundColor Red
    $blockers | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    Write-Host ""; Write-Host "RESULT: NOT READY TO ZIP" -ForegroundColor Red
    exit 1
}
if ($warnings.Count) {
    Write-Host ""; Write-Host "WARNINGS (review, not blockers):" -ForegroundColor Yellow
    $warnings | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
}
Write-Host ""; Write-Host "RESULT: READY TO ZIP" -ForegroundColor Green
Write-Host ""
Write-Host "Suggested zip command (PowerShell):" -ForegroundColor Cyan
Write-Host "  `$stamp = Get-Date -Format 'yyyyMMdd'"
Write-Host "  `$out   = `"`$env:USERPROFILE\Desktop\QF_repo_handin_`$stamp.zip`""
Write-Host "  Get-ChildItem -Path . -Force | Where-Object { `$_.Name -notin '.git','.venv','venv','__pycache__','.pytest_cache','node_modules','.mypy_cache','.vs','.idea' } | Compress-Archive -DestinationPath `$out -Force"
Write-Host ""
exit 0
