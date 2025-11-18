# 🎵 Audio To Voice Bot

Professional Telegram bot - audio fayllarni voice message formatiga o'tkazish. Zamonaviy modular arxitektura va to'liq avtomatik setup bilan.

## ✨ Xususiyatlar

- 🔄 **Audio-Voice Konvertatsiya**: MP3, WAV, OGG, M4A, FLAC, AAC → Voice Message
- 🔐 **Majburiy Obuna Tizimi**: Kanal/guruh obunalarini majburiy qilish
- 👥 **Admin Panel**: To'liq statistika va boshqaruv paneli
- 📊 **Statistika**: Foydalanuvchilar, faollik va konversiyalar hisoboti
- 🛡️ **Xavfsizlik**: Rate limiting va xavfsizlik himoyasi
- 🏗️ **Modular Arxitektura**: Oson kengaytirish va xizmat ko'rsatish
- 🌍 **User-Friendly**: O'zbek tilida tushunarli interfeys
- 📦 **Portable FFmpeg**: System o'rnatish talab qilinmaydi

## 🚀 Tezkor O'rnatish

### 1️⃣ Repository'ni klonlash
```bash
git clone https://github.com/islombek4642/AudioToVoiceBot.git
cd AudioToVoiceBot
```

### 2️⃣ Avtomatik setup (Tavsiya etiladi)

**Windows:**
```cmd
setup.bat
```

**Barcha platformalar:**
```bash
python install_requirements.py
```

Bu buyruq avtomatik ravishda:
- ✅ Virtual environment yaratadi
- ✅ Python paketlarni o'rnatadi  
- ✅ FFmpeg'ni yuklab oladi (loyiha papkasiga)
- ✅ Barcha kerakli fayllarni sozlaydi

### 3️⃣ Environment sozlash

```bash
# .env.example dan nusxa oling
cp .env.example .env

# .env faylini tahrirlang
notepad .env  # Windows
nano .env     # Linux/macOS
```

### 4️⃣ Botni ishga tushirish

```bash
# Virtual environment faollashtirish
# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

# Botni ishga tushirish
python main.py
```

## ⚙️ Konfiguratsiya

`.env` faylini to'ldiring:

```env
# Bot sozlamalari
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_ID=123456789

# Ma'lumotlar bazasi
DATABASE_URL=data/bot.db

# Audio sozlamalari  
MAX_AUDIO_SIZE=52428800  # 50MB
SUPPORTED_AUDIO_FORMATS=mp3,wav,ogg,m4a,flac,aac
TEMP_AUDIO_DIR=data/temp

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
```

### 🤖 Bot Token Olish

1. [@BotFather](https://t.me/botfather) ga yozing
2. `/newbot` buyrug'ini yuboring  
3. Bot nomini kiriting (masalan: "My Audio Bot")
4. Username kiriting (masalan: "my_audio_bot")
5. Tokenni oling va `.env` fayliga joylashtiring

### 👤 Admin ID Olish

1. [@userinfobot](https://t.me/userinfobot) ga yozing
2. `/start` tugmasini bosing
3. ID raqamingizni oling va `.env` fayliga joylashtiring

## 🏃‍♂️ Ishga Tushirish

```bash
# Virtual environment faollashtirish (agar faollashtirilmagan bo'lsa)
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Botni ishga tushirish
python main.py
```

**Muvaffaqiyatli ishga tushganda ko'rasiz:**
```
🎵 Audio To Voice Bot ishga tushirildi
📊 Ma'lumotlar bazasi sozlandi
🤖 Bot yaratildi
🔄 Polling rejimida ishga tushirildi
```

## 📁 Loyiha Strukturasi

```
AudioToVoiceBot/
├── app/                    # Asosiy dastur kodi
│   ├── core/              # Konfiguratsiya va asosiy modullar
│   ├── handlers/          # Telegram handler'lar
│   ├── middlewares/       # Middleware'lar  
│   ├── database/          # Database modellari va migratsiyalar
│   ├── services/          # Business logika (audio, broadcast, etc.)
│   └── utils/             # Yordam funksiyalari va konstantalar
├── data/                  # Ma'lumotlar bazasi va cache
├── logs/                  # Log fayllar
├── ffmpeg/                # FFmpeg binaries (avtomatik yuklanadi)
├── temp/                  # Vaqtinchalik fayllar
├── venv/                  # Virtual environment
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables namunasi
├── setup.bat             # Windows avtomatik setup
├── install_requirements.py  # Python + FFmpeg setup
├── download_ffmpeg.py    # FFmpeg yuklab olish
└── main.py              # Asosiy ishga tushirish fayli
```

## 🔧 Foydalanish

### 👤 Oddiy foydalanuvchi
1. `/start` - Botni ishga tushirish
2. Audio fayl yuboring (MP3, WAV, OGG, M4A, FLAC, AAC)
3. Voice message formatida qaytarib oling

### 👨‍💼 Admin funksiyalari
- `/admin` - Admin panel
- Statistikalar ko'rish
- Majburiy kanallar boshqaruvi  
- Foydalanuvchilar ro'yxati
- Broadcast xabarlar yuborish

## 🐛 Muammolarni Yechish

### FFmpeg muammolari
```bash
# Agar FFmpeg topilmasa, qayta yuklab oling
python download_ffmpeg.py
```

### Database muammolari
```bash
# Ma'lumotlar bazasini qayta yarating
rm data/bot.db
python main.py  # Avtomatik yaratiladi
```

### Audio konversiya muammolari
- Fayl hajmi: maksimal 50MB
- Qo'llab-quvvatlanadigan formatlar: MP3, WAV, OGG, M4A, FLAC, AAC
- FFmpeg mavjudligini tekshiring

## 🧹 Tozalash

Barcha o'rnatilgan fayllar va cache'larni tozalash uchun:

```bash
# Virtual environment o'chirish
rmdir /s venv          # Windows
rm -rf venv            # Linux/macOS

# Cache va temp fayllar
rmdir /s data          # Windows  
rm -rf data            # Linux/macOS

rmdir /s logs          # Windows
rm -rf logs            # Linux/macOS

rmdir /s temp          # Windows
rm -rf temp            # Linux/macOS

rmdir /s ffmpeg        # Windows
rm -rf ffmpeg          # Linux/macOS

# Python cache
rmdir /s __pycache__   # Windows
rm -rf __pycache__     # Linux/macOS
find . -name "*.pyc" -delete  # Linux/macOS
```

## 📝 Changelog

### v2.0.0 (2025-11-18)
- ✅ Avtomatik FFmpeg setup
- ✅ Portable FFmpeg binaries
- ✅ SonarCloud code quality fixes
- ✅ Improved error handling
- ✅ Better user experience

### v1.0.0 (2025-11-17)
- ✅ Audio-voice konversiya
- ✅ Majburiy obuna tizimi
- ✅ Admin panel
- ✅ Statistika tizimi

## 👨‍💻 Muallif

**Islombek** - [@islombek4642](https://github.com/islombek4642)

## ⭐ Qo'llab-quvvatlash

Agar loyiha foydali bo'lsa, ⭐ qo'ying!

## 📞 Bog'lanish

- GitHub: [Issues](https://github.com/islombek4642/AudioToVoiceBot/issues)
- Telegram: [@islombek4642](https://t.me/islombek4642)
