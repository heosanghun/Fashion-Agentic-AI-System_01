#!/bin/bash
# 리눅스 서버에서 실행할 완전 자동화 스크립트
# 전체를 복사하여 리눅스 터미널에 붙여넣기 후 실행

echo "==========================================================="
echo "ChatGarment 마이크로서비스 자동 설정 및 시작"
echo "==========================================================="
echo ""

# IP 확인
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "[*] 서버 IP: $SERVER_IP"
echo ""

# ChatGarment 경로
CHATGARMENT_DIR="/home/ims/ChatGarment"
SERVICE_DIR="$CHATGARMENT_DIR/chatgarment_service"

echo "[*] 서비스 디렉토리 생성: $SERVICE_DIR"
mkdir -p "$SERVICE_DIR"
cd "$SERVICE_DIR"

# main.py 파일 생성
echo "[*] 서비스 파일 생성 중..."
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

# 의존성 설치
echo "[*] 의존성 설치 중..."
python3 -m pip install --user fastapi uvicorn python-multipart 2>/dev/null || pip install fastapi uvicorn python-multipart

echo ""
echo "[+] 설치 완료!"
echo ""
echo "==========================================================="
echo "서비스 시작 중..."
echo "==========================================================="
echo "[*] 서비스 URL: http://$SERVER_IP:9000"
echo "[*] 헬스체크: curl http://localhost:9000/health"
echo "[*] 종료하려면 Ctrl+C"
echo ""
echo "백그라운드 실행을 원하면: nohup python3 main.py > service.log 2>&1 &"
echo ""

# 서비스 시작
python3 main.py

