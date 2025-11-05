# 리눅스 서버 ChatGarment 마이크로서비스 설정 가이드

## 📋 사전 준비

### 1. 리눅스 서버 IP 확인
리눅스 서버에서 실행:
```bash
hostname -I
# 또는
ip addr show | grep "inet "
```

**결과 예시**: `192.168.1.100` 또는 `10.0.0.5` 등

### 2. ChatGarment 디렉토리 확인
```bash
# ChatGarment 디렉토리 위치 확인
ls -la ~/ChatGarment
# 또는
ls -la /home/ims/ChatGarment
```

## 🚀 서비스 설정 및 시작

### 1. 서비스 디렉토리로 이동
```bash
cd ~/ChatGarment
# 또는 ChatGarment가 있는 실제 경로
```

### 2. 서비스 파일 복사
Windows에서 생성한 파일들을 리눅스로 복사하거나, 직접 생성:

```bash
# 마이크로서비스 디렉토리 생성
mkdir -p chatgarment_service
cd chatgarment_service

# main.py 파일 생성 (아래 내용 참고)
nano main.py
```

### 3. main.py 내용 (ChatGarment 경로 수정 필요)
실제 ChatGarment 경로에 맞게 수정:
```python
chatgarment_root = Path("/home/ims/ChatGarment")  # 실제 경로로 수정
```

### 4. 의존성 설치
```bash
# 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install fastapi uvicorn python-multipart
pip install torch transformers pillow
```

### 5. 서비스 시작
```bash
# 직접 실행
uvicorn main:app --host 0.0.0.0 --port 9000

# 또는 백그라운드 실행
nohup uvicorn main:app --host 0.0.0.0 --port 9000 > service.log 2>&1 &
```

### 6. 서비스 확인
```bash
# 헬스체크
curl http://localhost:9000/health

# 다른 머신에서 테스트 (리눅스 IP가 192.168.1.100인 경우)
curl http://192.168.1.100:9000/health
```

**예상 응답**: `{"status":"healthy","service":"chatgarment"}`

## 🔧 Windows 백엔드 설정

### 1. 환경 변수 설정
리눅스 IP를 확인한 후, Windows에서 환경 변수 설정:

```powershell
# PowerShell에서 실행
$env:CHATGARMENT_SERVICE_URL = "http://192.168.1.100:9000"  # 실제 리눅스 IP
$env:USE_CHATGARMENT_SERVICE = "true"
```

또는 `.env` 파일 생성:
```
CHATGARMENT_SERVICE_URL=http://192.168.1.100:9000
USE_CHATGARMENT_SERVICE=true
```

### 2. API 서버 재시작
```batch
python start_api_server.py
```

### 3. 연결 테스트
```powershell
# PowerShell에서 실행
Invoke-WebRequest -Uri "http://192.168.1.100:9000/health"
```

## ✅ 확인 사항

- [ ] 리눅스 IP 주소 확인
- [ ] ChatGarment 디렉토리 존재 확인
- [ ] 서비스 포트 9000 열림 확인
- [ ] Windows에서 리눅스 서비스 접근 가능 확인
- [ ] 환경 변수 설정 확인
- [ ] API 서버 재시작 완료

## 🔍 문제 해결

### 포트가 열리지 않는 경우
```bash
# 방화벽 확인
sudo ufw status
sudo ufw allow 9000/tcp
```

### 서비스 연결 실패
- 리눅스 IP 주소 확인
- 네트워크 연결 확인 (ping 테스트)
- 방화벽 설정 확인

