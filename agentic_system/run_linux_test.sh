#!/bin/bash
# 리눅스 환경에서 ChatGarment 통합 테스트 실행 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=================================================="
echo "ChatGarment 실제 통합 테스트 실행"
echo "=================================================="
echo ""

# 기본 설정
DEVICE="${1:-cuda}"
TEST_IMAGE="${2:-}"
OUTPUT_DIR="${3:-outputs/test_garment}"

# Python 경로 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되어 있지 않습니다."
    exit 1
fi

# 이미지 경로 자동 탐색
if [ -z "$TEST_IMAGE" ]; then
    echo "테스트 이미지 자동 탐색 중..."
    
    POSSIBLE_PATHS=(
        "ChatGarment/data/eval_images"
        "ChatGarment/example_data/example_imgs"
        "ChatGarment/data/images"
        "example_data"
    )
    
    for path in "${POSSIBLE_PATHS[@]}"; do
        if [ -d "$path" ]; then
            IMAGE=$(find "$path" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | head -1)
            if [ -n "$IMAGE" ]; then
                TEST_IMAGE="$IMAGE"
                echo "✅ 테스트 이미지 발견: $TEST_IMAGE"
                break
            fi
        fi
    done
fi

# 이미지가 없으면 오류
if [ -z "$TEST_IMAGE" ] || [ ! -f "$TEST_IMAGE" ]; then
    echo "❌ 테스트 이미지를 찾을 수 없습니다."
    echo ""
    echo "사용법:"
    echo "  ./run_linux_test.sh [device] [image_path] [output_dir]"
    echo ""
    echo "예시:"
    echo "  ./run_linux_test.sh cuda /path/to/image.jpg outputs/test"
    exit 1
fi

# 출력 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

echo ""
echo "테스트 설정:"
echo "  이미지: $TEST_IMAGE"
echo "  출력: $OUTPUT_DIR"
echo "  디바이스: $DEVICE"
echo ""

# 테스트 실행
cd agentic_system
python3 test_chatgarment_integration.py \
    --image "$TEST_IMAGE" \
    --output "$OUTPUT_DIR" \
    --device "$DEVICE"

echo ""
echo "=================================================="
echo "테스트 완료!"
echo "=================================================="

