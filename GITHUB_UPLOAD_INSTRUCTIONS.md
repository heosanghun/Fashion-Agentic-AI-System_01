# GitHub 업로드 가이드

## 📋 현재 상태

- ✅ `.gitignore` 파일 준비 완료
- ✅ GitHub 저장소 생성 완료: https://github.com/heosanghun/Fashion-Agentic-AI-System_01
- ⚠️ Git 저장소 초기화 필요

---

## 🚀 업로드 단계별 가이드

### 1단계: Git 저장소 초기화

```powershell
# 프로젝트 루트 디렉토리에서 실행
cd D:\AI\ChatGarment

# Git 저장소 초기화
git init
```

### 2단계: 원격 저장소 연결

```powershell
# 원격 저장소 추가
git remote add origin https://github.com/heosanghun/Fashion-Agentic-AI-System_01.git

# 원격 저장소 확인
git remote -v
```

### 3단계: 브랜치 설정 (필요시)

```powershell
# 기본 브랜치를 main으로 설정
git branch -M main
```

### 4단계: 파일 추가

```powershell
# .gitignore가 제외할 파일은 자동으로 제외됨
# 모든 파일 추가 (자동으로 제외 파일은 제외됨)
git add .

# 추가된 파일 확인
git status
```

### 5단계: 커밋

```powershell
# 첫 번째 커밋
git commit -m "Initial commit: ChatGarment 프로젝트"

# 또는 상세한 커밋 메시지
git commit -m "Initial commit

- Agentic AI 시스템 구현
- ChatGarment 통합
- GarmentCodeRC 통합
- 프론트엔드 구현
- API 서버 구현"
```

### 6단계: GitHub에 푸시

```powershell
# GitHub에 업로드
git push -u origin main
```

**참고**: GitHub 인증이 필요할 수 있습니다.
- Personal Access Token 사용 권장
- 또는 GitHub CLI 사용

---

## ⚠️ 주의사항

### 업로드 전 확인사항

1. **`.gitignore` 확인**
   ```powershell
   # .gitignore 파일 확인
   cat .gitignore
   
   # 제외될 파일 확인
   git status --ignored
   ```

2. **민감 정보 확인**
   - `.env` 파일이 제외되는지 확인
   - API 키, 비밀번호 등이 포함되지 않았는지 확인

3. **모델 파일 확인**
   - `checkpoints/` 디렉토리가 제외되는지 확인
   - `model/InternVL2_8B/`의 가중치 파일이 제외되는지 확인

### 제외되는 파일 확인

다음 파일들은 **자동으로 제외**됩니다:
- ✅ `checkpoints/` - 모델 체크포인트
- ✅ `model/InternVL2_8B/*.safetensors` - 모델 가중치
- ✅ `outputs/` - 출력 파일
- ✅ `uploads/` - 업로드 파일
- ✅ `__pycache__/` - Python 캐시
- ✅ `node_modules/` - Node.js 패키지
- ✅ `*.log` - 로그 파일
- ✅ `.env` - 환경 변수

---

## 🔐 GitHub 인증

### 방법 1: Personal Access Token (권장)

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" 클릭
3. 권한 선택: `repo` (전체 저장소 접근)
4. 토큰 생성 후 복사
5. 푸시 시 비밀번호 대신 토큰 사용

### 방법 2: GitHub CLI

```powershell
# GitHub CLI 설치 후
gh auth login

# 푸시
git push -u origin main
```

---

## 📊 업로드 예상 시간

- **소스 코드만**: 약 1-2분
- **예제 데이터 포함**: 약 3-5분
- **모델 파일 제외**: ✅ (용량 문제 없음)

---

## ✅ 업로드 후 확인

1. **GitHub 저장소 확인**
   - https://github.com/heosanghun/Fashion-Agentic-AI-System_01 접속
   - 파일이 올바르게 업로드되었는지 확인

2. **제외 파일 확인**
   - `checkpoints/`, `outputs/` 등이 업로드되지 않았는지 확인

3. **README 업데이트**
   - 모델 다운로드 방법 추가
   - 설치 및 실행 방법 추가

---

## 🔄 업데이트 방법

향후 변경사항 업로드:

```powershell
# 변경사항 확인
git status

# 변경사항 추가
git add .

# 커밋
git commit -m "변경사항 설명"

# GitHub에 푸시
git push origin main
```

---

## 🆘 문제 해결

### 문제 1: 인증 오류

```
error: failed to push some refs to 'https://github.com/...'
```

**해결**:
- Personal Access Token 사용
- 또는 GitHub CLI 사용

### 문제 2: 큰 파일 오류

```
error: File too large
```

**해결**:
- `.gitignore` 확인
- 모델 파일이 제외되었는지 확인

### 문제 3: 원격 저장소 충돌

```
error: failed to push some refs
hint: Updates were rejected because the remote contains work...
```

**해결**:
```powershell
# 원격 저장소의 변경사항 가져오기
git pull origin main --allow-unrelated-histories

# 충돌 해결 후 다시 푸시
git push origin main
```

---

## 📝 참고

- **모델 파일**: GitHub에 직접 업로드하지 않음 (용량 문제)
- **설정 파일**: `.env.example` 파일 생성 권장
- **문서**: README.md 파일 업데이트 권장

---

## 🎯 빠른 시작 명령어 (복사해서 사용)

```powershell
# 1. Git 초기화
git init

# 2. 원격 저장소 연결
git remote add origin https://github.com/heosanghun/Fashion-Agentic-AI-System_01.git

# 3. 브랜치 설정
git branch -M main

# 4. 파일 추가
git add .

# 5. 커밋
git commit -m "Initial commit: ChatGarment 프로젝트"

# 6. 푸시 (인증 필요)
git push -u origin main
```

