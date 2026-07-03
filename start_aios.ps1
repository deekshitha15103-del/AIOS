Write-Host "Starting AIOS..." -ForegroundColor Cyan

$ProjectPath = "C:\Users\deeks\AIOS"
Set-Location $ProjectPath

if (!(Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found. Please create venv first." -ForegroundColor Red
    exit
}

$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"

Write-Host "Starting FastAPI backend..." -ForegroundColor Yellow

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd $ProjectPath; .\venv\Scripts\Activate.ps1; `$env:HF_HUB_OFFLINE='1'; `$env:TRANSFORMERS_OFFLINE='1'; python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 10

Write-Host "Starting Streamlit frontend..." -ForegroundColor Yellow

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd $ProjectPath; .\venv\Scripts\Activate.ps1; streamlit run frontend/app.py"
)

Start-Sleep -Seconds 5

Write-Host "Opening AIOS in browser..." -ForegroundColor Green

Start-Process "http://localhost:8501"

Write-Host "AIOS launched successfully." -ForegroundColor Green