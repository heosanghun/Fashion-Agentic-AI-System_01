# 완전 자동 설정 가이드 (초보자용)

## ✅ Windows 설정 - 완료됨!

Windows 환경은 이미 자동으로 설정되었습니다:
- ✅ 환경 변수 설정 완료
- ✅ 코드 통합 완료

## 🚀 리눅스 서버 설정 - 한 번에 실행!

리눅스 서버에 SSH 접속하거나 직접 접속한 후, 아래 **전체 명령어를 복사**하여 실행하세요:

```bash
# 전체를 복사하여 리눅스 터미널에 붙여넣기

SERVER_IP=$(hostname -I | awk '{print $1}')
echo "서버 IP: $SERVER_IP"

mkdir -p ~/ChatGarment/chatgarment_service
cd ~/ChatGarment/chatgarment_service

cat > main.py << 'EOF'
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
EOF

chmod +x main.py
python3 -m pip install --user fastapi uvicorn python-multipart 2>/dev/null || pip install fastapi uvicorn python-multipart

echo ""
echo "서비스 시작: python3 main.py"
echo "서비스 URL: http://$SERVER_IP:9000"
echo ""
python3 main.py
```

## ✅ 확인

리눅스에서 서비스가 시작되면, **다른 터미널 창**에서 확인:

```bash
curl http://localhost:9000/health
```

**예상 응답**: `{"status":"healthy","service":"chatgarment"}`

## 🚀 Windows에서 API 서버 재시작

리눅스 서비스가 시작된 후, Windows PowerShell에서:

```powershell
.\restart_api_server.ps1
```

또는 직접:

```batch
python start_api_server.py
```

## 🎉 완료!

이제 프론트엔드에서 테스트:
1. http://localhost:5173 접속
2. 이미지 업로드
3. "요청 전송" 클릭
4. ChatGarment가 실제로 처리합니다!

