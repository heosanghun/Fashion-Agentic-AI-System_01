# WSL Ubuntu 완전 자동 설정 및 서비스 시작

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "WSL Ubuntu ChatGarment 서비스 완전 자동 설정" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

# Ubuntu 시작 확인
Write-Host "[*] Ubuntu 시작 중..." -ForegroundColor Cyan
$ubuntuCheck = wsl -d Ubuntu -- bash -c "echo 'OK'" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Ubuntu 시작 실패. WSL 서비스를 확인하세요." -ForegroundColor Red
    exit 1
}

Write-Host "[+] Ubuntu 시작 완료!" -ForegroundColor Green
Write-Host ""

# IP 확인
Write-Host "[*] Ubuntu IP 확인 중..." -ForegroundColor Cyan
$ubuntuIP = wsl -d Ubuntu -- bash -c "hostname -I 2>/dev/null | awk '{print `$1}' || echo 'localhost'"
if ([string]::IsNullOrWhiteSpace($ubuntuIP) -or $ubuntuIP -eq "") {
    $ubuntuIP = "localhost"
}
Write-Host "[+] Ubuntu IP: $ubuntuIP" -ForegroundColor Green
Write-Host ""

# 서비스 디렉토리 생성 및 파일 생성
Write-Host "[*] 서비스 디렉토리 설정 중..." -ForegroundColor Cyan

$setupScript = @'
# 서비스 디렉토리 생성
mkdir -p ~/ChatGarment/chatgarment_service
cd ~/ChatGarment/chatgarment_service

# main.py 생성
cat > main.py << 'MAINEOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import uvicorn

chatgarment_root = Path("/home/ims/ChatGarment")
if chatgarment_root.exists():
    sys.path.insert(0, str(chatgarment_root))

app = FastAPI(title="ChatGarment Service API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chatgarment"}

@app.post("/api/v1/process")
async def process_image(image: UploadFile = File(...), text: Optional[str] = Form(None)):
    try:
        upload_dir = chatgarment_root / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        image_path = upload_dir / image.filename
        with open(image_path, "wb") as f:
            content = await image.read()
            f.write(content)
        return JSONResponse(content={"status": "success", "message": "이미지 수신됨", "image_path": str(image_path)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "error": str(e)})

if __name__ == "__main__":
    print(f"ChatGarment 경로: {chatgarment_root}")
    print(f"서비스 시작: http://0.0.0.0:9000")
    uvicorn.run(app, host="0.0.0.0", port=9000)
MAINEOF

chmod +x main.py

# 의존성 설치
echo "[*] 의존성 설치 중..."
python3 -m pip install --user fastapi uvicorn python-multipart 2>/dev/null || pip install fastapi uvicorn python-multipart

echo ""
echo "[+] 설정 완료!"
echo ""
'@

wsl -d Ubuntu -- bash -c $setupScript

Write-Host "[+] Ubuntu 서비스 설정 완료!" -ForegroundColor Green
Write-Host ""

# Windows 환경 변수 설정
Write-Host "[*] Windows 환경 변수 설정 중..." -ForegroundColor Cyan
[System.Environment]::SetEnvironmentVariable("CHATGARMENT_SERVICE_URL", "http://localhost:9000", "User")
[System.Environment]::SetEnvironmentVariable("USE_CHATGARMENT_SERVICE", "true", "User")
Write-Host "[+] 환경 변수 설정 완료" -ForegroundColor Green
Write-Host "   CHATGARMENT_SERVICE_URL=http://localhost:9000" -ForegroundColor Yellow
Write-Host ""

# 서비스 시작
Write-Host "[*] ChatGarment 서비스 시작 중..." -ForegroundColor Cyan
Write-Host "[*] 서비스 URL: http://localhost:9000" -ForegroundColor Yellow
Write-Host "[*] 종료하려면 Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# 백그라운드로 서비스 시작
$serviceStart = @'
cd ~/ChatGarment/chatgarment_service
nohup python3 main.py > service.log 2>&1 &
echo $! > service.pid
sleep 2
curl -s http://localhost:9000/health || echo "서비스 시작 중..."
echo "서비스 PID: $(cat service.pid)"
echo ""
echo "서비스가 백그라운드에서 실행 중입니다."
echo "로그 확인: tail -f service.log"
echo "서비스 중지: kill $(cat service.pid)"
'@

wsl -d Ubuntu -- bash -c $serviceStart

Write-Host ""
Write-Host "[+] 서비스 시작 완료!" -ForegroundColor Green
Write-Host ""
Write-Host "다음 단계:" -ForegroundColor Yellow
Write-Host "1. API 서버 재시작: .\restart_api_server.ps1" -ForegroundColor Cyan
Write-Host "2. 프론트엔드에서 이미지 업로드 테스트" -ForegroundColor Cyan
Write-Host ""

