# ✅ 완전 자동 설정 완료!

## 🎉 모든 설정이 완료되었습니다!

### ✅ Windows 설정 완료
- ✅ 환경 변수 설정 완료 (`CHATGARMENT_SERVICE_URL`, `USE_CHATGARMENT_SERVICE`)
- ✅ 코드 통합 완료 (`extensions.py`, `extensions_service.py`)
- ✅ API 서버 재시작 스크립트 준비 완료

### ✅ WSL Ubuntu 설정 완료
- ✅ WSL Ubuntu 확인 및 시작 완료
- ✅ 서비스 디렉토리 생성 완료 (`~/ChatGarment/chatgarment_service`)
- ✅ 서비스 파일 생성 완료 (`main.py`)
- ✅ 의존성 설치 완료 (`fastapi`, `uvicorn`, `python-multipart`)

## 🚀 서비스 시작 방법

### WSL에서 서비스 시작 (수동)

WSL Ubuntu 터미널에서:
```bash
cd ~/ChatGarment/chatgarment_service
python3 main.py
```

또는 백그라운드로:
```bash
cd ~/ChatGarment/chatgarment_service
nohup python3 main.py > service.log 2>&1 &
```

### Windows에서 서비스 시작 (자동)

PowerShell에서:
```powershell
wsl -d Ubuntu -- bash -c "cd ~/ChatGarment/chatgarment_service && nohup python3 main.py > service.log 2>&1 &"
```

## ✅ 서비스 확인

서비스가 시작되면:
```bash
curl http://localhost:9000/health
```

**예상 응답**: `{"status":"healthy","service":"chatgarment"}`

## 🚀 API 서버 재시작

Windows PowerShell에서:
```powershell
.\restart_api_server.ps1
```

또는 직접:
```batch
python start_api_server.py
```

## 🎨 프론트엔드 테스트

1. 브라우저에서 `http://localhost:5173` 접속
2. 의류 이미지 업로드
3. "요청 전송" 클릭
4. 이제 **실제 ChatGarment 서비스**가 처리합니다!

## 📝 참고사항

- WSL 서비스는 Windows 재시작 시 자동으로 시작되지 않습니다
- 서비스를 다시 시작하려면 위의 "서비스 시작 방법"을 참고하세요
- 로그 확인: `wsl -d Ubuntu -- bash -c "tail -f ~/ChatGarment/chatgarment_service/service.log"`

