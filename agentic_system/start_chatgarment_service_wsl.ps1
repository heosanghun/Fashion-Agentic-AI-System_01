# WSL에서 ChatGarment 서비스 시작

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "ChatGarment 서비스 시작 (WSL)" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

# WSL Ubuntu 확인
$wslList = wsl --list --verbose 2>&1

if ($wslList -notmatch "Ubuntu") {
    Write-Host "[!] Ubuntu가 설치되지 않았습니다." -ForegroundColor Red
    Write-Host "[*] .\setup_wsl_ubuntu.ps1 실행하여 설치하세요." -ForegroundColor Yellow
    exit 1
}

Write-Host "[+] WSL Ubuntu 확인 완료" -ForegroundColor Green
Write-Host ""

# 서비스 디렉토리 확인 및 생성
Write-Host "[*] 서비스 디렉토리 확인 중..." -ForegroundColor Cyan

$checkScript = @"
if [ ! -d ~/ChatGarment/chatgarment_service ]; then
    echo '서비스 디렉토리가 없습니다. 생성 중...'
    mkdir -p ~/ChatGarment/chatgarment_service
    cd ~/ChatGarment/chatgarment_service
    
    # main.py 생성 (기존 스크립트와 동일)
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
MAIN_EOF

    chmod +x main.py
    python3 -m pip install --user fastapi uvicorn python-multipart 2>/dev/null || pip install fastapi uvicorn python-multipart
    echo '설정 완료'
fi

cd ~/ChatGarment/chatgarment_service
if [ ! -f main.py ]; then
    echo 'main.py 파일이 없습니다.'
    exit 1
fi
echo '서비스 준비 완료'
"@

wsl -d Ubuntu -- bash -c $checkScript

Write-Host ""
Write-Host "[*] 서비스 시작 중..." -ForegroundColor Cyan
Write-Host "[*] 서비스 URL: http://localhost:9000" -ForegroundColor Yellow
Write-Host "[*] 종료하려면 Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# 서비스 시작
wsl -d Ubuntu -- bash -c "cd ~/ChatGarment/chatgarment_service && python3 main.py"

