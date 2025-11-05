# 자동 설정 완료 스크립트

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "ChatGarment 마이크로서비스 자동 설정" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

# Step 1: 로컬호스트로 설정 (WSL 또는 로컬 서버 가능성)
$linuxIP = "localhost"
$serviceURL = "http://localhost:9000"

Write-Host "[*] Step 1: 환경 변수 설정" -ForegroundColor Cyan
Write-Host "   서비스 URL: $serviceURL" -ForegroundColor Yellow

# 환경 변수 설정 (현재 세션)
$env:CHATGARMENT_SERVICE_URL = $serviceURL
$env:USE_CHATGARMENT_SERVICE = "true"

# 영구 설정 (사용자 레벨)
try {
    [System.Environment]::SetEnvironmentVariable("CHATGARMENT_SERVICE_URL", $serviceURL, "User")
    [System.Environment]::SetEnvironmentVariable("USE_CHATGARMENT_SERVICE", "true", "User")
    Write-Host "[+] 환경 변수 영구 설정 완료" -ForegroundColor Green
} catch {
    Write-Host "[!] 영구 설정 실패 (현재 세션에만 적용)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[*] Step 2: 서비스 연결 테스트" -ForegroundColor Cyan

# 서비스 헬스체크 (여러 IP 시도)
$testIPs = @("localhost", "127.0.0.1")
$serviceFound = $false

foreach ($testIP in $testIPs) {
    try {
        $response = Invoke-WebRequest -Uri "http://$testIP:9000/health" -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "[+] ChatGarment 서비스 연결 성공! ($testIP:9000)" -ForegroundColor Green
            $serviceFound = $true
            break
        }
    } catch {
        # 다음 IP 시도
    }
}

if (-not $serviceFound) {
    Write-Host "[!] ChatGarment 서비스가 아직 실행되지 않았습니다." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "다음 단계:" -ForegroundColor Yellow
    Write-Host "1. 리눅스 서버에서 ChatGarment 서비스 시작 필요" -ForegroundColor Cyan
    Write-Host "   cd ~/ChatGarment/chatgarment_service" -ForegroundColor White
    Write-Host "   uvicorn main:app --host 0.0.0.0 --port 9000" -ForegroundColor White
    Write-Host ""
    Write-Host "2. 서비스 시작 후 이 스크립트를 다시 실행하세요" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[+] Step 3: 모든 설정 완료!" -ForegroundColor Green
    Write-Host ""
    Write-Host "다음 단계:" -ForegroundColor Yellow
    Write-Host "1. API 서버 재시작: python start_api_server.py" -ForegroundColor Cyan
    Write-Host "2. 프론트엔드에서 이미지 업로드 테스트" -ForegroundColor Cyan
    Write-Host ""
}

