@echo off
echo 🚀 Audio To Voice Bot - Quick Setup
echo ====================================

REM Virtual environment yaratish
if not exist "venv" (
    echo 📦 Virtual environment yaratilmoqda...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Virtual environment yaratib bo'lmadi
        pause
        exit /b 1
    )
)

REM Virtual environment faollashtirish
echo 🔄 Virtual environment faollashtirilmoqda...
call venv\Scripts\activate.bat

REM Requirements va FFmpeg o'rnatish
echo 📋 Requirements va FFmpeg o'rnatilmoqda...
python install_requirements.py

if errorlevel 1 (
    echo ❌ Setup muvaffaqiyatsiz
    pause
    exit /b 1
)

echo.
echo ✅ Setup yakunlandi!
echo ℹ️  Botni ishga tushirish uchun: python main.py
echo.
pause
