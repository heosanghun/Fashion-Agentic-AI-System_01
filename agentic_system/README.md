# Fashion Agentic AI System

패션 Agentic AI 가상 피팅 POC 개발 - 시스템 아키텍처 구현

## 아키텍처 개요

본 시스템은 "인식-판단-행동"의 3단계 흐름을 중심으로 구성된 멀티 에이전트 시스템입니다.

### 주요 구성 요소

1. **Custom UI**: 사용자 입력 처리 및 결과 시각화
2. **Agent Runtime**: AI 에이전트의 판단 및 계획 실행 (오케스트레이션 엔진)
3. **F.LLM (Foundation LLM)**: 사용자의 의도를 파악하고 작업 계획 생성 (Agent 2)
4. **Data Stores (RAG)**: 에이전트의 판단 정확도를 높이기 위한 외부 지식 저장소
5. **Extensions (Tools)**: 2D/3D 변환 등 실제 작업을 수행하는 독립적인 기술 모듈
6. **Function (Tools)**: 상품 검색 및 매칭 기능

### 시스템 흐름

```
[사용자 입력] 
    ↓
[Custom UI] → JSON Payload
    ↓
[Agent Runtime] → 계획 수립
    ↓
[F.LLM (Agent 2)] → 실행 계획 생성 (JSON)
    ↓
[Extensions/Function] → 도구 실행
    ↓
[결과 검증 및 재시도 루프]
    ↓
[최종 결과] → Custom UI
```

## 프로젝트 구조

```
agentic_system/
├── core/                    # 핵심 컴포넌트
│   ├── __init__.py
│   ├── custom_ui.py        # Custom UI 컴포넌트
│   ├── agent_runtime.py    # Agent Runtime (Agent 1)
│   ├── f_llm.py           # F.LLM (Agent 2)
│   └── memory.py          # 메모리 관리
├── tools/                   # 도구 (Extensions & Functions)
│   ├── __init__.py
│   ├── extensions.py       # 2D to 3D 변환 도구
│   └── functions.py        # 상품 검색 및 매칭 도구
├── data_stores/            # 데이터 저장소 (RAG)
│   ├── __init__.py
│   └── rag.py             # RAG 구현 (Mock for PoC)
├── api/                    # FastAPI 서버
│   ├── __init__.py
│   ├── main.py            # 메인 API 서버
│   └── schemas.py         # 데이터 스키마
├── frontend/               # 프론트엔드 (선택사항)
│   └── ...
└── config/                 # 설정 파일
    ├── config.yaml
    └── agent_config.json
```

## 설치 및 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn api.main:app --reload --port 8000
```

## 개발 계획

1. ✅ 프로젝트 구조 설계
2. ⏳ Custom UI 컴포넌트 구현
3. ⏳ Agent Runtime 구현
4. ⏳ F.LLM (Agent 2) 구현
5. ⏳ Extensions 구현 (2D to 3D)
6. ⏳ Function 구현 (상품 검색)
7. ⏳ Data Stores (RAG) 구현
8. ⏳ 자기 수정 루프 구현
9. ⏳ FastAPI 서버 통합
10. ⏳ 프론트엔드 UI 구현

