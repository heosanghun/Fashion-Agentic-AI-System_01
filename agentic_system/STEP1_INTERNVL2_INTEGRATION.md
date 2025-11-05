# 1단계: InternVL2 8B 모델 통합 완료

## ✅ 완료된 작업

### 1. InternVL2 Wrapper 구현
- **파일**: `agentic_system/models/internvl2_wrapper.py`
- **기능**:
  - InternVL2-8B 모델 로딩
  - 멀티모달 입력 처리 (텍스트 + 이미지)
  - 동적 이미지 전처리 (타일 분할)
  - 대화 형식 인터페이스
  - 이미지 분석 유틸리티

### 2. F.LLM (Agent 2) 통합
- **파일**: `agentic_system/core/f_llm.py`
- **변경사항**:
  - InternVL2-8B 모델 래퍼 통합
  - LLM 기반 계획 생성 기능 추가
  - 사용자 입력(텍스트/이미지)을 LLM에 전달
  - Fallback 메커니즘 (LLM 실패 시 규칙 기반)

### 3. Agent Runtime 업데이트
- **파일**: `agentic_system/core/agent_runtime.py`
- **변경사항**:
  - F.LLM에 사용자 입력 전달
  - 이미지 경로 전달

### 4. API 서버 업데이트
- **파일**: `agentic_system/api/main.py`
- **변경사항**:
  - InternVL2 모델 자동 초기화
  - CUDA 자동 감지

## 📋 모델 사용 방법

### 기본 사용

```python
from agentic_system.models import InternVL2Wrapper

# 모델 초기화
model = InternVL2Wrapper(
    model_path=None,  # 자동 경로 감지
    device="cuda"     # 또는 "cpu"
)

# 텍스트만 사용
response = model.generate_text(
    prompt="이 옷을 설명해주세요",
    max_new_tokens=512
)

# 이미지와 텍스트 함께 사용
response = model.analyze_image(
    image_path="/path/to/image.jpg",
    task="analyze_garment"
)

# 대화 형식
response, history = model.chat(
    text="<image>\n이 이미지를 자세히 설명해주세요.",
    image_path="/path/to/image.jpg"
)
```

### Agent 2에서 사용

F.LLM 컴포넌트가 자동으로 InternVL2 모델을 사용하여:
1. 사용자 입력 분석
2. 계획 생성 강화
3. 이미지 기반 의도 파악

## 🔧 설정

### 모델 경로
기본적으로 `model/InternVL2_8B` 경로를 자동 감지합니다.
다른 경로를 사용하려면:

```python
agent2 = FLLM(
    model_path="/custom/path/to/InternVL2_8B",
    use_llm=True
)
```

### 디바이스 설정
- CUDA 사용 가능 시 자동으로 GPU 사용
- CPU 사용: `device="cpu"`

### 메모리 최적화
8-bit 양자화를 사용하려면 `InternVL2Wrapper` 초기화 시:
```python
model = InternVL2Wrapper(
    load_in_8bit=True  # 메모리 절약
)
```

## ⚠️ 주의사항

1. **모델 크기**: InternVL2-8B는 약 16GB GPU 메모리 필요
2. **로딩 시간**: 첫 모델 로딩은 몇 분 소요될 수 있음
3. **Fallback**: 모델 로딩 실패 시 규칙 기반 모드로 자동 전환

## 🧪 테스트

```bash
# API 서버 실행
cd agentic_system
uvicorn api.main:app --reload --port 8000

# 테스트 요청
curl -X POST "http://localhost:8000/api/v1/request/json" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "이 옷을 입혀줘",
    "image_path": "/path/to/garment_image.jpg"
  }'
```

## 📝 다음 단계

1단계 완료 후, 다음 단계로 진행:
- **2단계**: ChatGarment 실제 통합
- **3단계**: 프론트엔드 UI 구현
- **4단계**: Vector DB 기반 RAG 구현

