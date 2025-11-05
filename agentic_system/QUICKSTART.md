# Quick Start Guide

## Fashion Agentic AI System 빠른 시작 가이드

### 1. 환경 설정

```bash
# Python 3.8+ 필요
python --version

# 의존성 설치
pip install -r requirements.txt
```

### 2. 서버 실행

```bash
# API 서버 시작
cd agentic_system
uvicorn api.main:app --reload --port 8000
```

서버가 실행되면: `http://localhost:8000`

### 3. API 테스트

#### 3.1 JSON 형식 요청

```bash
curl -X POST "http://localhost:8000/api/v1/request/json" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "이 옷을 입혀줘",
    "image_path": "/path/to/image.jpg",
    "user_id": "user123",
    "session_id": "session456"
  }'
```

#### 3.2 Multipart Form 형식 요청

```bash
curl -X POST "http://localhost:8000/api/v1/request" \
  -F "text=이 옷을 입혀줘" \
  -F "image=@/path/to/image.jpg" \
  -F "user_id=user123" \
  -F "session_id=session456"
```

### 4. 세션 관리

#### 세션 기록 조회

```bash
curl "http://localhost:8000/api/v1/session/session456/history"
```

#### 세션 삭제

```bash
curl -X DELETE "http://localhost:8000/api/v1/session/session456"
```

### 5. 주요 엔드포인트

- `GET /` - 루트 엔드포인트
- `GET /health` - 헬스 체크
- `POST /api/v1/request` - 요청 처리 (multipart/form-data)
- `POST /api/v1/request/json` - 요청 처리 (JSON)
- `GET /api/v1/session/{session_id}/history` - 세션 기록 조회
- `DELETE /api/v1/session/{session_id}` - 세션 삭제

### 6. 시스템 흐름

1. 사용자가 텍스트/이미지 입력
2. Custom UI가 JSON Payload 생성
3. Agent Runtime (Agent 1)이 의도 분석 및 계획 수립
4. F.LLM (Agent 2)가 구체적 실행 계획 생성
5. 도구(Extensions/Functions) 실행
6. 자기 수정 루프를 통한 결과 검증
7. 최종 결과 반환

## 다음 단계

- [ ] ChatGarment 실제 통합
- [ ] 실제 LLM 연동 (OpenAI/Gemini)
- [ ] 프론트엔드 UI 개발
- [ ] Vector DB 기반 RAG 구현

