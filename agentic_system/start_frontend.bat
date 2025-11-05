@echo off
chcp 65001 >nul
echo ============================================================
echo Fashion Agentic AI System - 프론트엔드 서버 시작
echo ============================================================
echo.

cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo [*] npm 패키지 설치 중...
    call npm install
    if errorlevel 1 (
        echo [!] npm 설치 실패
        pause
        exit /b 1
    )
    echo [+] npm 패키지 설치 완료
    echo.
)

echo [*] 프론트엔드 서버 시작 중...
echo [*] 브라우저에서 http://localhost:5173 접속
echo [*] 종료하려면 Ctrl+C
echo.

call npm run dev

pause

