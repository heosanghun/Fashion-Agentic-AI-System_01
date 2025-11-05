#!/bin/bash
# ChatGarment 마이크로서비스 시작 스크립트

echo "============================================================"
echo "ChatGarment 마이크로서비스 시작"
echo "============================================================"

# 현재 스크립트의 디렉토리로 이동
cd "$(dirname "$0")"

# 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Python 경로 확인
python3 --version

# ChatGarment 경로 확인
CHATGARMENT_ROOT="${CHATGARMENT_ROOT:-/home/ims/ChatGarment}"
echo "ChatGarment 경로: $CHATGARMENT_ROOT"

if [ ! -d "$CHATGARMENT_ROOT" ]; then
    echo "⚠️ ChatGarment 디렉토리를 찾을 수 없습니다: $CHATGARMENT_ROOT"
    echo "환경 변수 CHATGARMENT_ROOT를 설정하거나 스크립트를 수정하세요."
    exit 1
fi

# 의존성 설치 (필요한 경우)
if [ ! -d "venv" ]; then
    echo "[*] 가상환경 생성 중..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# 서비스 시작
echo "[*] 서비스 시작 중..."
echo "[*] 포트: 9000"
echo "[*] 접속: http://localhost:9000"
echo "[*] 종료하려면 Ctrl+C"
echo ""

uvicorn main:app --host 0.0.0.0 --port 9000 --reload

