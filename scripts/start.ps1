$ErrorActionPreference = "Stop"
if (-not $env:VIRTUAL_ENV) { & ".\.venv\Scripts\Activate.ps1" }
python -m uvicorn orchestrator.main:app --reload --port 8000 --app-dir src