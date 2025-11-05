@echo off
echo ============================================================
echo ChatGarment Service - Real Model Loading
echo ============================================================
echo.
echo [INFO] Switching to ChatGarment directory...
cd /d D:\AI\ChatGarment\ChatGarment
echo [INFO] Current directory: %CD%
echo.
echo [INFO] Checking checkpoint...
if exist "..\checkpoints\try_7b_lr1e_4_v3_garmentcontrol_4h100_v4_final\pytorch_model.bin" (
    echo [OK] Checkpoint found
) else (
    echo [FAIL] Checkpoint not found
)
echo.
echo [INFO] Starting service...
cd /d D:\AI\ChatGarment\agentic_system\chatgarment_service
python main.py
pause

