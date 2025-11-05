# 🎯 최종 실행 가이드 (초보자용)

## ✅ Windows 설정 완료!

Windows 환경은 이미 설정되었습니다. 이제 리눅스 서버에서만 실행하면 됩니다.

## 📋 리눅스 서버에서 실행할 명령어

### 전체 명령어 (한 번에 복사하여 실행)

리눅스 서버에 접속한 후, 아래 **전체를 복사**하여 실행하세요:

```bash
# IP 확인
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "서버 IP: $SERVER_IP"

# 디렉토리 생성
mkdir -p ~/ChatGarment/chatgarment_service
cd ~/ChatGarment/chatgarment_service

# 서비스 파일 생성
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
    uvicorn.run(app, host="0.0.0.0", port=9000)
EOF

chmod +x main.py

# 의존성 설치
python3 -m pip install --user fastapi uvicorn python-multipart 2>/dev/null || pip install fastapi uvicorn python-multipart

# 서비스 시작
echo ""
echo "서비스 시작 중..."
python3 main.py
```

### 또는 백그라운드로 실행 (추천)

위 명령어를 실행한 후 `Ctrl+C`로 중단하고, 다음으로 실행:

```bash
nohup python3 main.py > service.log 2>&1 &
```

## ✅ 확인

서비스가 시작되었는지 확인:

```bash
curl http://localhost:9000/health
```

**예상 응답**: `{"status":"healthy","service":"chatgarment"}`

## 🚀 Windows에서 다음 단계

리눅스 서비스가 시작되면:

1. **API 서버 재시작**
   ```batch
   python start_api_server.py
   ```

2. **프론트엔드에서 테스트**
   - http://localhost:5173 접속
   - 이미지 업로드
   - "요청 전송" 클릭

## 💡 문제 발생 시

### 서비스에 연결할 수 없는 경우

Windows PowerShell에서:
```powershell
# 리눅스 IP 확인 시도
.\find_linux_server.ps1

# 또는 수동으로 IP 입력
$env:CHATGARMENT_SERVICE_URL = "http://리눅스IP:9000"
```

### 리눅스 IP 확인

리눅스에서:
```bash
hostname -I
```

결과를 Windows에서 환경 변수에 설정하세요.

