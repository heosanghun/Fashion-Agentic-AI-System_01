@echo off
echo ============================================================
echo Fashion Agentic AI System - 전체 시스템 시작
echo ============================================================
echo.

REM API 서버 시작 (백그라운드)
echo [1/2] API 서버 시작 중...
start /B cmd /c "cd agentic_system && python start_api_server.py"
timeout /t 3 /nobreak >nul

REM 프론트엔드 시작
echo [2/2] 프론트엔드 서버 시작 중...
cd agentic_system\frontend
if not exist node_modules (
    echo npm 패키지 설치 중...
    call npm install
)
echo.
echo ============================================================
echo 서버 시작 완료!
echo API 서버: http://localhost:8000
echo 프론트엔드: http://localhost:3000
echo ============================================================
echo.
echo 프론트엔드 개발 서버를 시작합니다...
call npm run dev

