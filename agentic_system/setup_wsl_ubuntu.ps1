# WSL Ubuntu 완전 자동 설정

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "WSL Ubuntu 자동 설정" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

# WSL Ubuntu 확인
$ubuntuExists = wsl --list --verbose 2>&1 | Select-String "Ubuntu"

if (-not $ubuntuExists) {
    Write-Host "[*] Ubuntu 설치 중..." -ForegroundColor Cyan
    wsl --install -d Ubuntu
    Write-Host "[+] Ubuntu 설치 시작됨 (재부팅 후 계속)" -ForegroundColor Green
    Write-Host ""
    Write-Host "[!] 재부팅 후 이 스크립트를 다시 실행하세요." -ForegroundColor Yellow
    exit
}

Write-Host "[+] Ubuntu 발견!" -ForegroundColor Green
Write-Host ""

# Ubuntu에서 사용자 설정 (최초 1회)
Write-Host "[*] Ubuntu 사용자 설정 확인 중..." -ForegroundColor Cyan

# 계정 정보 설정
$username = "ims"
$password = "@q1w2e3r4"

# Ubuntu에서 명령어 실행
Write-Host "[*] Ubuntu에서 서비스 설정 중..." -ForegroundColor Cyan

$setupScript = @"
# ChatGarment 서비스 자동 설정
SERVER_IP=`$(hostname -I | awk '{print `$1}')
echo '서버 IP: $SERVER_IP'

mkdir -p ~/ChatGarment/chatgarment_service
cd ~/ChatGarment/chatgarment_service

cat > main.py << 'MAIN_EOF'
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

chatgarment_root = Path("/home/$username/ChatGarment")
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
MAIN_EOF

chmod +x main.py
python3 -m pip install --user fastapi uvicorn python-multipart 2>/dev/null || pip install fastapi uvicorn python-multipart

echo ""
echo "설정 완료!"
echo "서비스 시작: cd ~/ChatGarment/chatgarment_service && python3 main.py"
"@

# WSL에서 스크립트 실행
wsl -d Ubuntu -- bash -c $setupScript

Write-Host ""
Write-Host "[+] Ubuntu 설정 완료!" -ForegroundColor Green
Write-Host ""
Write-Host "[*] 서비스 시작 명령어:" -ForegroundColor Cyan
Write-Host "   wsl -d Ubuntu -- bash -c 'cd ~/ChatGarment/chatgarment_service && python3 main.py &'" -ForegroundColor White

