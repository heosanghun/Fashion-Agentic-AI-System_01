# GitHub 업로드 가이드

## 📋 현재 상태

**모든 파일은 현재 위치에 그대로 보존됩니다.**

- ✅ 파일 이동 없음
- ✅ 구조 변경 없음
- ✅ `.gitignore`로 제외 파일 관리

## 🔒 .gitignore로 제외되는 파일

다음 파일들은 **현재 위치에 그대로 있지만** GitHub에 업로드되지 않습니다:

### 1. 모델 파일 (용량이 너무 큼)
- `checkpoints/` - 전체 디렉토리
- `model/InternVL2_8B/*.safetensors` - 모델 가중치 파일
- `model/InternVL2_8B/*.bin` - 모델 바이너리 파일
- `*.pt`, `*.pth`, `*.ckpt` - 모든 체크포인트 파일

### 2. 출력 및 업로드 파일
- `outputs/` - 실행 결과 파일
- `uploads/` - 사용자 업로드 파일
- `ChatGarment/outputs/`
- `ChatGarment/uploads/`
- `ChatGarment/runs/`

### 3. 로그 파일
- `*.log` - 모든 로그 파일
- `*.jsonl` - JSON Lines 로그
- `browser_test_result_*.json` - 테스트 결과
- `test_*_response.json` - 테스트 응답

### 4. 캐시 및 빌드 파일
- `__pycache__/` - Python 캐시
- `*.pyc`, `*.pyo` - 컴파일된 Python 파일
- `dist/`, `build/` - 빌드 결과
- `*.egg-info/` - 패키지 메타데이터

### 5. 의존성 패키지
- `node_modules/` - Node.js 패키지
- `venv/`, `.venv/`, `env/` - 가상환경

### 6. 기타
- `.env` - 환경 변수 파일
- `.vscode/`, `.idea/` - IDE 설정
- `*.dll`, `*.so`, `*.dylib` - 컴파일된 바이너리

## ✅ GitHub에 업로드되는 파일

다음 파일들은 **현재 위치에 그대로 있고** GitHub에 업로드됩니다:

### 1. 소스 코드
- `agentic_system/**/*.py` - 모든 Python 소스 파일
- `ChatGarment/**/*.py` - ChatGarment 소스 코드
- `GarmentCodeRC/**/*.py` - GarmentCodeRC 소스 코드
- `chatgarment_service/**/*.py` - 서비스 소스 코드

### 2. 설정 파일
- `*.toml`, `*.yaml`, `*.json` - 설정 파일 (모델 가중치 제외)
- `requirements.txt` - 의존성 파일
- `package.json` - Node.js 패키지 설정
- `vite.config.js` - Vite 설정

### 3. 문서
- `*.md` - 모든 마크다운 문서
- `README.md` - 프로젝트 설명
- `LICENSE` - 라이센스 파일

### 4. 예제 데이터
- `ChatGarment/example_data/` - 예제 이미지 및 JSON
- `ChatGarment/docs/images/` - 문서 이미지
- `GarmentCodeRC/assets/` - 설정 파일 및 예제

### 5. 프론트엔드
- `agentic_system/frontend/src/` - React 소스 코드
- `agentic_system/frontend/index.html` - HTML 파일
- `agentic_system/frontend/public/` - 정적 파일

### 6. 스크립트
- `*.sh` - Shell 스크립트
- `*.ps1` - PowerShell 스크립트
- `*.bat` - 배치 파일

### 7. 모델 설정 파일 (가중치 제외)
- `model/InternVL2_8B/*.py` - 모델 아키텍처 코드
- `model/InternVL2_8B/*.json` - 모델 설정 파일
- `model/InternVL2_8B/*.txt` - 텍스트 설정 파일

## 🚀 GitHub 업로드 방법

### 1. Git 저장소 초기화 (처음 한 번만)

```bash
# Git 저장소 초기화
git init

# 원격 저장소 추가 (GitHub 저장소 URL 사용)
git remote add origin https://github.com/your-username/your-repo.git
```

### 2. 파일 추가 및 커밋

```bash
# .gitignore 확인
git status

# 모든 파일 추가 (자동으로 .gitignore 제외 파일은 제외됨)
git add .

# 커밋
git commit -m "Initial commit: ChatGarment 프로젝트"

# 원격 저장소에 푸시
git push -u origin main
```

### 3. 업로드 전 확인

```bash
# .gitignore가 제대로 작동하는지 확인
git status

# 제외되어야 할 파일이 목록에 나타나지 않아야 함
# 예: checkpoints/, outputs/, uploads/, node_modules/ 등
```

## 📊 예상 저장소 크기

- **소스 코드만**: 약 50-100 MB
- **예제 데이터 포함**: 약 200-500 MB
- **모델 파일 포함하지 않음**: ✅ (용량 문제 해결)

## ⚠️ 주의사항

1. **모델 파일은 별도 관리**
   - `checkpoints/`와 `model/InternVL2_8B/`의 가중치 파일은 GitHub에 업로드되지 않음
   - README에 모델 다운로드 방법을 명시해야 함

2. **환경 변수 파일**
   - `.env` 파일은 업로드되지 않음
   - `.env.example` 파일을 만들어서 템플릿 제공 권장

3. **민감 정보**
   - API 키, 비밀번호 등은 절대 커밋하지 않음
   - `.gitignore`에 이미 `.env` 파일이 포함되어 있음

## 🔍 .gitignore 확인 방법

```bash
# 특정 파일이 제외되는지 확인
git check-ignore -v checkpoints/
git check-ignore -v model/InternVL2_8B/
git check-ignore -v outputs/
git check-ignore -v node_modules/

# 모든 제외 파일 확인
git status --ignored
```

## 📝 README에 추가할 내용

GitHub 저장소의 README에 다음 내용을 추가하세요:

```markdown
## 모델 파일 다운로드

이 저장소에는 모델 가중치 파일이 포함되어 있지 않습니다. 
다음 링크에서 모델 파일을 다운로드하세요:

- ChatGarment 체크포인트: [다운로드 링크]
- InternVL2-8B 모델: [다운로드 링크]

다운로드 후 다음 위치에 저장하세요:
- `checkpoints/try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final/pytorch_model.bin`
- `model/InternVL2_8B/`
```

## ✅ 최종 확인

업로드 전에 다음을 확인하세요:

- [ ] `.gitignore` 파일이 프로젝트 루트에 있음
- [ ] `checkpoints/` 디렉토리가 제외됨
- [ ] `model/InternVL2_8B/`의 가중치 파일이 제외됨
- [ ] `outputs/`, `uploads/` 디렉토리가 제외됨
- [ ] `node_modules/` 디렉토리가 제외됨
- [ ] 로그 파일이 제외됨
- [ ] `.env` 파일이 제외됨

**모든 파일은 현재 위치에 그대로 보존되며, `.gitignore`를 통해 GitHub에 업로드되지 않습니다.**

