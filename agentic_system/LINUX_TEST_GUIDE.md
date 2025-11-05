# 리눅스 환경 테스트 가이드

## 🚀 빠른 시작

### 1단계: 환경 검증

```bash
# 검증 스크립트 실행
cd agentic_system
./verify_integration.sh
```

또는 빠른 테스트:

```bash
python3 quick_test.py
```

### 2단계: 실제 통합 테스트

```bash
# 자동 이미지 탐색 및 테스트
./run_linux_test.sh cuda

# 또는 이미지 경로 지정
./run_linux_test.sh cuda /path/to/image.jpg outputs/test
```

### 3단계: 상세 테스트

```bash
python3 test_chatgarment_integration.py \
    --image /path/to/garment_image.jpg \
    --output outputs/test_garment \
    --device cuda \
    --garment-id test_001
```

## 📋 검증 체크리스트

### 사전 준비

- [ ] Python 3.8+ 설치
- [ ] PyTorch 설치 (CUDA 지원)
- [ ] 필수 패키지 설치
  ```bash
  pip install torch transformers Pillow numpy opencv-python
  ```
- [ ] ChatGarment 디렉토리 존재
- [ ] 모델 체크포인트 다운로드
- [ ] GarmentCodeRC 설정

### 테스트 실행

- [ ] 환경 검증 통과
- [ ] 테스트 이미지 준비
- [ ] 테스트 스크립트 실행
- [ ] 결과 확인:
  - [ ] JSON specification 생성
  - [ ] 3D mesh 파일 생성
  - [ ] 출력 디렉토리 확인

## 🔍 문제 해결

### GPU 메모리 부족

```bash
# CPU 모드로 실행
python3 test_chatgarment_integration.py \
    --image /path/to/image.jpg \
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
python3 agentic_system/test_chatgarment_integration.py ...
```

## 📊 예상 결과

### 성공 시 출력

```
==================================================
ChatGarment 실제 통합 테스트
==================================================
입력 이미지: /path/to/image.jpg
출력 디렉토리: outputs/test_garment
디바이스: cuda
==================================================

📦 ChatGarment 모델 로딩 중...
==================================================
ChatGarment 모델 로딩 시작...
==================================================
✅ ChatGarment 모델 로딩 완료!

🔄 이미지 처리 시작...

==================================================
의류 생성 시작: test_001
이미지: /path/to/image.jpg
출력: outputs/test_garment/valid_garment_test_001
==================================================

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
✅ 패턴 생성 완료: outputs/.../specification.json

6️⃣ 3D 변환 시작 (GarmentCodeRC)...
✅ 3D 변환 완료!
✅ 3D 메시 생성 완료: outputs/.../mesh.obj

==================================================
테스트 결과
==================================================
✅ 성공!

생성된 파일들:
  - 출력 디렉토리: outputs/test_garment/valid_garment_test_001
  - JSON Specification: outputs/.../specification.json
  - 3D 메시 파일: outputs/.../mesh.obj

✨ 3D 의류 생성 완료!
==================================================
```

### 출력 파일 구조

```
outputs/test_garment/valid_garment_test_001/
├── gt_image.png                           # 원본 이미지
├── output.txt                             # 전체 출력 로그
├── valid_garment_test_001_specification.json  # 패턴 JSON
└── valid_garment_test_001_sim.obj         # 3D 메시 파일
```

## 🎯 성능 최적화

### GPU 메모리 최적화

- 배치 크기 조정
- Mixed precision 사용
- Gradient checkpointing

### 처리 시간 최적화

- 모델 캐싱
- 병렬 처리
- 중간 결과 저장

## 📝 로그 확인

테스트 중 상세 로그는 `outputs/test_garment/valid_garment_*/output.txt`에 저장됩니다.

## 🔄 다음 단계

테스트 성공 후:

1. API 서버 통합
2. 프론트엔드 연동
3. 배치 처리 구현
4. 성능 모니터링

