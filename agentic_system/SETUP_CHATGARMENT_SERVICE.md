# ChatGarment 마이크로서비스 설정 가이드

## 🔍 1단계: 리눅스 서버 IP 확인

리눅스 서버에서 다음 명령어로 IP 주소를 확인하세요:

```bash
# 방법 1: ip 명령어
ip addr show | grep inet

# 방법 2: hostname 명령어
hostname -I

# 방법 3: ifconfig (설치되어 있는 경우)
ifconfig | grep inet
```

**예상 결과**: `192.168.x.x` 또는 `10.x.x.x` 형태의 IP 주소

## 📋 2단계: 리눅스 서버에서 ChatGarment 서비스 설정

### 1. ChatGarment 디렉토리 확인
```bash
# ChatGarment가 설치된 경로 확인
ls -la ~/ChatGarment
# 또는
ls -la /home/ims/ChatGarment
```

### 2. 마이크로서비스 디렉토리 생성
```bash
cd ~/ChatGarment  # 또는 ChatGarment 디렉토리 경로
mkdir -p chatgarment_service
cd chatgarment_service
```

### 3. 서비스 파일 생성
```bash
# main.py 파일 생성 (아래 내용 참고)
nano main.py
```

### 4. 의존성 설치
```bash
pip install fastapi uvicorn python-multipart
```

### 5. 서비스 시작
```bash
# 포트 9000에서 서비스 시작
uvicorn main:app --host 0.0.0.0 --port 9000
```

## 🔧 3단계: Windows 백엔드 설정

리눅스 IP를 확인한 후, Windows 백엔드에서 연결 설정을 업데이트하겠습니다.

