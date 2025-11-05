# ChatGarment 실제 통합 설치 가이드

## 📋 필수 요구사항

### 1. 시스템 요구사항
- Linux 환경 (권장)
- Python 3.8+
- CUDA 지원 GPU (권장, 최소 16GB VRAM)
- 최소 32GB RAM

### 2. 필수 패키지 설치

```bash
# 기본 Python 패키지
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers>=4.37.2
pip install Pillow opencv-python
pip install pyyaml easydict

# ChatGarment 추가 패키지
pip install flash-attn --no-build-isolation  # GPU 필수
pip install deepspeed  # 분산 학습용 (선택사항)

# GarmentCodeRC 의존성
# Maya, Qualoth 등이 필요할 수 있음 (선택사항)
```

### 3. 모델 체크포인트 확인

다음 경로에 모델이 있어야 합니다:

```bash
checkpoints/
├── llava-v1.5-7b/           # 기본 모델
└── try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final/
    └── pytorch_model.bin     # ChatGarment 파인튜닝 체크포인트
```

체크포인트가 없으면:
1. LLaVA modelling 체크포인트 다운로드
2. ChatGarment 파인튜닝 체크포인트 다운로드

### 4. GarmentCodeRC 설정

```bash
# GarmentCodeRC 경로 확인
cd GarmentCodeRC

# 필요한 경우 설치
pip install -e .
```

## 🧪 테스트 실행

### 1. 단일 이미지 테스트

```bash
cd agentic_system
python test_chatgarment_integration.py \
    --image /path/to/garment_image.jpg \
    --output outputs/test_garment \
    --device cuda
```

### 2. 예제 이미지로 테스트

```bash
# ChatGarment의 예제 이미지 사용
python test_chatgarment_integration.py \
    --image ChatGarment/data/eval_images/1.jpg \
    --output outputs/example_test \
    --device cuda
```

## 📊 예상 출력

성공 시 다음 파일들이 생성됩니다:

```
outputs/test_garment/valid_garment_XXXX/
├── gt_image.png                    # 원본 이미지
├── output.txt                      # 전체 출력 로그
├── valid_garment_XXXX_specification.json  # 패턴 JSON
└── valid_garment_XXXX_sim.obj      # 3D 메시 파일 (성공 시)
```

## ⚠️ 문제 해결

### GPU 메모리 부족
- `--device cpu` 사용 (느림)
- 8-bit 양자화 사용

### 모델 로딩 실패
- 체크포인트 경로 확인
- 모델 파일 권한 확인
- 디스크 공간 확인

### 3D 변환 실패
- GarmentCodeRC 설치 확인
- JSON specification 파일 형식 확인
- Maya/Qualoth 설정 확인 (필요한 경우)

## 🔍 검증 체크리스트

- [ ] ChatGarment 모델 로딩 성공
- [ ] 이미지 분석 (Step 1) 성공
- [ ] 패턴 코드 생성 (Step 2) 성공
- [ ] JSON specification 파일 생성
- [ ] GarmentCode 패턴 생성
- [ ] 3D 메시 파일 생성

## 📝 다음 단계

테스트 성공 후:
1. API 서버에 통합
2. 프론트엔드 연동
3. 배치 처리 기능 추가

