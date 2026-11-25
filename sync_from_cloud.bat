@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ====================================================
echo   เสถียรการแว่น - ซิงค์ข้อมูลล่าสุดจาก Cloud ลง Drive D
echo ====================================================
python sync_from_cloud.py
echo.
pause
