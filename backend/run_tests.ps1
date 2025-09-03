param([switch]$ReuseVenv)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

# 1) Create or reuse venv (this script assumes backend as working dir)
if (-not $ReuseVenv -and -not (Test-Path ".\venv")) {
  python -m venv venv
}
. .\venv\Scripts\Activate.ps1

# 2) Install dependencies
# Install backend runtime deps from repo root if available
if (Test-Path "..\requirements-prod.txt") {
  pip install -r ..\requirements-prod.txt
}
# Optional: additional backend-specific requirements files
if (Test-Path ".\requirements-dev.txt") {
  pip install -r .\requirements-dev.txt
} elseif (Test-Path ".\requirements.txt") {
  pip install -r .\requirements.txt
}
# Ensure test tooling
pip install pytest pytest-cov pytest-benchmark pytest-xdist pytest-json-report tzdata psutil

# 3) Env for imports
$env:PYTHONPATH = "."
New-Item -ItemType Directory -Force -Path ".\test-reports" | Out-Null

# 4) Run tests (parallel, coverage, reports)
pytest -n auto `
  --maxfail=1 `
  --cov=app --cov-report=term-missing --cov-report=html `
  --junitxml=.\test-reports\junit.xml `
  --json-report --json-report-file=.\test-reports\report.json `
  tests

Write-Host "`nCoverage HTML: $root\htmlcov\index.html"
Write-Host "JUnit XML:    $root\test-reports\junit.xml"
Write-Host "JSON report:  $root\test-reports\report.json"
