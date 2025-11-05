#!/bin/bash
# ChatGarment 실제 통합 검증 스크립트
# 리눅스 환경에서 실행

set -e  # 오류 시 중단

echo "=================================================="
echo "ChatGarment 실제 통합 검증 스크립트"
echo "=================================================="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 프로젝트 루트 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "프로젝트 루트: $PROJECT_ROOT"
echo ""

# 1. Python 환경 확인
echo "[1/7] Python 환경 확인..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3가 설치되어 있지 않습니다.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python 버전: $PYTHON_VERSION${NC}"
echo ""

# 2. 필수 패키지 확인
echo "[2/7] 필수 패키지 확인..."
REQUIRED_PACKAGES=("torch" "transformers" "PIL" "numpy")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✅ $package${NC}"
    else
        echo -e "${RED}❌ $package (누락)${NC}"
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  누락된 패키지: ${MISSING_PACKAGES[*]}${NC}"
    echo "설치 명령어: pip install ${MISSING_PACKAGES[*]}"
    echo ""
    read -p "지금 설치하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install "${MISSING_PACKAGES[@]}" || {
            echo -e "${RED}❌ 패키지 설치 실패${NC}"
            exit 1
        }
    else
        echo -e "${RED}필수 패키지를 설치한 후 다시 실행해주세요.${NC}"
        exit 1
    fi
fi
echo ""

# 3. CUDA 확인
echo "[3/7] CUDA 환경 확인..."
if python3 -c "import torch; print('CUDA available:', torch.cuda.is_available())" 2>/dev/null; then
    CUDA_AVAILABLE=$(python3 -c "import torch; print(torch.cuda.is_available())" 2>/dev/null)
    if [ "$CUDA_AVAILABLE" == "True" ]; then
        CUDA_VERSION=$(python3 -c "import torch; print(torch.version.cuda)" 2>/dev/null)
        GPU_COUNT=$(python3 -c "import torch; print(torch.cuda.device_count())" 2>/dev/null)
        echo -e "${GREEN}✅ CUDA 사용 가능${NC}"
        echo "  CUDA 버전: $CUDA_VERSION"
        echo "  GPU 개수: $GPU_COUNT"
        DEVICE="cuda"
    else
        echo -e "${YELLOW}⚠️  CUDA를 사용할 수 없습니다. CPU 모드로 실행됩니다.${NC}"
        DEVICE="cpu"
    fi
else
    echo -e "${YELLOW}⚠️  PyTorch가 설치되어 있지 않거나 CUDA를 확인할 수 없습니다.${NC}"
    DEVICE="cpu"
fi
echo ""

# 4. ChatGarment 디렉토리 확인
echo "[4/7] ChatGarment 디렉토리 확인..."
if [ ! -d "ChatGarment" ]; then
    echo -e "${RED}❌ ChatGarment 디렉토리를 찾을 수 없습니다.${NC}"
    exit 1
fi

if [ -d "ChatGarment/llava" ]; then
    echo -e "${GREEN}✅ ChatGarment 디렉토리 확인됨${NC}"
else
    echo -e "${RED}❌ ChatGarment/llava 디렉토리를 찾을 수 없습니다.${NC}"
    exit 1
fi
echo ""

# 5. 체크포인트 확인
echo "[5/7] 모델 체크포인트 확인..."
CHECKPOINT_PATH="checkpoints/try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final/pytorch_model.bin"
BASE_MODEL_PATH="checkpoints/llava-v1.5-7b"

if [ -f "$CHECKPOINT_PATH" ]; then
    CHECKPOINT_SIZE=$(du -h "$CHECKPOINT_PATH" | cut -f1)
    echo -e "${GREEN}✅ ChatGarment 체크포인트 발견: $CHECKPOINT_PATH ($CHECKPOINT_SIZE)${NC}"
else
    echo -e "${YELLOW}⚠️  ChatGarment 체크포인트를 찾을 수 없습니다: $CHECKPOINT_PATH${NC}"
    echo "   모델 로딩이 실패할 수 있습니다."
