#!/bin/bash
# 리눅스 서버에서 실행할 간단한 설정 스크립트

echo "==========================================================="
echo "ChatGarment 마이크로서비스 자동 설정"
echo "==========================================================="
echo ""

# 현재 IP 확인
CURRENT_IP=$(hostname -I | awk '{print $1}')
echo "[*] 현재 서버 IP: $CURRENT_IP"
echo ""

# ChatGarment 디렉토리 확인
CHATGARMENT_DIR="/home/ims/ChatGarment"
if [ ! -d "$CHATGARMENT_DIR" ]; then
    echo "[!] ChatGarment 디렉토리를 찾을 수 없습니다: $CHATGARMENT_DIR"
    echo "[*] 실제 경로를 확인하고 스크립트를 수정하세요."
    exit 1
fi

echo "[+] ChatGarment 디렉토리 확인: $CHATGARMENT_DIR"

# 서비스 디렉토리 생성
SERVICE_DIR="$CHATGARMENT_DIR/chatgarment_service"
mkdir -p "$SERVICE_DIR"
cd "$SERVICE_DIR"

echo "[*] 서비스 디렉토리: $SERVICE_DIR"
echo ""

# main.py 파일이 없는 경우 생성
if [ ! -f "main.py" ]; then
    echo "[*] main.py 파일 생성 중..."
    # Windows에서 생성한 main.py 내용을 여기에 복사해야 함
    # 또는 직접 생성
    echo "[!] main.py 파일을 수동으로 생성해야 합니다."
    echo "[*] Windows의 chatgarment_service/main.py를 이 위치로 복사하세요."
fi

# 의존성 확인 및 설치
echo "[*] 의존성 확인 중..."
python3 -m pip install --user fastapi uvicorn python-multipart 2>/dev/null || pip install fastapi uvicorn python-multipart

echo ""
echo "[+] 설정 완료!"
echo ""
echo "서비스 시작 명령어:"
echo "  cd $SERVICE_DIR"
echo "  python3 main.py"
echo ""
echo "또는 백그라운드 실행:"
echo "  nohup python3 main.py > service.log 2>&1 &"
echo ""
echo "서비스 URL: http://$CURRENT_IP:9000"

