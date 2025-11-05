# Windows의 서비스 파일을 WSL로 복사

Write-Host "[*] 서비스 파일을 WSL로 복사 중..." -ForegroundColor Cyan

$serviceFile = "chatgarment_service\main.py"
$wslPath = "/home/ims/ChatGarment/chatgarment_service/main.py"

if (Test-Path $serviceFile) {
    # WSL로 파일 복사
    wsl -d Ubuntu -- bash -c "mkdir -p ~/ChatGarment/chatgarment_service"
    
    # 파일 내용 읽기 및 WSL로 전달
    $content = Get-Content $serviceFile -Raw -Encoding UTF8
    
    # 임시 파일에 저장 후 WSL로 복사
    $tempFile = "temp_main.py"
    $content | Out-File -FilePath $tempFile -Encoding UTF8 -NoNewline
    
    # WSL로 복사
    wsl -d Ubuntu -- bash -c "cat > $wslPath" < $tempFile
    Remove-Item $tempFile -ErrorAction SilentlyContinue
    
    Write-Host "[+] 파일 복사 완료: $wslPath" -ForegroundColor Green
} else {
    Write-Host "[!] 파일을 찾을 수 없습니다: $serviceFile" -ForegroundColor Red
}

