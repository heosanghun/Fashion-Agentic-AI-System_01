# API 서버 완전 재시작 스크립트

Write-Host "=" * 60
Write-Host "API 서버 완전 재시작"
Write-Host "=" * 60

# 1. 포트 8000 사용 프로세스 종료
Write-Host "`n[1/4] 포트 8000 사용 프로세스 종료 중..."
$processes = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($processes) {
    foreach ($pid in $processes) {
        Write-Host "  프로세스 종료: PID $pid"
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 2

# 2. Python 캐시 삭제
Write-Host "`n[2/4] Python 캐시 삭제 중..."
Get-ChildItem -Path "agentic_system" -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path "agentic_system" -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "  완료"

# 3. 포트 확인
Write-Host "`n[3/4] 포트 8000 확인 중..."
$check = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($check) {
    Write-Host "  경고: 포트 8000이 여전히 사용 중입니다."
    Write-Host "  프로세스: $($check.OwningProcess -join ', ')"
} else {
    Write-Host "  포트 8000 사용 가능"
}

# 4. API 서버 시작
Write-Host "`n[4/4] API 서버 시작 중..."
Set-Location agentic_system
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python start_api_server.py"
Set-Location ..
Write-Host "  API 서버가 새 PowerShell 창에서 시작되었습니다."
Write-Host "`n5초 대기 후 테스트를 진행합니다..."
Start-Sleep -Seconds 5

Write-Host "`n" + "=" * 60
Write-Host "재시작 완료!"
Write-Host "=" * 60

