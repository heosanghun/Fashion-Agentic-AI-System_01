# ChatGarment 독립 환경 설정 가이드

## ✅ 권장사항: 독립 환경으로 진행

**ChatGarment를 리눅스 환경에서 독립적으로 실행하는 것을 강력히 권장합니다.**

### 이유:

1. **리소스 효율성**
   - GPU 메모리 집약적 (16GB+)
   - CPU 시간 집약적 (수 초~수십 초)
   - 메인 시스템과 리소스 격리

2. **배포 유연성**
   - 메인 시스템은 어떤 환경에서든 실행 가능
   - ChatGarment만 리눅스 GPU 환경에서 실행
   - 독립적 확장 가능

3. **확장성**
   - 여러 ChatGarment 서버로 분산 가능
   - 부하 분산 가능
   - 배치 처리 전용 서버 구성 가능

4. **유지보수**
   - 독립적 업데이트
   - 버전 관리 분리
   - 장애 격리

## 🏗️ 아키텍처

### 현재 구조 (통합)
```
Fashion Agentic AI System
├── Custom UI (Frontend)
├── API Server (FastAPI)
├── Agent Runtime
├── F.LLM (InternVL2)
├── RAG Store
└── Extensions (ChatGarment) ← 여기서 직접 호출
```

### 권장 구조 (마이크로서비스)
```
Fashion Agentic AI System (Main)
├── Custom UI (Frontend)
├── API Server (FastAPI)
├── Agent Runtime
├── F.LLM (InternVL2)
├── RAG Store
└── Extensions (Service Client) ← HTTP API 호출
                                      │
                                      ▼
ChatGarment Service (독립 서비스)
├── API Server (FastAPI)
├── ChatGarment Pipeline
└── GarmentCodeRC
    └── 리눅스 환경 / GPU 서버
```

## 🚀 설정 방법

### 1단계: ChatGarment 서비스 설정 (리눅스)

```bash
# 프로젝트 루트에서
cd chatgarment_service

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
export DEVICE="cuda"
export OUTPUT_DIR="outputs/garments"
export HOST="0.0.0.0"
export PORT="8001"

# 서비스 시작
python main.py
```

### 2단계: 메인 시스템 설정

#### 옵션 A: 환경 변수 설정

```bash
# ChatGarment 서비스 URL 설정
export CHATGARMENT_SERVICE_URL="http://chatgarment-server:8001"
```

#### 옵션 B: 코드 수정

`agentic_system/tools/extensions.py`에서:

```python
# 기존 직접 호출 대신
from agentic_system.tools.extensions_service import (
    extensions_2d_to_3d_tool_via_service
)

# 도구 함수 교체
def extensions_2d_to_3d_tool(parameters, context):
    return extensions_2d_to_3d_tool_via_service(parameters, context)
```

### 3단계: 서비스 확인

```bash
# 서비스 헬스체크
curl http://localhost:8001/health

# 테스트 요청
curl -X POST "http://localhost:8001/api/v1/process" \
  -F "image=@/path/to/image.jpg"
```

## 📋 체크리스트

### ChatGarment 독립 서비스

- [ ] 리눅스 서버 설정 (GPU 권장)
- [ ] Python 가상환경 구성
- [ ] ChatGarment 의존성 설치
- [ ] 모델 체크포인트 준비
- [ ] API 서버 실행
- [ ] 헬스체크 통과

### 메인 시스템 연동

- [ ] ChatGarment 서비스 URL 설정
- [ ] 서비스 클라이언트 코드 적용
- [ ] 연결 테스트
- [ ] 에러 처리 확인

## 🔄 마이그레이션 전략

### 현재 → 독립 서비스

1. **현재**: `extensions.py`에서 직접 ChatGarment 호출
2. **변경**: `extensions.py`에서 서비스 클라이언트 사용
3. **결과**: ChatGarment는 독립 서비스로 실행

### 장점

- ✅ 코드 변경 최소화
- ✅ 기존 API 인터페이스 유지
- ✅ 점진적 마이그레이션 가능
- ✅ 롤백 용이

## ✨ 최종 권장사항

**✅ ChatGarment를 리눅스 환경에서 독립적으로 실행하세요.**

이유:
1. Fashion Agentic AI System은 이미 완성되어 있음
2. ChatGarment는 리소스 집약적이므로 독립 실행이 적합
3. 마이크로서비스 패턴으로 확장성 확보
4. 현재 코드 구조에서 쉽게 분리 가능

**구현 방법:**
1. `chatgarment_service/` 디렉토리에 독립 서비스 생성
2. 메인 시스템에서 HTTP API로 호출
3. 환경 변수로 서비스 URL 설정

이렇게 하면:
- 메인 시스템은 어떤 환경에서든 실행 가능
- ChatGarment만 리눅스 GPU 환경에서 독립 실행
- 확장성과 유지보수성 향상

