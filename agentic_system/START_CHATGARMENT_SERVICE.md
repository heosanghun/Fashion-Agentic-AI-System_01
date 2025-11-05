# ChatGarment 서비스 자동 시작 가이드

## 🚀 빠른 시작

### 리눅스 서버에서 실행할 명령어

리눅스 서버에 SSH 접속하거나 직접 접속한 후, 다음 명령어를 **순서대로** 실행하세요:

```bash
# 1. ChatGarment 디렉토리로 이동
cd ~/ChatGarment

# 2. 서비스 디렉토리 생성 (없는 경우)
mkdir -p chatgarment_service
cd chatgarment_service

# 3. main.py 파일 생성 (아래 내용 복사)
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

# ChatGarment 경로 설정
chatgarment_root = Path("/home/ims/ChatGarment")
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
async def process_image(
    image: UploadFile = File(...),
    text: Optional[str] = Form(None)
):
    try:
        upload_dir = chatgarment_root / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        image_path = upload_dir / image.filename
        with open(image_path, "wb") as f:
            content = await image.read()
            f.write(content)
        
        # 여기에 ChatGarment 처리 로직 추가
        # 현재는 간단한 응답 반환
        return JSONResponse(content={
            "status": "success",
            "message": "이미지가 수신되었습니다.",
            "image_path": str(image_path)
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
EOF

# 4. 의존성 설치
pip install fastapi uvicorn python-multipart

# 5. 서비스 시작
python3 main.py
```

## ✅ 확인

서비스가 시작되면 다음을 확인하세요:

```bash
# 다른 터미널에서 실행
curl http://localhost:9000/health
```

**예상 응답**: `{"status":"healthy","service":"chatgarment"}`

