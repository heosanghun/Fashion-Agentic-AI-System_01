#!/bin/bash
# 리눅스 서버에서 이 스크립트를 실행하면 자동으로 설정됩니다

echo "==========================================================="
echo "ChatGarment 서비스 자동 설치"
echo "==========================================================="

# IP 확인
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "[*] 서버 IP: $SERVER_IP"
echo ""

# ChatGarment 경로
CHATGARMENT_DIR="/home/ims/ChatGarment"
SERVICE_DIR="$CHATGARMENT_DIR/chatgarment_service"

# 디렉토리 생성
mkdir -p "$SERVICE_DIR"
cd "$SERVICE_DIR"

# main.py 생성
cat > main.py << 'MAINPY_EOF'
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
    uvicorn.run(app, host="0.0.0.0", port=9000)
MAINPY_EOF

chmod +x main.py

# 의존성 설치
echo "[*] 의존성 설치 중..."
python3 -m pip install --user fastapi uvicorn python-multipart 2>/dev/null || pip install fastapi uvicorn python-multipart

echo ""
echo "[+] 설치 완료!"
echo ""
echo "서비스 시작:"
echo "  python3 $SERVICE_DIR/main.py"
echo ""
echo "서비스 URL: http://$SERVER_IP:9000"
echo ""

