$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
. .\venv\Scripts\Activate.ps1
$env:PYTHONPATH = "."

# Loop on failures: reruns last failed tests on file changes
pytest -f --maxfail=1 --last-failed --last-failed-no-failures all tests
