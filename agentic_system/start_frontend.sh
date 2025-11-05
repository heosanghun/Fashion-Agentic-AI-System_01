#!/bin/bash
echo "============================================================"
echo "Fashion Agentic AI System - 프론트엔드 서버 시작"
echo "============================================================"
echo

cd "$(dirname "$0")/frontend"

if [ ! -d "node_modules" ]; then
    echo "[*] npm 패키지 설치 중..."
    npm install
    if [ $? -ne 0 ]; then
        echo "[!] npm 설치 실패"
        exit 1
    fi
    echo "[+] npm 패키지 설치 완료"
    echo
fi

echo "[*] 프론트엔드 서버 시작 중..."
echo "[*] 브라우저에서 http://localhost:5173 접속"
echo "[*] 종료하려면 Ctrl+C"
echo

npm run dev

