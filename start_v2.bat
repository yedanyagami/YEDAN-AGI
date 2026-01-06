@echo off
title YEDAN V2.0 - FAILOVER SYSTEM
color 0A

:LOOP
cls
echo ===================================================
echo [!] YEDAN V2.0 FAILOVER SYSTEM ACTIVE
echo.
echo     Mode: ULTRA (Maintenance / Disaster Recovery)
echo     Time: %date% %time%
echo ===================================================
echo.
echo [1/3] Checking Connectivity...
ping 1.1.1.1 -n 1 >nul
if errorlevel 1 (
    color 0C
    echo [!] NETWORK ERROR. Retrying in 30s...
    timeout /t 30 >nul
    goto LOOP
)

echo [2/3] Running V2 Engine (Disaster Recovery Mode)...
python run_roi_loop.py

echo.
echo [!] Cycle Complete. 
echo [!] Watching for next scheduled slot (15m)...
echo.
timeout /t 900

goto LOOP
