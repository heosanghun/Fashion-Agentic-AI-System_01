# ChatGarment 독립 서비스

ChatGarment를 독립 마이크로서비스로 실행하는 서비스입니다.

## 🚀 실행 방법

### 1. 환경 설정

```bash
# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정 (선택사항)

```bash
export DEVICE="cuda"  # 또는 "cpu"
export OUTPUT_DIR="outputs/garments"
export HOST="0.0.0.0"
export PORT="8001"
```

### 3. 서비스 시작

```bash
python main.py
```

또는 uvicorn 직접 실행:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

## 📡 API 엔드포인트

### 헬스체크

```bash
curl http://localhost:8001/health
```

### 이미지 처리 (파일 업로드)

```bash
curl -X POST "http://localhost:8001/api/v1/process" \
  -F "image=@/path/to/image.jpg" \
  -F "garment_id=test_001"
```

### 이미지 처리 (경로 지정)

```bash
curl -X POST "http://localhost:8001/api/v1/process/path" \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "/path/to/image.jpg",
    "garment_id": "test_001",
    "output_dir": "outputs/test"
  }'
```

## 🔗 메인 시스템 연동

메인 시스템에서 이 서비스를 호출하려면:

```python
import requests

def call_chatgarment_service(image_path: str):
    """ChatGarment 서비스 호출"""
    service_url = "http://localhost:8001"
    
    with open(image_path, 'rb') as f:
        response = requests.post(
            f"{service_url}/api/v1/process",
            files={"image": f}
        )
    
    return response.json()
```

## 🐳 Docker 지원 (선택사항)

```dockerfile
FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## ⚙️ 설정

- `DEVICE`: cuda 또는 cpu
- `OUTPUT_DIR`: 출력 디렉토리
- `HOST`: 서버 호스트 (기본: 0.0.0.0)
- `PORT`: 서버 포트 (기본: 8001)

## 📝 로그

서비스는 자동으로 로그를 출력합니다:
- 모델 로딩 상태
- 요청 처리 상태
- 오류 발생 시 상세 로그

