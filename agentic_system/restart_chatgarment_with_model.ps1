# ChatGarment 서비스 재시작 (실제 모델 사용)

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "ChatGarment 서비스 재시작 (실제 모델 로딩)" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

# 기존 서비스 종료
Write-Host "[*] 기존 서비스 종료 중..." -ForegroundColor Cyan
$processes = Get-NetTCPConnection -LocalPort 9000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($pid in $processes) {
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Write-Host "  프로세스 종료: PID $pid" -ForegroundColor Yellow
}
Start-Sleep -Seconds 2
Write-Host "[OK] 기존 서비스 종료 완료" -ForegroundColor Green
Write-Host ""

# 서비스 시작 (ChatGarment 디렉토리에서 실행)
Write-Host "[*] ChatGarment 서비스 시작 중..." -ForegroundColor Cyan
Write-Host "    작업 디렉토리: ChatGarment 디렉토리로 변경" -ForegroundColor Yellow
Write-Host "    모델 로딩에는 몇 분이 걸릴 수 있습니다 (13.96 GB)" -ForegroundColor Yellow
Write-Host ""

$serviceDir = "agentic_system\chatgarment_service"
$chatgarmentDir = "ChatGarment"

# PowerShell 창에서 ChatGarment 디렉토리로 이동 후 서비스 시작
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
`$ErrorActionPreference = 'Continue'
cd 'D:\AI\ChatGarment\$chatgarmentDir'
Write-Host '===========================================================' -ForegroundColor Green
Write-Host 'ChatGarment Service - 실제 모델 로딩' -ForegroundColor Green
Write-Host '===========================================================' -ForegroundColor Green
Write-Host ''
Write-Host '[INFO] 작업 디렉토리: ' -NoNewline -ForegroundColor Cyan
Write-Host `$(Get-Location) -ForegroundColor White
Write-Host ''
Write-Host '[INFO] 체크포인트 확인:' -ForegroundColor Cyan
`$checkpoint = '..\checkpoints\try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final\pytorch_model.bin'
if (Test-Path `$checkpoint) {
    `$size = (Get-Item `$checkpoint).Length / 1GB
    Write-Host "  체크포인트 존재: `$checkpoint" -ForegroundColor Green
    Write-Host "  크기: `$(`$size.ToString('F2')) GB" -ForegroundColor Green
} else {
    Write-Host "  체크포인트 없음: `$checkpoint" -ForegroundColor Red
}
Write-Host ''
Write-Host '[INFO] 서비스 시작 중...' -ForegroundColor Cyan
Write-Host '    모델 로딩 로그가 출력됩니다.' -ForegroundColor Yellow
Write-Host ''
cd 'D:\AI\ChatGarment\$serviceDir'
python main.py
"@

Write-Host "[OK] ChatGarment 서비스 시작 창이 열렸습니다" -ForegroundColor Green
Write-Host ""
Write-Host "[*] 서비스 로그에서 다음을 확인하세요:" -ForegroundColor Cyan
Write-Host "    1. 작업 디렉토리가 ChatGarment로 설정되었는지" -ForegroundColor White
Write-Host "    2. 'ChatGarment Pipeline 로딩 완료' 메시지" -ForegroundColor White
Write-Host "    3. 또는 오류 메시지 (모델 로딩 실패 시)" -ForegroundColor White
Write-Host ""
Write-Host "[*] 모델 로딩에는 몇 분이 걸릴 수 있습니다..." -ForegroundColor Yellow
Write-Host ""

