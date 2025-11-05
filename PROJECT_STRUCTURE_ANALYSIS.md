# ChatGarment 프로젝트 전체 구조 분석 문서

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [전체 디렉토리 구조](#전체-디렉토리-구조)
3. [주요 모듈별 상세 분석](#주요-모듈별-상세-분석)
4. [시스템 아키텍처](#시스템-아키텍처)
5. [작동 원리 및 특징](#작동-원리-및-특징)

---

## 프로젝트 개요

이 프로젝트는 **패션 Agentic AI 가상 피팅 POC** 시스템으로, 다음과 같은 주요 기능을 제공합니다:
- 이미지/텍스트 기반 의류 분석 및 생성
- 2D 이미지에서 3D 의류 모델 생성
- Agentic AI 시스템을 통한 지능형 작업 오케스트레이션
- React 기반 프론트엔드 UI

---

## 전체 디렉토리 구조

```
ChatGarment/
├── agentic_system/              # Agentic AI 시스템 (메인 시스템)
│   ├── api/                     # FastAPI 서버
│   ├── core/                    # 핵심 컴포넌트 (Agent 1, Agent 2)
│   ├── tools/                   # 도구 (Extensions & Functions)
│   ├── data_stores/             # RAG 데이터 저장소
│   ├── models/                  # AI 모델 래퍼
│   ├── frontend/                # React 프론트엔드
│   └── chatgarment_service/     # ChatGarment 마이크로서비스
│
├── ChatGarment/                 # ChatGarment 모델 (LLaVA 기반)
│   ├── llava/                   # LLaVA 모델 구현
│   ├── scripts/                 # 실행 스크립트
│   └── outputs/                 # 생성 결과
│
├── GarmentCodeRC/              # GarmentCode 라이브러리 (2D→3D 변환)
│   ├── pygarment/              # 핵심 라이브러리
│   ├── assets/                 # 자산 (패턴, 바디 모델 등)
│   └── gui/                    # GUI 인터페이스
│
├── checkpoints/                 # AI 모델 체크포인트
│   ├── llava-v1.5-7b/
│   └── try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final/
│
├── model/                       # InternVL2 모델
│   └── InternVL2_8B/
│
├── outputs/                     # 시스템 출력
│   ├── patterns/               # 2D 패턴
│   ├── 3d_models/              # 3D 모델
│   └── renders/                # 렌더링 이미지
│
└── uploads/                      # 사용자 업로드 파일
```

---

## 주요 모듈별 상세 분석

### 1. agentic_system/ (메인 Agentic AI 시스템)

#### 1.1 api/ - FastAPI 서버
**파일**: `api/main.py`

**역할**:
- FastAPI 기반 REST API 서버
- 사용자 요청 수신 및 처리
- Agent Runtime과 통신

**주요 기능**:
- `/api/v1/request` - 메인 요청 엔드포인트
- `/api/v1/file` - 파일 서빙
- `/health` - 헬스체크
- CORS 미들웨어 설정

**작동 원리**:
1. 사용자 요청(이미지/텍스트) 수신
2. Agent Runtime에 전달
3. 처리 결과 반환

---

#### 1.2 core/ - 핵심 컴포넌트

##### `core/agent_runtime.py` - Agent Runtime (Agent 1)
**역할**: 종합 감독 에이전트
- 사용자 요청 분석 및 추상적 계획 수립
- Agent 2에게 계획 전달 및 결과 수신
- 도구 실행 오케스트레이션
- 자기 수정 루프 관리

**주요 클래스**:
- `AgentRuntime`: 메인 런타임 클래스
- `AbstractPlan`: 추상적 작업 계획 모델

**작동 원리**:
```
[사용자 요청] → [인식(Perception)] → [판단(Judgment)] → [행동(Action)]
     ↓              ↓                      ↓                  ↓
  요청 분석    추상적 계획 수립      Agent 2에게 전달      도구 실행
```

**특징**:
- 메모리 관리 통합
- 도구 레지스트리 시스템
- 재시도 로직 포함

---

##### `core/f_llm.py` - F.LLM (Agent 2)
**역할**: 작업 지시 전문가 에이전트
- Agent 1의 추상적 계획을 구체적 실행 계획으로 변환
- JSON 형식의 실행 계획 생성
- InternVL2-8B 모델 통합

**주요 클래스**:
- `FLLM`: Foundation LLM 에이전트
- `ExecutionPlan`: 실행 계획 모델

**작동 원리**:
1. 추상적 계획 수신
2. InternVL2 모델을 통한 분석
3. 구체적 단계별 실행 계획 생성 (JSON)
4. 실행 계획 반환

**특징**:
- 멀티모달 입력 지원 (이미지 + 텍스트)
- CUDA/CPU 자동 디바이스 감지
- 규칙 기반 폴백 모드

---

##### `core/memory.py` - 메모리 관리
**역할**: 대화 및 세션 메모리 관리
- 단기 메모리 (세션별)
- 장기 메모리 (전역)
- 대화 기록 저장

---

##### `core/custom_ui.py` - Custom UI
**역할**: UI 컴포넌트 인터페이스
- 사용자 입력 처리
- 결과 시각화

---

#### 1.3 tools/ - 도구 (Extensions & Functions)

##### `tools/extensions.py` - 2D to 3D 변환 도구
**역할**: 2D 이미지를 3D 모델로 변환
- ChatGarment 파이프라인 통합
- 패턴 생성 및 3D 변환

**주요 클래스**:
- `Extensions2DTo3D`: 메인 변환 도구

**작동 원리**:
1. 이미지 분석 (ChatGarment 모델)
2. 2D 패턴 생성 (JSON)
3. GarmentCodeRC를 통한 3D 메시 생성
4. 렌더링 이미지 생성

**특징**:
- 지연 로딩 (Lazy Loading)
- Mock 모드 지원
- 실제 ChatGarment 파이프라인 통합

---

##### `tools/functions.py` - 상품 검색 도구
**역할**: 상품 검색 및 매칭
- PoC 단계에서는 Mock 데이터 사용
- 상품 추천 기능

**주요 클래스**:
- `ProductSearchFunction`: 상품 검색 함수

---

##### `tools/chatgarment_integration.py` - ChatGarment 통합
**역할**: ChatGarment 파이프라인 래퍼
- ChatGarment 모델 로딩 및 실행
- 이미지 분석 및 패턴 생성

---

#### 1.4 data_stores/ - RAG 데이터 저장소

##### `data_stores/rag.py` - RAG Store
**역할**: Retrieval-Augmented Generation
- PoC 단계에서는 Mock RAG
- 지식 베이스 검색

**주요 클래스**:
- `MockRAG`: Mock RAG 구현

**특징**:
- 의류 유형, 스타일, 색상 가이드라인 제공
- 키워드 매칭 기반 검색

---

##### `data_stores/rag_vector.py` - Vector RAG
**역할**: 벡터 기반 RAG (향후 확장용)

---

#### 1.5 models/ - AI 모델 래퍼

##### `models/internvl2_wrapper.py` - InternVL2 래퍼
**역할**: InternVL2-8B 모델 래퍼
- 모델 로딩 및 추론
- 멀티모달 입력 처리

---

#### 1.6 frontend/ - React 프론트엔드

**구조**:
```
frontend/
├── src/
│   ├── App.jsx              # 메인 앱 컴포넌트
│   ├── components/
│   │   ├── ImageUpload.jsx   # 이미지 업로드
│   │   ├── StatusBar.jsx    # 상태 표시
│   │   ├── ResultViewer.jsx # 결과 표시
│   │   └── ModelViewer.jsx  # 3D 모델 뷰어
│   └── main.jsx             # 진입점
├── vite.config.js           # Vite 설정
└── package.json             # 의존성
```

**기술 스택**:
- React 18
- Vite
- Three.js (3D 모델 뷰어)
- Axios (API 통신)

**작동 원리**:
1. 사용자 입력 (이미지/텍스트)
2. API 서버로 요청 전송
3. 결과 수신 및 표시
4. 3D 모델 뷰어로 시각화

---

### 2. ChatGarment/ - ChatGarment 모델

#### 2.1 llava/ - LLaVA 모델 구현

**주요 파일**:
- `llava/garment_utils_v2.py`: 의류 생성 유틸리티
- `llava/garmentcode_utils.py`: GarmentCode 통합
- `llava/garmentcodeRC_utils.py`: GarmentCodeRC 통합
- `llava/model/`: 모델 아키텍처
- `llava/mm_utils.py`: 멀티모달 유틸리티

**작동 원리**:
1. 이미지 입력 받기
2. LLaVA 모델로 이미지 분석
3. GarmentCode JSON 패턴 생성
4. 결과 반환

---

#### 2.2 scripts/ - 실행 스크립트

**주요 스크립트**:
- `evaluate_garment_v2_imggen_2step.sh`: 이미지 기반 생성 (2단계)
- `evaluate_garment_v2_textgen.sh`: 텍스트 기반 생성
- `evaluate_garment_v2_demo_edit.sh`: 의류 편집

---

#### 2.3 run_garmentcode_sim.py - 시뮬레이션 실행
**역할**: 2D 패턴을 3D 메시로 변환
- GarmentCodeRC 통합
- 시뮬레이션 실행
- 렌더링 생성

---

### 3. GarmentCodeRC/ - GarmentCode 라이브러리

#### 3.1 pygarment/ - 핵심 라이브러리

**주요 모듈**:
- `pygarment/garmentcode/`: 패턴 생성 엔진
- `pygarment/meshgen/`: 3D 메시 생성
- `pygarment/pattern/`: 패턴 렌더링

**작동 원리**:
1. JSON 패턴 사양 읽기
2. 패널 및 엣지 생성
3. 3D 메시 생성 (BoxMesh)
4. 시뮬레이션 실행
5. 렌더링

---

#### 3.2 assets/ - 자산

**구조**:
- `assets/garment_programs/`: 의류 프로그램 (Python 코드)
- `assets/bodies/`: 바디 모델 (OBJ, YAML)
- `assets/design_params/`: 디자인 파라미터
- `assets/Patterns/`: 예제 패턴 JSON

---

#### 3.3 gui/ - GUI 인터페이스

**파일**: `gui/callbacks.py`
**역할**: NiceGUI 기반 웹 인터페이스
- 2D 패턴 시각화
- 3D 뷰어
- 파라미터 조정

**기술**:
- NiceGUI (Python 웹 프레임워크)
- Cairo (2D 렌더링)

---

### 4. checkpoints/ - AI 모델 체크포인트

**모델**:
- `llava-v1.5-7b`: LLaVA 1.5 7B 모델
- `try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final`: ChatGarment 파인튜닝 모델

---

### 5. outputs/ - 시스템 출력

**구조**:
- `outputs/patterns/`: 생성된 2D 패턴 (JSON)
- `outputs/3d_models/`: 생성된 3D 모델 (OBJ, GLB)
- `outputs/renders/`: 렌더링 이미지 (PNG)

---

## 시스템 아키텍처

### 전체 시스템 흐름

```
[사용자 입력]
    ↓
[프론트엔드 (React)]
    ↓
[API 서버 (FastAPI)]
    ↓
[Agent Runtime (Agent 1)]
    ↓
[F.LLM (Agent 2) - InternVL2-8B]
    ↓
[도구 실행]
    ├─ Extensions (2D→3D)
    │   ├─ ChatGarment (이미지 분석)
    │   ├─ 패턴 생성 (JSON)
    │   └─ GarmentCodeRC (3D 변환)
    │
    └─ Functions (상품 검색)
    ↓
[결과 반환]
    ↓
[프론트엔드 시각화]
```

### Agent 간 상호작용

```
Agent 1 (Agent Runtime)
    │
    ├─ 추상적 계획 수립
    │
    └─→ Agent 2 (F.LLM)
            │
            ├─ 구체적 실행 계획 생성
            │
            └─→ 도구 실행
                    │
                    ├─ Extensions (2D→3D)
                    └─ Functions (검색)
```

---

## 작동 원리 및 특징

### 1. Agentic AI 시스템

**특징**:
- **멀티 에이전트 아키텍처**: Agent 1 (오케스트레이션) + Agent 2 (실행 계획)
- **자기 수정 루프**: 결과 검증 및 재시도
- **도구 기반 확장성**: 플러그인 방식의 도구 시스템

**작동 원리**:
1. **인식 (Perception)**: 사용자 요청 분석
2. **판단 (Judgment)**: 추상적 계획 → 구체적 실행 계획
3. **행동 (Action)**: 도구 실행 및 결과 생성

---

### 2. ChatGarment 통합

**특징**:
- **멀티모달 AI**: 이미지 + 텍스트 입력 처리
- **LLaVA 기반**: Vision-Language 모델 사용
- **패턴 생성**: GarmentCode JSON 형식 출력

**작동 원리**:
1. 이미지 분석 (의류 유형, 스타일, 색상 등)
2. 텍스트 프롬프트 생성
3. ChatGarment 모델로 패턴 생성
4. JSON 형식으로 출력

---

### 3. 2D → 3D 변환 파이프라인

**특징**:
- **GarmentCodeRC 통합**: 산업용 의류 생성 라이브러리
- **물리 시뮬레이션**: 실제 의류 드레이핑 시뮬레이션
- **렌더링**: 고품질 렌더링 이미지 생성

**작동 원리**:
1. JSON 패턴 사양 파싱
2. 패널 및 엣지 생성
3. 3D 메시 생성 (BoxMesh)
4. 물리 시뮬레이션 실행
5. 렌더링

---

### 4. 프론트엔드

**특징**:
- **React 기반**: 모던 웹 프레임워크
- **3D 뷰어**: Three.js 기반 3D 모델 시각화
- **실시간 상태 표시**: 처리 진행 상황 표시

**작동 원리**:
1. 사용자 입력 수집
2. API 서버로 요청 전송
3. WebSocket 또는 폴링으로 상태 확인
4. 결과 수신 및 시각화

---

### 5. 메모리 관리

**특징**:
- **세션별 메모리**: 사용자별 대화 기록 유지
- **장기 메모리**: 학습 데이터 축적 (향후)

**작동 원리**:
- 단기 메모리: 세션 ID 기반 대화 기록
- 장기 메모리: 전역 지식 저장소 (향후 RAG 통합)

---

## 주요 기술 스택

### Backend
- **FastAPI**: REST API 서버
- **PyTorch**: AI 모델 실행
- **InternVL2-8B**: Vision-Language 모델
- **LLaVA**: ChatGarment 기반 모델

### Frontend
- **React 18**: UI 프레임워크
- **Vite**: 빌드 도구
- **Three.js**: 3D 모델 뷰어
- **Axios**: HTTP 클라이언트

### 3D 처리
- **GarmentCodeRC**: 의류 생성 라이브러리
- **PyGarment**: 패턴 생성 엔진
- **물리 시뮬레이션**: 의류 드레이핑

---

## 파일별 상세 역할

### 핵심 파일

1. **agentic_system/api/main.py**
   - FastAPI 메인 서버
   - API 엔드포인트 정의
   - CORS 설정

2. **agentic_system/core/agent_runtime.py**
   - Agent 1 (오케스트레이션)
   - 도구 실행 관리
   - 자기 수정 루프

3. **agentic_system/core/f_llm.py**
   - Agent 2 (실행 계획 생성)
   - InternVL2 모델 통합
   - JSON 실행 계획 생성

4. **agentic_system/tools/extensions.py**
   - 2D→3D 변환 도구
   - ChatGarment 통합
   - GarmentCodeRC 호출

5. **ChatGarment/llava/garment_utils_v2.py**
   - ChatGarment 유틸리티
   - 패턴 생성 로직

6. **GarmentCodeRC/pygarment/garmentcode/**
   - 패턴 생성 엔진
   - 패널, 엣지, 인터페이스 관리

7. **GarmentCodeRC/run_garmentcode_sim.py**
   - 3D 시뮬레이션 실행
   - 메시 생성 및 렌더링

---

## 결론

이 프로젝트는 **Agentic AI + 멀티모달 AI + 3D 생성**을 결합한 종합적인 패션 가상 피팅 시스템입니다. 

주요 특징:
- ✅ 멀티 에이전트 아키텍처
- ✅ 멀티모달 입력 처리 (이미지 + 텍스트)
- ✅ 2D → 3D 자동 변환
- ✅ 실제 물리 시뮬레이션
- ✅ 모던 웹 UI

향후 확장 가능성:
- Vector RAG 통합
- 실제 상품 검색 API 연동
- 더 많은 의류 유형 지원

