# Bank As A Service - Start All Services (Windows PowerShell)
# Run this script to launch both backend and frontend services

$ErrorActionPreference = "Continue"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "              BANK AS A SERVICE - MULTI-SERVICE LAUNCHER" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Colors
$greenCheck = "✓"
$blueInfo = "ℹ"
$yellowWarn = "⚠"

# Check if banking directory exists
if (-not (Test-Path "banking")) {
    Write-Host "$yellowWarn Creating banking directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "banking" | Out-Null
}

Set-Location "banking"

# Check Python
Write-Host "$blueInfo Checking Python..." -ForegroundColor Blue
python --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "$yellowWarn Error: Python not found. Install Python 3.10+" -ForegroundColor Red
    exit 1
}

Write-Host "$greenCheck Python found" -ForegroundColor Green
Write-Host ""

# Check dependencies
Write-Host "$blueInfo Checking Python packages..." -ForegroundColor Blue
$packages = @("flask", "pydantic", "requests")

foreach ($package in $packages) {
    python -c "import $package" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "$yellowWarn Installing $package..." -ForegroundColor Yellow
        pip install $package | Out-Null
    } else {
        Write-Host "$greenCheck $package installed" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "STARTING BANK AS A SERVICE PLATFORM" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
Write-Host ""

# Check if files exist
if (-not (Test-Path "baas_backend.py")) {
    Write-Host "$yellowWarn Error: baas_backend.py not found" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "banking_ui_english.py")) {
    Write-Host "$yellowWarn Error: banking_ui_english.py not found" -ForegroundColor Red
    exit 1
}

# Start Backend in new window
Write-Host "$blueInfo Starting Backend API (Port 5001)..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python baas_backend.py"
Start-Sleep -Seconds 2
Write-Host "$greenCheck Backend started" -ForegroundColor Green

# Start Frontend in new window
Write-Host "$blueInfo Starting Frontend Dashboard (Port 5000)..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python banking_ui_english.py"
Start-Sleep -Seconds 2
Write-Host "$greenCheck Frontend started" -ForegroundColor Green

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "BANK AS A SERVICE IS RUNNING" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "$blueInfo Access Dashboard:" -ForegroundColor Blue
Write-Host "  http://localhost:5000" -ForegroundColor Cyan
Write-Host ""

Write-Host "$blueInfo API Health Check:" -ForegroundColor Blue
Write-Host "  http://localhost:5001/api/health" -ForegroundColor Cyan
Write-Host ""

Write-Host "$blueInfo Services running on:" -ForegroundColor Blue
Write-Host "  Backend  (Port 5001): http://localhost:5001" -ForegroundColor Cyan
Write-Host "  Frontend (Port 5000): http://localhost:5000" -ForegroundColor Cyan
Write-Host ""

Write-Host "$yellowWarn Note: Services opened in new terminal windows" -ForegroundColor Yellow
Write-Host "$yellowWarn Close each window to stop that service" -ForegroundColor Yellow
Write-Host ""

Write-Host "Returning to main window..." -ForegroundColor Gray
Write-Host ""
