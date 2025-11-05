# API 서버 자동 재시작 스크립트

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "API 서버 재시작" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

# 기존 서버 프로세스 종료
Write-Host "[*] 기존 서버 프로세스 종료 중..." -ForegroundColor Cyan
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*start_api_server*" -or $_.CommandLine -like "*api.main*"
} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# 환경 변수 확인
Write-Host "[*] 환경 변수 확인..." -ForegroundColor Cyan
$serviceURL = [System.Environment]::GetEnvironmentVariable("CHATGARMENT_SERVICE_URL", "User")
$useService = [System.Environment]::GetEnvironmentVariable("USE_CHATGARMENT_SERVICE", "User")

if ($serviceURL) {
    Write-Host "[+] CHATGARMENT_SERVICE_URL: $serviceURL" -ForegroundColor Green
} else {
    Write-Host "[!] CHATGARMENT_SERVICE_URL이 설정되지 않았습니다." -ForegroundColor Yellow
    $serviceURL = "http://localhost:9000"
    [System.Environment]::SetEnvironmentVariable("CHATGARMENT_SERVICE_URL", $serviceURL, "User")
    Write-Host "[+] 환경 변수 설정 완료: $serviceURL" -ForegroundColor Green
}

if ($useService -eq "true") {
    Write-Host "[+] USE_CHATGARMENT_SERVICE: true" -ForegroundColor Green
} else {
    Write-Host "[!] USE_CHATGARMENT_SERVICE가 false입니다." -ForegroundColor Yellow
    [System.Environment]::SetEnvironmentVariable("USE_CHATGARMENT_SERVICE", "true", "User")
    Write-Host "[+] 환경 변수 설정 완료" -ForegroundColor Green
}

Write-Host ""
Write-Host "[*] API 서버 시작 중..." -ForegroundColor Cyan
Write-Host "[*] 종료하려면 Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# 현재 디렉토리로 이동
cd $PSScriptRoot

# API 서버 시작
python start_api_server.py

