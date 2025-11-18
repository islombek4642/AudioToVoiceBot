@echo off
chcp 65001 >nul
echo 🚀 Audio To Voice Bot - Avtomatik Setup
echo ==========================================

REM Python mavjudligini tekshirish
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python o'rnatilmagan! Python 3.8+ kerak.
    echo 💡 Python.org dan yuklab oling: https://python.org
    pause
    exit /b 1
)

REM Virtual environment yaratish
if not exist "venv" (
    echo 📦 Virtual environment yaratilmoqda...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Virtual environment yaratib bo'lmadi
        pause
        exit /b 1
    )
    echo ✅ Virtual environment yaratildi
) else (
    echo ✅ Virtual environment allaqachon mavjud
)

REM Virtual environment faollashtirish
echo 🔄 Virtual environment faollashtirilmoqda...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Virtual environment faollashtirib bo'lmadi
    pause
    exit /b 1
)

REM Requirements va FFmpeg o'rnatish
echo.
echo 📋 Python paketlar va FFmpeg o'rnatilmoqda...
echo ⏳ Bu biroz vaqt olishi mumkin...
echo.
python install_requirements.py

if errorlevel 1 (
    echo.
    echo ❌ Setup muvaffaqiyatsiz bo'ldi
    echo 💡 Qo'lda o'rnatish uchun README.md ni ko'ring
    pause
    exit /b 1
)

REM .env fayl tekshiruvi
echo.
if not exist ".env" (
    if exist ".env.example" (
        echo 📝 .env fayl yaratilmoqda...
        copy .env.example .env >nul
        echo ⚠️  MUHIM: .env faylini tahrirlang va bot tokenini kiriting!
        echo 📖 Qo'llanma: README.md da "Bot Token Olish" bo'limini ko'ring
    ) else (
        echo ⚠️  .env.example fayl topilmadi
    )
) else (
    echo ✅ .env fayl mavjud
)

echo.
echo ==========================================
echo 🎉 Setup muvaffaqiyatli yakunlandi!
echo.
echo 📋 Keyingi qadamlar:
echo 1️⃣  .env faylini tahrirlang (BOT_TOKEN va ADMIN_ID)
echo 2️⃣  Botni ishga tushiring: python main.py
echo.
echo 💡 Yordam kerakmi? README.md faylini o'qing
echo ==========================================
pause