fi

if [ -d "$BASE_MODEL_PATH" ]; then
    echo -e "${GREEN}✅ 기본 모델 디렉토리 발견: $BASE_MODEL_PATH${NC}"
else
    echo -e "${YELLOW}⚠️  기본 모델 디렉토리를 찾을 수 없습니다: $BASE_MODEL_PATH${NC}"
    echo "   모델 경로를 수정해야 할 수 있습니다."
fi
echo ""

# 6. GarmentCodeRC 확인
echo "[6/7] GarmentCodeRC 확인..."
if [ -d "GarmentCodeRC" ]; then
    echo -e "${GREEN}✅ GarmentCodeRC 디렉토리 발견${NC}"
    if [ -f "GarmentCodeRC/assets/Sim_props/default_sim_props.yaml" ]; then
        echo -e "${GREEN}✅ 시뮬레이션 설정 파일 발견${NC}"
    else
        echo -e "${YELLOW}⚠️  시뮬레이션 설정 파일을 찾을 수 없습니다.${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  GarmentCodeRC 디렉토리를 찾을 수 없습니다.${NC}"
    echo "   3D 변환 단계가 실패할 수 있습니다."
fi
echo ""

# 7. 테스트 이미지 찾기
echo "[7/7] 테스트 이미지 찾기..."
TEST_IMAGES=()

# 가능한 이미지 경로들
POSSIBLE_PATHS=(
    "ChatGarment/data/eval_images"
    "ChatGarment/example_data/example_imgs"
    "ChatGarment/data/images"
    "example_data"
)

for path in "${POSSIBLE_PATHS[@]}"; do
    if [ -d "$path" ]; then
        # 첫 번째 이미지 파일 찾기
        FIRST_IMAGE=$(find "$path" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | head -1)
        if [ -n "$FIRST_IMAGE" ]; then
            TEST_IMAGES+=("$FIRST_IMAGE")
            echo -e "${GREEN}✅ 테스트 이미지 발견: $FIRST_IMAGE${NC}"
        fi
    fi
done

if [ ${#TEST_IMAGES[@]} -eq 0 ]; then
    echo -e "${YELLOW}⚠️  테스트 이미지를 찾을 수 없습니다.${NC}"
    echo "   이미지 경로를 직접 제공해야 합니다."
else
    SELECTED_IMAGE="${TEST_IMAGES[0]}"
    echo ""
    echo -e "${GREEN}사용할 테스트 이미지: $SELECTED_IMAGE${NC}"
fi
echo ""

# 검증 완료
echo "=================================================="
echo "검증 완료!"
echo "=================================================="
echo ""
echo "테스트를 실행하시겠습니까?"
echo ""
echo "명령어:"
if [ ${#TEST_IMAGES[@]} -gt 0 ]; then
    echo "  cd agentic_system"
    echo "  python3 test_chatgarment_integration.py \\"
    echo "      --image \"$SELECTED_IMAGE\" \\"
    echo "      --output outputs/test_garment \\"
    echo "      --device $DEVICE"
else
    echo "  cd agentic_system"
    echo "  python3 test_chatgarment_integration.py \\"
    echo "      --image <이미지_경로> \\"
    echo "      --output outputs/test_garment \\"
    echo "      --device $DEVICE"
fi
echo ""

read -p "지금 테스트를 실행하시겠습니까? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd agentic_system
    if [ ${#TEST_IMAGES[@]} -gt 0 ]; then
        python3 test_chatgarment_integration.py \
            --image "$SELECTED_IMAGE" \
            --output outputs/test_garment \
            --device "$DEVICE"
    else
        echo -e "${RED}테스트 이미지 경로를 직접 제공해야 합니다.${NC}"
        echo "사용법: python3 test_chatgarment_integration.py --image <경로> --output outputs/test --device $DEVICE"
    fi
fi

