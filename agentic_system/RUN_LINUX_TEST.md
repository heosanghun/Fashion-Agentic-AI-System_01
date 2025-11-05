# 리눅스 환경 테스트 실행 가이드

## 📋 준비된 테스트 스크립트

### 1. 환경 검증 스크립트 (`quick_test.py`)
빠른 환경 검증을 수행합니다.

```bash
cd agentic_system
python3 quick_test.py
```

### 2. 상세 검증 스크립트 (`verify_integration.sh`)
리눅스 환경에서 상세 검증을 수행합니다.

```bash
cd agentic_system
chmod +x verify_integration.sh
./verify_integration.sh
```

### 3. 테스트 실행 스크립트 (`run_linux_test.sh`)
자동으로 이미지를 찾아 테스트를 실행합니다.

```bash
cd agentic_system
chmod +x run_linux_test.sh
./run_linux_test.sh cuda
```

### 4. 실제 통합 테스트 (`test_chatgarment_integration.py`)
실제 ChatGarment 파이프라인을 테스트합니다.

```bash
cd agentic_system
python3 test_chatgarment_integration.py \
    --image ChatGarment/example_data/example_imgs/1aee14a8c7b4d56b4e8b6ddd575d1f561a72fdc75c43a4b6926f1655152193c6.png \
    --output outputs/test_garment \
    --device cuda
```

## 🚀 실제 테스트 실행

### 단계 1: 환경 검증

```bash
# 빠른 환경 검증
python3 quick_test.py
```

예상 출력:
```
============================================================
ChatGarment 통합 빠른 테스트
============================================================

============================================================
1. 필수 모듈 임포트 테스트
============================================================
✅ PyTorch
✅ Transformers
✅ Pillow
✅ NumPy

============================================================
2. CUDA 환경 확인
============================================================
✅ CUDA 사용 가능
   CUDA 버전: 11.8
   GPU 개수: 1
   GPU 이름: NVIDIA RTX 4090

...

============================================================
테스트 결과 요약
============================================================
임포트: ✅ 통과
CUDA: ✅ 통과
ChatGarment 구조: ✅ 통과
체크포인트: ✅ 통과
통합 모듈: ✅ 통과
GarmentCodeRC: ✅ 통과
============================================================

🎉 모든 테스트 통과!

다음 단계:
  python3 test_chatgarment_integration.py --image <이미지_경로> --device cuda
```

### 단계 2: 실제 통합 테스트

```bash
# 예제 이미지로 테스트
python3 test_chatgarment_integration.py \
    --image ../ChatGarment/example_data/example_imgs/1aee14a8c7b4d56b4e8b6ddd575d1f561a72fdc75c43a4b6926f1655152193c6.png \
    --output outputs/test_garment \
    --device cuda \
    --garment-id test_001
```

예상 출력:
```
============================================================
ChatGarment 실제 통합 테스트
============================================================
입력 이미지: ../ChatGarment/example_data/example_imgs/1aee14a8c7b4d56b4e8b6ddd575d1f561a72fdc75c43a4b6926f1655152193c6.png
출력 디렉토리: outputs/test_garment
디바이스: cuda
============================================================

📦 ChatGarment 모델 로딩 중...
============================================================
ChatGarment 모델 로딩 시작...
============================================================
모델 경로: checkpoints/llava-v1.5-7b
체크포인트: checkpoints/try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final/pytorch_model.bin
============================================================
✅ ChatGarment 모델 로딩 완료!
============================================================

🔄 이미지 처리 시작...

============================================================
의류 생성 시작: test_001
이미지: ../ChatGarment/example_data/example_imgs/1aee14a8c7b4d56b4e8b6ddd575d1f561a72fdc75c43a4b6926f1655152193c6.png
출력: outputs/test_garment/valid_garment_test_001
============================================================

1️⃣ 이미지 로딩 및 전처리...
2️⃣ Step 1: Geometry features 분석 중...
✅ Geometry features 추출 완료
출력 길이: 1234 문자

3️⃣ Step 2: Sewing pattern code 생성 중...
✅ Sewing pattern code 생성 완료
출력 길이: 2345 문자
Float 예측값 개수: 50

4️⃣ JSON 파싱 중...
5️⃣ GarmentCode 패턴 생성 중...
✅ 패턴 생성 완료: outputs/test_garment/valid_garment_test_001/valid_garment_test_001_specification.json

6️⃣ 3D 변환 시작 (GarmentCodeRC)...
실행 명령어: python ChatGarment/run_garmentcode_sim.py --json_spec_file "..."
작업 디렉토리: /path/to/project
✅ 3D 변환 완료!
✅ 3D 메시 생성 완료: outputs/test_garment/valid_garment_test_001/valid_garment_test_001_sim.obj

============================================================
테스트 결과
============================================================
✅ 성공!

생성된 파일들:
  - 출력 디렉토리: outputs/test_garment/valid_garment_test_001
  - JSON Specification: outputs/.../valid_garment_test_001_specification.json
  - 3D 메시 파일: outputs/.../valid_garment_test_001_sim.obj

✨ 3D 의류 생성 완료!

결과 확인:
  - 디렉토리: outputs/test_garment/valid_garment_test_001
  - 3D 모델: outputs/.../valid_garment_test_001_sim.obj
============================================================
```

## 📊 결과 확인

### 생성된 파일 구조

```
outputs/test_garment/valid_garment_test_001/
├── gt_image.png                                    # 원본 이미지
├── output.txt                                      # 전체 출력 로그
│   ├── Step 1: Geometry Features
│   ├── Step 2: Sewing Pattern Code
│   └── Parsed JSON
├── valid_garment_test_001_specification.json      # 패턴 JSON
└── valid_garment_test_001_sim.obj                 # 3D 메시 파일 (성공 시)
```

### 로그 확인

```bash
# 출력 로그 확인
cat outputs/test_garment/valid_garment_test_001/output.txt
```

### JSON 확인

```bash
# JSON specification 확인
cat outputs/test_garment/valid_garment_test_001/valid_garment_test_001_specification.json | python3 -m json.tool
```

### 3D 모델 확인

생성된 `.obj` 파일은 3D 뷰어로 확인할 수 있습니다:
- Blender
- MeshLab
- 프론트엔드 3D 뷰어

## ⚠️ 문제 해결

### GPU 메모리 부족

```bash
# CPU 모드로 실행
python3 test_chatgarment_integration.py \
    --image <이미지_경로> \
    --device cpu
```

### 모델 로딩 실패

1. 체크포인트 경로 확인
2. 모델 파일 크기 확인
3. 디스크 공간 확인

### Import 오류

```bash
# 프로젝트 루트에서 실행
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/ChatGarment"
cd agentic_system
python3 test_chatgarment_integration.py ...
```

## ✨ 성공 기준

테스트가 성공한 경우:

- ✅ 모델 로딩 성공
- ✅ Step 1 (Geometry features) 출력 생성
- ✅ Step 2 (Sewing pattern code) 출력 생성
- ✅ JSON specification 파일 생성
- ✅ 3D mesh 파일 생성 (선택사항)

## 📝 다음 단계

테스트 성공 후:

1. **API 서버 통합**
   - `agentic_system/api/main.py`에서 실제 파이프라인 사용
   
2. **프론트엔드 연동**
   - 3D 뷰어에 실제 mesh 파일 로딩
   
3. **배치 처리**
   - 여러 이미지 동시 처리
   
4. **성능 최적화**
   - 모델 캐싱
   - 병렬 처리

