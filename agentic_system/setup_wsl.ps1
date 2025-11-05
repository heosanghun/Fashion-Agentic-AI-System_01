# WSL 자동 설정 스크립트

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "WSL (Windows Subsystem for Linux) 자동 설정" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

# WSL 설치 여부 확인
Write-Host "[*] WSL 설치 확인 중..." -ForegroundColor Cyan
$wslStatus = wsl --status 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "[+] WSL이 설치되어 있습니다!" -ForegroundColor Green
    wsl --list --verbose
    
    Write-Host ""
    Write-Host "[*] WSL 배포판 시작 중..." -ForegroundColor Cyan
    $wslList = wsl --list --verbose 2>&1
    
    if ($wslList -match "Ubuntu") {
        Write-Host "[+] Ubuntu 배포판 발견!" -ForegroundColor Green
        Write-Host "[*] Ubuntu 시작 중..." -ForegroundColor Cyan
        
        # Ubuntu 시작
        wsl -d Ubuntu -- bash -c "echo 'Ubuntu 시작 완료'"
        
        Write-Host ""
        Write-Host "[+] WSL Ubuntu 준비 완료!" -ForegroundColor Green
    } else {
        Write-Host "[!] Ubuntu 배포판이 설치되지 않았습니다." -ForegroundColor Yellow
        Write-Host "[*] Ubuntu 설치 중..." -ForegroundColor Cyan
        
        # Ubuntu 설치
        wsl --install -d Ubuntu
        
        Write-Host ""
        Write-Host "[+] Ubuntu 설치가 시작되었습니다." -ForegroundColor Green
        Write-Host "[*] 설치 완료 후 Ubuntu를 실행하세요." -ForegroundColor Yellow
    }
} else {
    Write-Host "[!] WSL이 설치되지 않았습니다." -ForegroundColor Yellow
    Write-Host "[*] WSL 설치 중..." -ForegroundColor Cyan
    
    # 관리자 권한 필요
    Write-Host "[!] 관리자 권한이 필요합니다." -ForegroundColor Red
    Write-Host "[*] PowerShell을 관리자 권한으로 실행한 후 다시 실행하세요." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "또는 수동으로 설치:" -ForegroundColor Yellow
    Write-Host "wsl --install" -ForegroundColor Cyan
}

