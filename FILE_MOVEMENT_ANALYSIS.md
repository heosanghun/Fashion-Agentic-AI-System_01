# 파일 이동 영향 분석 및 해결 방법

## 📋 분석 결과

### ✅ 업로드 제외 파일을 별도 폴더로 이동해도 되는 경우

다음 파일들은 **별도 폴더로 이동해도 실행 오류가 발생하지 않습니다**:

#### 1. **출력 파일** (`outputs/`, `uploads/`)
- ✅ **이동 가능**: 실행 시 새로 생성되므로 이동해도 문제 없음
- ✅ **실행 영향**: 없음 (실행 시 자동 생성)

#### 2. **로그 파일** (`*.log`, `*.jsonl`)
- ✅ **이동 가능**: 실행 시 새로 생성되므로 이동해도 문제 없음
- ✅ **실행 영향**: 없음 (실행 시 자동 생성)

#### 3. **캐시 파일** (`__pycache__/`, `*.pyc`)
- ✅ **이동 가능**: 실행 시 자동 재생성되므로 이동해도 문제 없음
- ✅ **실행 영향**: 없음 (자동 재생성)

#### 4. **의존성 패키지** (`node_modules/`)
- ✅ **이동 가능**: `npm install`로 재설치 가능
- ✅ **실행 영향**: 없음 (재설치 가능)

---

### ⚠️ 업로드 제외 파일을 별도 폴더로 이동하면 문제가 발생하는 경우

다음 파일들은 **별도 폴더로 이동하면 실행 오류가 발생할 수 있습니다**:

#### 1. **모델 체크포인트** (`checkpoints/`)

**현재 경로 참조:**
```python
# agentic_system/tools/chatgarment_integration.py
checkpoint_path = str(
    project_root / "checkpoints" / 
    "try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final" / 
    "pytorch_model.bin"
)

# agentic_system/chatgarment_service/main.py
possible_checkpoint_paths = [
    project_root / "checkpoints" / "try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final" / "pytorch_model.bin",
    project_root.parent / "checkpoints" / "try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final" / "pytorch_model.bin",
    chatgarment_root / "checkpoints" / "try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final" / "pytorch_model.bin",
    Path("D:/AI/ChatGarment/checkpoints/try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final/pytorch_model.bin"),
]
```

**문제:**
- ❌ 체크포인트 경로가 하드코딩되어 있음
- ❌ 일부는 상대 경로 사용 (`project_root / "checkpoints"`)
- ❌ 일부는 절대 경로 사용 (`D:/AI/ChatGarment/...`)

**영향:**
- 🔴 **치명적 오류**: 모델 파일을 찾지 못하면 Mock 모드로 동작하거나 오류 발생
- 🔴 **기능 제한**: ChatGarment 모델 기능 사용 불가

#### 2. **InternVL2 모델** (`model/InternVL2_8B/`)

**현재 경로 참조:**
```python
# agentic_system/models/internvl2_wrapper.py
if model_path is None:
    project_root = Path(__file__).parent.parent.parent
    model_path = str(project_root / "model" / "InternVL2_8B")
```

**문제:**
- ⚠️ 상대 경로 사용 (`project_root / "model" / "InternVL2_8B"`)
- ⚠️ 모델이 없으면 규칙 기반 모드로 폴백 (기능 제한)

**영향:**
- 🟡 **기능 제한**: InternVL2 모델 기능 사용 불가 (규칙 기반 모드로 동작)
- 🟡 **치명적 오류는 아님**: 폴백 모드로 실행 가능

---

## 🔧 해결 방법

### 방법 1: 심볼릭 링크 사용 (권장)

**Windows:**
```powershell
# 관리자 권한으로 실행
New-Item -ItemType SymbolicLink -Path "checkpoints" -Target "D:\AI\ChatGarment_Models\checkpoints"
New-Item -ItemType SymbolicLink -Path "model" -Target "D:\AI\ChatGarment_Models\model"
```

