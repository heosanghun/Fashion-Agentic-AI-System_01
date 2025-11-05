@echo off
echo ===========================================================
echo ChatGarment 서비스 시작
echo ===========================================================
echo.

cd /d "%~dp0chatgarment_service"

echo [*] 서비스 디렉토리: %CD%
echo [*] 서비스 URL: http://localhost:9000
echo [*] 종료하려면 Ctrl+C
echo.

python main.py

pause

