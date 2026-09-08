# PowerShell Local Launch Script for Studio Guardian
# Usage: .\scripts\start_local.ps1

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " 🛡️ LAUNCHING STUDIO GUARDIAN SERVICES" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Ensure .env exists
if (-not (Test-Path ".\.env")) {
    if (Test-Path ".\.env.example") {
        Copy-Item ".\.env.example" ".\.env"
        Write-Host " Created .env from .env.example" -ForegroundColor Green
    }
}

Write-Host " Starting FastAPI Backend (Port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..\backend'; .\.venv\Scripts\activate; uvicorn src.main:app --port 8000 --reload"

Write-Host " Starting React Command Center (Port 5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..\frontend'; npm run dev"

Write-Host ""
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan
Write-Host " Services launched in background windows!" -ForegroundColor Green
Write-Host " Command Center URL: http://localhost:5173" -ForegroundColor Yellow
Write-Host " Backend API Docs:   http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""
