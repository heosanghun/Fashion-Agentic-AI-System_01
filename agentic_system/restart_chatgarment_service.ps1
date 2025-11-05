# ChatGarment 서비스 재시작 스크립트 (실제 모델 사용)

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "ChatGarment 서비스 재시작 (실제 모델 사용)" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

# 기존 서비스 종료
Write-Host "[*] 기존 서비스 확인 중..." -ForegroundColor Cyan
$existingProcesses = Get-NetTCPConnection -LocalPort 9000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($existingProcesses) {
    foreach ($pid in $existingProcesses) {
        Write-Host "[!] 포트 9000을 사용하는 프로세스 종료: PID $pid" -ForegroundColor Yellow
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
    Write-Host "[OK] 기존 서비스 종료 완료" -ForegroundColor Green
} else {
    Write-Host "[INFO] 실행 중인 서비스가 없습니다" -ForegroundColor Cyan
}

Write-Host ""

# 모델 파일 확인
Write-Host "[*] 모델 파일 확인 중..." -ForegroundColor Cyan
$modelFile = "checkpoints\try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final\pytorch_model.bin"
if (Test-Path $modelFile) {
    $file = Get-Item $modelFile
    $sizeGB = [math]::Round($file.Length / 1GB, 2)
    Write-Host "[OK] 모델 파일 확인 완료" -ForegroundColor Green
    Write-Host "    경로: $($file.FullName)" -ForegroundColor Yellow
    Write-Host "    크기: $sizeGB GB" -ForegroundColor Yellow
} else {
    Write-Host "[WARNING] 모델 파일을 찾을 수 없습니다: $modelFile" -ForegroundColor Yellow
    Write-Host "    서비스는 Mock 모드로 동작합니다" -ForegroundColor Yellow
}

Write-Host ""

# 서비스 디렉토리 확인
$serviceDir = "agentic_system\chatgarment_service"
if (-not (Test-Path $serviceDir)) {
    Write-Host "[FAIL] 서비스 디렉토리를 찾을 수 없습니다: $serviceDir" -ForegroundColor Red
    exit 1
}

Write-Host "[*] ChatGarment 서비스 시작 중..." -ForegroundColor Cyan
Write-Host "    디렉토리: $serviceDir" -ForegroundColor Yellow
Write-Host "    URL: http://localhost:9000" -ForegroundColor Yellow
Write-Host "    종료하려면 Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# 서비스 시작 (새 터미널에서)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd D:\AI\ChatGarment\$serviceDir; Write-Host 'ChatGarment Service Starting with Real Model...' -ForegroundColor Green; Write-Host 'Model Path: D:\AI\ChatGarment\checkpoints\try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final\pytorch_model.bin' -ForegroundColor Cyan; python main.py"

Write-Host "[OK] 서비스 시작 창이 열렸습니다" -ForegroundColor Green
Write-Host ""
Write-Host "[*] 서비스가 시작되는 데 시간이 걸릴 수 있습니다..." -ForegroundColor Cyan
Write-Host "    모델 로딩에는 몇 분이 걸릴 수 있습니다 (13.96 GB)" -ForegroundColor Yellow
Write-Host ""

# 서비스 시작 대기
Write-Host "[*] 서비스 시작 대기 중..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# 서비스 상태 확인
Write-Host ""
Write-Host "[*] 서비스 상태 확인 중..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

try {
    $response = Invoke-WebRequest -Uri "http://localhost:9000/health" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "[OK] 서비스가 실행 중입니다!" -ForegroundColor Green
    Write-Host "    상태: $($response.StatusCode)" -ForegroundColor Yellow
    Write-Host "    응답: $($response.Content)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "[INFO] 서비스 로그를 확인하여 모델 로딩 상태를 확인하세요." -ForegroundColor Cyan
    Write-Host "    'ChatGarment Pipeline 로딩 완료' 메시지가 보이면 성공입니다." -ForegroundColor Cyan
} catch {
    Write-Host "[INFO] 서비스가 아직 시작 중입니다..." -ForegroundColor Yellow
    Write-Host "    잠시 후 다시 확인하거나 서비스 창의 로그를 확인하세요." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Green
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Check service window for 'ChatGarment Pipeline loaded' message" -ForegroundColor Cyan
Write-Host "2. Check service status: .\agentic_system\check_services.ps1" -ForegroundColor Cyan
Write-Host "3. Run integration test: python agentic_system\test_integration.py" -ForegroundColor Cyan
Write-Host "4. Test 3D conversion in frontend" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Green

