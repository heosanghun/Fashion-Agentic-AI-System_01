# ChatGarment 서비스 시작 스크립트 (Windows)

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "ChatGarment 서비스 시작" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

# 프로젝트 루트 경로
$projectRoot = Split-Path -Parent $PSScriptRoot
$serviceDir = Join-Path $projectRoot "agentic_system" "chatgarment_service"

Write-Host "[*] 서비스 디렉토리: $serviceDir" -ForegroundColor Cyan

if (-not (Test-Path $serviceDir)) {
    Write-Host "[!] 서비스 디렉토리를 찾을 수 없습니다: $serviceDir" -ForegroundColor Red
    exit 1
}

# 기존 서비스 프로세스 확인 및 종료
Write-Host "[*] 기존 서비스 프로세스 확인 중..." -ForegroundColor Cyan
$existingProcesses = Get-NetTCPConnection -LocalPort 9000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($existingProcesses) {
    foreach ($pid in $existingProcesses) {
        Write-Host "[!] 포트 9000을 사용하는 프로세스 종료: PID $pid" -ForegroundColor Yellow
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
}

# Python 환경 확인
Write-Host "[*] Python 환경 확인 중..." -ForegroundColor Cyan
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[!] Python을 찾을 수 없습니다." -ForegroundColor Red
    exit 1
}
Write-Host "[+] Python 발견: $($pythonCmd.Source)" -ForegroundColor Green

# 서비스 시작
Write-Host ""
Write-Host "[*] ChatGarment 서비스 시작 중..." -ForegroundColor Cyan
Write-Host "   URL: http://localhost:9000" -ForegroundColor Yellow
Write-Host "   종료하려면 Ctrl+C" -ForegroundColor Yellow
Write-Host ""

Set-Location $serviceDir
python main.py

