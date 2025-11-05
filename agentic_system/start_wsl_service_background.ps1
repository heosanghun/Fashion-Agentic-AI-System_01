# WSL에서 ChatGarment 서비스를 백그라운드로 시작

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "ChatGarment 서비스 시작 (WSL 백그라운드)" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

# 서비스 시작
$startScript = @'
cd ~/ChatGarment/chatgarment_service

# 기존 프로세스 종료 (있는 경우)
if [ -f service.pid ]; then
    PID=$(cat service.pid)
    kill $PID 2>/dev/null
    rm service.pid
fi

# 서비스 시작
nohup python3 main.py > service.log 2>&1 &
echo $! > service.pid

sleep 3

# 서비스 확인
if curl -s http://localhost:9000/health > /dev/null 2>&1; then
    echo "✅ 서비스 시작 성공!"
    echo "   PID: $(cat service.pid)"
    echo "   URL: http://localhost:9000"
    echo "   로그: tail -f ~/ChatGarment/chatgarment_service/service.log"
else
    echo "⚠️ 서비스 시작 확인 중..."
    sleep 2
    if curl -s http://localhost:9000/health > /dev/null 2>&1; then
        echo "✅ 서비스 시작 성공!"
    else
        echo "❌ 서비스 시작 실패. 로그 확인: tail ~/ChatGarment/chatgarment_service/service.log"
    fi
fi
'@

wsl -d Ubuntu -- bash -c $startScript

Write-Host ""
Write-Host "[*] 서비스 상태 확인 중..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

$healthCheck = wsl -d Ubuntu -- bash -c "curl -s http://localhost:9000/health 2>/dev/null"
if ($healthCheck -match "healthy") {
    Write-Host "[+] 서비스가 정상 작동 중입니다!" -ForegroundColor Green
    Write-Host "   $healthCheck" -ForegroundColor Cyan
} else {
    Write-Host "[!] 서비스 확인 중... 잠시 후 다시 시도하세요." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "다음 단계:" -ForegroundColor Yellow
Write-Host "1. API 서버 재시작: .\restart_api_server.ps1" -ForegroundColor Cyan
Write-Host "2. 프론트엔드에서 테스트" -ForegroundColor Cyan
Write-Host ""

