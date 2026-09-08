# PowerShell Environment & Service Verification Script for Studio Guardian
# Usage: .\scripts\verify_environment.ps1

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " STUDIO GUARDIAN - LOCAL ENVIRONMENT HEALTH CHECK" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$allPass = $true

# 1. Check .env Configuration File
if (Test-Path ".\.env") {
    Write-Host " [PASS] Environment File (.env) (Found in repo root)" -ForegroundColor Green
} else {
    if (Test-Path ".\.env.example") {
        Copy-Item ".\.env.example" ".\.env"
        Write-Host " [PASS] Environment File (.env) (Created from .env.example)" -ForegroundColor Green
    } else {
        Write-Host " [FAIL] Environment File (.env) (Missing .env template)" -ForegroundColor Yellow
        $allPass = $false
    }
}

# 2. Check Python Installation & Virtual Environment
$pyExe = "python"
if (Test-Path ".\backend\.venv\Scripts\python.exe") {
    $pyExe = ".\backend\.venv\Scripts\python.exe"
}

try {
    $pyVer = (& $pyExe --version 2>&1).ToString()
    if ($pyVer -like "*Python 3*") {
        Write-Host " [PASS] Python Runtime ($pyVer)" -ForegroundColor Green
    } else {
        Write-Host " [FAIL] Python Runtime (Python 3.12+ required)" -ForegroundColor Yellow
        $allPass = $false
    }
} catch {
    Write-Host " [FAIL] Python Runtime (Python executable not found in PATH)" -ForegroundColor Yellow
    $allPass = $false
}

if (Test-Path ".\backend\.venv") {
    Write-Host " [PASS] Python Virtualenv (backend\.venv found)" -ForegroundColor Green
} else {
    Write-Host " [FAIL] Python Virtualenv (Run 'python -m venv .venv' inside backend\)" -ForegroundColor Yellow
    $allPass = $false
}

# 3. Check Node.js Runtime
try {
    $nodeVer = (node --version 2>&1).ToString()
    Write-Host " [PASS] Node.js Runtime ($nodeVer)" -ForegroundColor Green
} catch {
    Write-Host " [FAIL] Node.js Runtime (Node.js 18+ required)" -ForegroundColor Yellow
    $allPass = $false
}

# 4. Check Docker Engine Status
try {
    $dockerCheck = (docker info 2>&1).ToString()
    if ($LASTEXITCODE -eq 0) {
        Write-Host " [PASS] Docker Engine (Docker daemon running)" -ForegroundColor Green
    } else {
        Write-Host " [INFO] Docker Engine (Docker Desktop inactive - local SQLite/Mock mode active)" -ForegroundColor Gray
    }
} catch {
    Write-Host " [INFO] Docker Engine (Docker CLI not found - local SQLite/Mock mode active)" -ForegroundColor Gray
}

# 5. Check Backend FastAPI Endpoint (http://localhost:8000)
try {
    $backendRes = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/incidents" -Method Get -TimeoutSec 3 -ErrorAction Stop
    Write-Host " [PASS] Backend API Service (Responding at http://localhost:8000)" -ForegroundColor Green
} catch {
    Write-Host " [NOT RUNNING] Backend API Service (Start via 'uvicorn src.main:app --port 8000' in backend\)" -ForegroundColor Yellow
    $allPass = $false
}

# 6. Check Frontend React Command Center (http://localhost:5173)
try {
    $frontendRes = Invoke-WebRequest -Uri "http://localhost:5173" -Method Get -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Host " [PASS] Frontend Command Center (Responding at http://localhost:5173)" -ForegroundColor Green
} catch {
    Write-Host " [NOT RUNNING] Frontend Command Center (Start via 'npm run dev' in frontend\)" -ForegroundColor Yellow
    $allPass = $false
}

Write-Host ""
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan
if ($allPass) {
    Write-Host " ALL SERVICES ARE ACTIVE AND HEALTHY!" -ForegroundColor Green
    Write-Host " Access the Studio Guardian Command Center at: http://localhost:5173" -ForegroundColor Yellow
} else {
    Write-Host " SERVICE STATUS CHECK COMPLETE." -ForegroundColor Yellow
    Write-Host " Refer to the log output above to start any missing services." -ForegroundColor White
}
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""