**Linux/Mac:**
```bash
ln -s /path/to/external/models/checkpoints ./checkpoints
ln -s /path/to/external/models/model ./model
```

**장점:**
- ✅ 코드 수정 불필요
- ✅ 기존 경로 참조 유지
- ✅ GitHub에 심볼릭 링크만 포함 (실제 파일은 제외)

---

### 방법 2: 환경 변수 사용

**1. 환경 변수 설정**

Windows:
```powershell
$env:CHATGARMENT_CHECKPOINTS_DIR = "D:\AI\ChatGarment_Models\checkpoints"
$env:INTERNVL2_MODEL_DIR = "D:\AI\ChatGarment_Models\model\InternVL2_8B"
```

Linux:
```bash
export CHATGARMENT_CHECKPOINTS_DIR="/path/to/external/models/checkpoints"
export INTERNVL2_MODEL_DIR="/path/to/external/models/model/InternVL2_8B"
```

**2. 코드 수정**

```python
# agentic_system/tools/chatgarment_integration.py
import os

# 환경 변수에서 경로 읽기
checkpoints_base = os.getenv(
    "CHATGARMENT_CHECKPOINTS_DIR",
    str(project_root / "checkpoints")  # 기본값
)
checkpoint_path = str(
    Path(checkpoints_base) / 
    "try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final" / 
    "pytorch_model.bin"
)
```

**장점:**
- ✅ 유연한 경로 설정
- ✅ 환경별로 다른 경로 사용 가능

**단점:**
- ⚠️ 코드 수정 필요
- ⚠️ 환경 변수 설정 필요

---

### 방법 3: 설정 파일 사용

**1. 설정 파일 생성** (`config/model_paths.yaml`)

```yaml
models:
  checkpoints_dir: "D:/AI/ChatGarment_Models/checkpoints"
  internvl2_dir: "D:/AI/ChatGarment_Models/model/InternVL2_8B"
  
  # 또는 상대 경로
  # checkpoints_dir: "../ChatGarment_Models/checkpoints"
  # internvl2_dir: "../ChatGarment_Models/model/InternVL2_8B"
```

**2. 설정 파일 로딩 코드 추가**

```python
import yaml
from pathlib import Path

def load_model_paths():
    """모델 경로 설정 파일 로드"""
    config_path = Path(__file__).parent.parent / "config" / "model_paths.yaml"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('models', {})
    else:
        # 기본값 (프로젝트 루트 기준)
        project_root = Path(__file__).parent.parent.parent
        return {
            'checkpoints_dir': str(project_root / "checkpoints"),
            'internvl2_dir': str(project_root / "model" / "InternVL2_8B")
        }
```

**장점:**
- ✅ 설정 파일로 관리 (버전 관리 가능)
- ✅ 환경별 설정 파일 분리 가능

**단점:**
- ⚠️ 코드 수정 필요
- ⚠️ 설정 파일 관리 필요

---

### 방법 4: .gitignore만 사용 (가장 간단)

**권장 방법**: 모델 파일을 그대로 두고 `.gitignore`로만 제외

**장점:**
- ✅ 코드 수정 불필요
- ✅ 기존 경로 유지
- ✅ GitHub에 업로드되지 않음

**단점:**
- ⚠️ 로컬 저장소에 큰 파일 존재 (용량 문제)

---

## 📊 파일별 이동 영향 요약

| 파일/디렉토리 | 이동 가능 | 실행 영향 | 해결 방법 |
|-------------|---------|---------|---------|
| `checkpoints/` | ❌ | 🔴 치명적 | 심볼릭 링크 또는 환경 변수 |
| `model/InternVL2_8B/` | ❌ | 🟡 기능 제한 | 심볼릭 링크 또는 환경 변수 |
| `outputs/` | ✅ | ✅ 없음 | 그대로 이동 가능 |
| `uploads/` | ✅ | ✅ 없음 | 그대로 이동 가능 |
| `__pycache__/` | ✅ | ✅ 없음 | 그대로 이동 가능 |
| `node_modules/` | ✅ | ✅ 없음 | 재설치 가능 |
| `*.log` | ✅ | ✅ 없음 | 그대로 이동 가능 |

