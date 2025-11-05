# Start All Services Script

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "Starting All Services" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

# Check if services are already running
Write-Host "[*] Checking existing services..." -ForegroundColor Cyan
$apiRunning = $false
$chatgarmentRunning = $false

try {
    $null = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
    $apiRunning = $true
    Write-Host "[OK] API Server is already running" -ForegroundColor Green
} catch {
    Write-Host "[INFO] API Server is not running" -ForegroundColor Yellow
}

try {
    $null = Invoke-WebRequest -Uri "http://localhost:9000/health" -TimeoutSec 2 -ErrorAction Stop
    $chatgarmentRunning = $true
    Write-Host "[OK] ChatGarment Service is already running" -ForegroundColor Green
} catch {
    Write-Host "[INFO] ChatGarment Service is not running" -ForegroundColor Yellow
}

Write-Host ""

# Start ChatGarment Service
if (-not $chatgarmentRunning) {
    Write-Host "[*] Starting ChatGarment Service..." -ForegroundColor Cyan
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    $chatgarmentDir = Join-Path $scriptPath "chatgarment_service"
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$chatgarmentDir'; Write-Host 'ChatGarment Service Starting...' -ForegroundColor Green; python main.py"
    Write-Host "[OK] ChatGarment Service starting window opened" -ForegroundColor Green
    Start-Sleep -Seconds 3
}

# Start API Server
if (-not $apiRunning) {
    Write-Host "[*] Starting API Server..." -ForegroundColor Cyan
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath'; Write-Host 'API Server Starting...' -ForegroundColor Green; python start_api_server.py"
    Write-Host "[OK] API Server starting window opened" -ForegroundColor Green
    Start-Sleep -Seconds 3
}

Write-Host ""
Write-Host "[*] Waiting for services to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Green
Write-Host "Service Status Check" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

# Final Status Check
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
& (Join-Path $scriptPath "check_services.ps1")

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Green
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Make sure both services are running" -ForegroundColor Cyan
Write-Host "2. Test the system via frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "3. Check service logs in the PowerShell windows" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Green

