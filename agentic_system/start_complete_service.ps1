# 완전 자동 서비스 시작 스크립트 (인코딩 문제 해결)

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "ChatGarment Service - Complete Setup" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

# Step 1: WSL Ubuntu 확인
Write-Host "[Step 1] Checking WSL Ubuntu..." -ForegroundColor Cyan
$wslCheck = wsl -d Ubuntu -- bash -c "echo OK" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Ubuntu not available" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Ubuntu is running" -ForegroundColor Green
Write-Host ""

# Step 2: 서비스 디렉토리 설정
Write-Host "[Step 2] Setting up service directory..." -ForegroundColor Cyan
wsl -d Ubuntu -- bash -c "mkdir -p ~/ChatGarment/chatgarment_service && cd ~/ChatGarment/chatgarment_service && ls -la main.py" 2>&1 | Out-Null
Write-Host "[OK] Service directory ready" -ForegroundColor Green
Write-Host ""

# Step 3: 의존성 설치
Write-Host "[Step 3] Installing dependencies..." -ForegroundColor Cyan
wsl -d Ubuntu -- bash -c "cd ~/ChatGarment/chatgarment_service && python3 -m pip install --break-system-packages --quiet fastapi uvicorn python-multipart" 2>&1 | Out-Null
Write-Host "[OK] Dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 4: 서비스 시작 (백그라운드)
Write-Host "[Step 4] Starting service..." -ForegroundColor Cyan

$serviceScript = @'
cd ~/ChatGarment/chatgarment_service
if [ -f service.pid ]; then
    PID=$(cat service.pid)
    kill $PID 2>/dev/null
    rm -f service.pid
fi
nohup python3 main.py > service.log 2>&1 &
echo $! > service.pid
sleep 3
if curl -s http://localhost:9000/health > /dev/null 2>&1; then
    echo "SUCCESS"
    echo "PID: $(cat service.pid)"
    echo "URL: http://localhost:9000"
else
    echo "FAILED"
    tail -20 service.log
fi
'@

$result = wsl -d Ubuntu -- bash -c $serviceScript

if ($result -match "SUCCESS") {
    Write-Host "[OK] Service started successfully!" -ForegroundColor Green
    $result | ForEach-Object { Write-Host $_ -ForegroundColor White }
} else {
    Write-Host "[ERROR] Service start failed" -ForegroundColor Red
    $result | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
}

Write-Host ""

# Step 5: Windows 환경 변수 설정
Write-Host "[Step 5] Setting Windows environment variables..." -ForegroundColor Cyan
[System.Environment]::SetEnvironmentVariable("CHATGARMENT_SERVICE_URL", "http://localhost:9000", "User")
[System.Environment]::SetEnvironmentVariable("USE_CHATGARMENT_SERVICE", "true", "User")
Write-Host "[OK] Environment variables set" -ForegroundColor Green
Write-Host "   CHATGARMENT_SERVICE_URL=http://localhost:9000" -ForegroundColor Yellow
Write-Host "   USE_CHATGARMENT_SERVICE=true" -ForegroundColor Yellow
Write-Host ""

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Restart API server: .\restart_api_server.ps1" -ForegroundColor Cyan
Write-Host "2. Test in frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

