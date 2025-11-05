# Fashion Agentic AI System - Architecture Documentation

## 아키텍처 구조 설명

## 전체 시스템 아키텍처

본 시스템은 PDF 문서에 명시된 "Fashion Agentic AI System" 아키텍처를 코드로 구현한 것입니다.

## 주요 컴포넌트

### 1. Custom UI
- **위치**: `core/custom_ui.py`
- **역할**: 사용자 입력 처리 및 JSON Payload 생성
- **기능**:
  - 텍스트/이미지 입력 받기
  - 데이터 구조화 (JSON Payload)
  - 결과 포맷팅

### 2. Agent Runtime (Agent 1)
- **위치**: `core/agent_runtime.py`
- **역할**: 종합 감독 에이전트, 전체 프로세스 오케스트레이션
- **기능**:
  - 사용자 의도 분석 (Perception)
  - 추상적 계획 수립 (Judgment)
  - 도구 실행 오케스트레이션 (Action)
  - 자기 수정 루프 관리

### 3. F.LLM (Agent 2)
- **위치**: `core/f_llm.py`
- **역할**: 작업 지시 전문가 에이전트
- **기능**:
  - 추상적 계획을 구체적 실행 계획으로 변환
  - JSON 형식 실행 계획 생성
  - RAG 통합

### 4. Extensions (Tools)
- **위치**: `tools/extensions.py`
- **역할**: 2D to 3D 변환 도구
- **기능**:
  - 이미지 분석
  - 패턴 생성
  - 3D 변환
  - 렌더링

### 5. Functions (Tools)
- **위치**: `tools/functions.py`
- **역할**: 상품 검색 및 매칭
- **기능**:
  - 상품 검색
  - 추천 매칭

### 6. Data Stores (RAG)
- **위치**: `data_stores/rag.py`
- **역할**: 지식 검색 및 보강
- **현재**: Mock RAG (PoC 단계)
- **향후**: Vector DB 기반 RAG (Pilot 단계)

## 데이터 흐름

```
1. 사용자 입력 (텍스트 + 이미지)
   ↓
2. Custom UI: JSON Payload 생성
   ↓
3. Agent Runtime (Agent 1):
   - 의도 분석
   - 추상적 계획 수립
   ↓
4. F.LLM (Agent 2):
   - 구체적 실행 계획 생성 (JSON)
   ↓
5. Agent Runtime:
   - 도구 실행 오케스트레이션
   - Extensions/Functions 호출
   ↓
6. 자기 수정 루프:
   - 결과 평가
   - 실패 시 재시도
   ↓
7. 최종 결과 반환
```

## 디자인 패턴 구현

### PoC 단계 (5개 패턴)

1. **프롬프트 체이닝**: Agent 1 → Agent 2 → 도구 실행
2. **라우팅**: 의도 분석을 통한 경로 선택 (3D 생성 vs 추천)
3. **도구 사용**: Extensions/Functions 도구 호출
4. **반성**: 결과 평가 및 검증
5. **복구**: 실패 시 재시도

## 향후 확장 계획

- Pilot 1단계: 16개 추가 패턴
- Pilot 2단계: 패턴 융합 및 시너지 극대화