---

## 🎯 권장 작업 순서

### 1단계: 안전하게 이동 가능한 파일 이동

```bash
# 출력 파일 이동
mkdir -p ../ChatGarment_External/outputs
mv outputs/* ../ChatGarment_External/outputs/

# 업로드 파일 이동
mkdir -p ../ChatGarment_External/uploads
mv uploads/* ../ChatGarment_External/uploads/

# 로그 파일 이동
mkdir -p ../ChatGarment_External/logs
find . -name "*.log" -type f -exec mv {} ../ChatGarment_External/logs/ \;
```

### 2단계: 모델 파일 처리 (선택)

#### 옵션 A: 심볼릭 링크 사용 (권장)

```powershell
# 모델 파일을 외부 디렉토리로 이동
Move-Item -Path "checkpoints" -Destination "D:\AI\ChatGarment_Models\checkpoints"
Move-Item -Path "model" -Destination "D:\AI\ChatGarment_Models\model"

# 심볼릭 링크 생성
New-Item -ItemType SymbolicLink -Path "checkpoints" -Target "D:\AI\ChatGarment_Models\checkpoints"
New-Item -ItemType SymbolicLink -Path "model" -Target "D:\AI\ChatGarment_Models\model"
```

#### 옵션 B: .gitignore만 사용 (가장 간단)

```bash
# 아무것도 이동하지 않고 .gitignore만 설정
# 이미 .gitignore 파일에 포함되어 있음
```

### 3단계: .gitignore 확인

```bash
# .gitignore 파일 확인
cat .gitignore

# 모델 파일이 제외되어 있는지 확인
git check-ignore checkpoints/
git check-ignore model/InternVL2_8B/
```

---

## 🔍 테스트 방법

이동 후 다음을 테스트하세요:

### 1. ChatGarment 모델 로딩 테스트

```python
# agentic_system/debug_chatgarment_load.py 실행
python agentic_system/debug_chatgarment_load.py
```

**성공 조건:**
- ✅ 체크포인트 발견
- ✅ 모델 로딩 완료

### 2. InternVL2 모델 로딩 테스트

```python
from agentic_system.models import InternVL2Wrapper

model = InternVL2Wrapper()
model.load_model()  # 오류 없이 로딩되어야 함
```

**성공 조건:**
- ✅ 모델 경로 발견
- ✅ 모델 로딩 완료

### 3. 전체 시스템 테스트

```bash
# API 서버 시작
cd agentic_system
python start_api_server.py

# 프론트엔드에서 이미지 업로드 테스트
# 3D 변환 기능이 정상 작동하는지 확인
```

---

## ⚠️ 주의사항

1. **절대 경로 하드코딩**: 일부 코드에 `D:/AI/ChatGarment/...` 같은 절대 경로가 있음
   - 이런 경우 심볼릭 링크가 가장 효과적

2. **Mock 모드**: 모델을 찾지 못하면 Mock 모드로 동작
   - Mock 모드에서는 실제 모델 기능 사용 불가
   - 오류는 발생하지 않지만 기능 제한

3. **상대 경로**: 대부분의 코드가 `project_root` 기준 상대 경로 사용
   - 프로젝트 구조는 유지해야 함

---

## 📝 결론

**가장 안전한 방법:**

1. **출력/로그 파일**: 그대로 이동 가능 (✅)
2. **모델 파일**: 심볼릭 링크 사용 또는 .gitignore만 사용 (⚠️)
3. **코드 수정 최소화**: 심볼릭 링크 사용 권장

**치명적 오류 발생 가능성:**
- 모델 파일을 이동하고 경로 수정 없이 실행하면 **기능 제한 또는 오류 발생**
- 하지만 **심볼릭 링크를 사용하면 코드 수정 없이 해결 가능**

