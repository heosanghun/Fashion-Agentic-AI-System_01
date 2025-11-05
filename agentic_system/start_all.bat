@echo off
chcp 65001 >nul
echo ============================================================
echo Fashion Agentic AI System - 전체 시스템 시작
echo ============================================================
echo.
echo [주의] 두 개의 창이 열립니다:
echo   1. API 서버 (포트 8000)
echo   2. 프론트엔드 서버 (포트 5173)
echo.
echo 각 창에서 Ctrl+C로 종료할 수 있습니다.
echo.

start "API Server" cmd /k "cd /d %~dp0 && python start_api_server.py"
timeout /t 3 /nobreak >nul

start "Frontend Server" cmd /k "cd /d %~dp0 && call start_frontend.bat"

echo.
echo [+] 두 서버가 시작되었습니다!
echo.
echo [*] API 서버: http://localhost:8000
echo [*] 프론트엔드: http://localhost:5173
echo.
echo 브라우저에서 http://localhost:5173 접속하여 테스트하세요.
echo.

pause

