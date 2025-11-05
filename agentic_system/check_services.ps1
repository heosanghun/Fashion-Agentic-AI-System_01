# Service Status Check Script

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "Service Status Check" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

# API Server Check (Port 8000)
Write-Host "[*] Checking API Server (Port 8000)..." -ForegroundColor Cyan
try {
    $apiResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "[OK] API Server is running" -ForegroundColor Green
    Write-Host "   Status: $($apiResponse.StatusCode)" -ForegroundColor Yellow
} catch {
    Write-Host "[FAIL] API Server is not running" -ForegroundColor Red
    Write-Host "   Start: cd agentic_system; python start_api_server.py" -ForegroundColor Yellow
}

Write-Host ""

# ChatGarment Service Check (Port 9000)
Write-Host "[*] Checking ChatGarment Service (Port 9000)..." -ForegroundColor Cyan
try {
    $cgResponse = Invoke-WebRequest -Uri "http://localhost:9000/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "[OK] ChatGarment Service is running" -ForegroundColor Green
    Write-Host "   Status: $($cgResponse.StatusCode)" -ForegroundColor Yellow
    Write-Host "   Response: $($cgResponse.Content)" -ForegroundColor Yellow
} catch {
    Write-Host "[FAIL] ChatGarment Service is not running" -ForegroundColor Red
    Write-Host "   Start Options:" -ForegroundColor Yellow
    Write-Host "   1. Separate terminal: cd agentic_system\chatgarment_service; python main.py" -ForegroundColor Yellow
    Write-Host "   2. Or run: agentic_system\start_chatgarment.bat" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Green
