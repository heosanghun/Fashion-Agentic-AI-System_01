# ChatGarment 마이크로서비스 통합 가이드

## 🎯 목표

Windows 환경의 Fashion Agentic AI System이 리눅스 서버에서 실행되는 ChatGarment 마이크로서비스를 사용하도록 설정합니다.

## 📋 단계별 가이드

### Step 1: 리눅스 서버 IP 확인

리눅스 서버에서 실행:
```bash
hostname -I
```

**결과 예시**: `192.168.1.100` (이 IP를 기록해두세요)

### Step 2: 리눅스 서버 설정

#### 2-1. ChatGarment 디렉토리 확인
```bash
ls -la ~/ChatGarment
# 실제 경로가 다르면 수정 필요
```

#### 2-2. 서비스 파일 생성

Windows에서 생성된 파일들을 리눅스로 복사하거나, 직접 생성:

1. `chatgarment_service/main.py` 파일 생성
2. ChatGarment 경로를 실제 경로로 수정:
   ```python
   chatgarment_root = Path("/home/ims/ChatGarment")  # 실제 경로로 수정
   ```

#### 2-3. 의존성 설치
```bash
cd ~/ChatGarment/chatgarment_service
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn python-multipart
pip install torch transformers pillow
```

#### 2-4. 서비스 시작
```bash
uvicorn main:app --host 0.0.0.0 --port 9000
```

#### 2-5. 서비스 확인
```bash
curl http://localhost:9000/health
```

**예상 응답**: `{"status":"healthy","service":"chatgarment"}`

### Step 3: Windows 환경 설정

#### 3-1. 환경 변수 설정 스크립트 실행

PowerShell에서:
```powershell
.\setup_windows_env.ps1
```

리눅스 IP를 입력하면 자동으로 환경 변수가 설정됩니다.

또는 수동 설정:
```powershell
$env:CHATGARMENT_SERVICE_URL = "http://192.168.1.100:9000"  # 실제 IP
$env:USE_CHATGARMENT_SERVICE = "true"
```

#### 3-2. 연결 테스트

```powershell
Invoke-WebRequest -Uri "http://192.168.1.100:9000/health"
```

**예상 응답**: `{"status":"healthy","service":"chatgarment"}`

### Step 4: API 서버 재시작

```batch
python start_api_server.py
```

환경 변수가 적용된 상태로 서버가 시작됩니다.

### Step 5: 프론트엔드 테스트

1. 브라우저에서 `http://localhost:5173` 접속
2. 의류 이미지 업로드
3. "요청 전송" 클릭
4. 결과 확인 (이번에는 실제 ChatGarment가 처리함)

## ✅ 확인 체크리스트

- [ ] 리눅스 IP 확인
- [ ] 리눅스에서 서비스 실행 확인
- [ ] Windows에서 리눅스 서비스 접근 가능 확인
- [ ] 환경 변수 설정 확인
- [ ] API 서버 재시작 완료
- [ ] 프론트엔드에서 이미지 업로드 테스트 성공

## 🔍 문제 해결

### 리눅스 서비스에 연결할 수 없는 경우

1. **IP 주소 확인**
   ```bash
   # 리눅스에서
   hostname -I
   ```

2. **방화벽 확인**
   ```bash
   # 리눅스에서
   sudo ufw status
   sudo ufw allow 9000/tcp
   ```

3. **서비스 실행 확인**
   ```bash
   # 리눅스에서
   curl http://localhost:9000/health
   ```

4. **Windows에서 ping 테스트**
   ```powershell
   ping 192.168.1.100  # 실제 리눅스 IP
   ```

### 서비스는 연결되지만 처리 실패

1. **ChatGarment 경로 확인**
   - `main.py`의 `chatgarment_root` 경로가 실제 경로와 일치하는지 확인

2. **체크포인트 파일 확인**
   - ChatGarment 체크포인트 파일이 존재하는지 확인

3. **로그 확인**
   - 리눅스 서버의 콘솔 로그 확인
   - 오류 메시지 확인

## 📝 참고사항

- 리눅스 서버는 **포트 9000**을 열어야 합니다
- Windows와 리눅스가 같은 네트워크에 있어야 합니다
- 환경 변수는 **새로운 터미널 세션**에서만 적용됩니다
- API 서버를 재시작해야 환경 변수가 적용됩니다

