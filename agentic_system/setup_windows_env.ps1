# Windows 환경 변수 설정 스크립트
# 리눅스 IP 주소를 입력하세요

$linuxIP = Read-Host "리눅스 서버 IP 주소를 입력하세요 (예: 192.168.1.100)"

if ([string]::IsNullOrWhiteSpace($linuxIP)) {
    Write-Host "❌ IP 주소가 입력되지 않았습니다." -ForegroundColor Red
    exit 1
}

$serviceURL = "http://$linuxIP:9000"

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Green
Write-Host "환경 변수 설정" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host "ChatGarment 서비스 URL: $serviceURL" -ForegroundColor Cyan
Write-Host ""

# 현재 세션에 환경 변수 설정
$env:CHATGARMENT_SERVICE_URL = $serviceURL
$env:USE_CHATGARMENT_SERVICE = "true"

Write-Host "[+] 환경 변수 설정 완료 (현재 세션)" -ForegroundColor Green
Write-Host "   CHATGARMENT_SERVICE_URL=$serviceURL" -ForegroundColor Yellow
Write-Host "   USE_CHATGARMENT_SERVICE=true" -ForegroundColor Yellow
Write-Host ""

# 영구 설정 (사용자 레벨)
try {
    [System.Environment]::SetEnvironmentVariable("CHATGARMENT_SERVICE_URL", $serviceURL, "User")
    [System.Environment]::SetEnvironmentVariable("USE_CHATGARMENT_SERVICE", "true", "User")
    Write-Host "[+] 환경 변수 영구 설정 완료 (사용자 레벨)" -ForegroundColor Green
} catch {
    Write-Host "[!] 영구 설정 실패: $_" -ForegroundColor Yellow
    Write-Host "    현재 세션에서는 작동합니다." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Green
Write-Host "연결 테스트" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "$serviceURL/health" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ ChatGarment 서비스 연결 성공!" -ForegroundColor Green
        Write-Host "   응답: $($response.Content)" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️ 서비스 응답: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ 서비스 연결 실패: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "확인 사항:" -ForegroundColor Yellow
    Write-Host "1. 리눅스 서버에서 ChatGarment 서비스가 실행 중인지 확인" -ForegroundColor White
    Write-Host "2. 리눅스 IP 주소가 올바른지 확인" -ForegroundColor White
    Write-Host "3. 방화벽 설정 확인" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Green
Write-Host "다음 단계" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host "1. API 서버 재시작: python start_api_server.py" -ForegroundColor Cyan
Write-Host "2. 프론트엔드에서 이미지 업로드 테스트" -ForegroundColor Cyan
Write-Host ""

