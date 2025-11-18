# 🎵 Audio To Voice Bot

Zamonaviy modular arxitekturada yaratilgan Telegram bot. Foydalanuvchilar audio fayllarini yuklaydilar, bot ularni voice message formatiga o'tkazib qaytaradi.

## ✨ Xususiyatlar

- 🔄 **Audio-Voice Konvertatsiya**: Barcha mashhur audio formatlarni voice message'ga o'tkazish
- 🔐 **Majburiy Obuna Tizimi**: Kanal/guruh obunalarini majburiy qilish imkoniyati
- 👥 **Admin Panel**: To'liq statistika va boshqaruv paneli
- 📊 **Statistika**: Foydalanuvchilar, faollik va konversiyalar statistikasi
- 🛡️ **Xavfsizlik**: Rate limiting va xavfsizlik himoyasi
- 🏗️ **Modular Arxitektura**: Oson kengaytirish va xizmat ko'rsatish
- 🌍 **User-Friendly**: O'zbek tilida tushunarli interfeys

## 🚀 O'rnatish

### 1. Repository'ni klonlash
```bash
git clone https://github.com/yourusername/AudioToVoiceBot.git
cd AudioToVoiceBot
```

### 2. Virtual environment yaratish
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Paketlarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Environment o'rnatish
```bash
# .env.example faylini .env ga ko'chiring
cp .env.example .env

# .env faylini o'z ma'lumotlaringiz bilan to'ldiring
```

### 5. FFmpeg o'rnatish
**Windows:**
1. [FFmpeg](https://ffmpeg.org/download.html) saytidan yuklab oling
2. PATH'ga qo'shing

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

## ⚙️ Konfiguratsiya

`.env` faylini to'ldiring:

```env
# Asosiy sozlamalar
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_admin_user_id_here

# Ma'lumotlar bazasi
DATABASE_URL=data/bot.db

# Audio sozlamalari
MAX_AUDIO_SIZE=52428800  # 50MB
SUPPORTED_AUDIO_FORMATS=mp3,wav,ogg,m4a,flac,aac
```

### Bot Token Olish
1. [@BotFather](https://t.me/botfather) ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting
4. Username kiriting
5. Tokenni oling va `.env` ga joylashtiring

### Admin ID Olish
1. [@userinfobot](https://t.me/userinfobot) ga yozing
2. `/start` ni bosing
3. ID raqamingizni oling

## 🏃‍♂️ Ishga Tushirish

### Development rejimida
```bash
python main.py
```

### Production rejimida
```bash
# systemd service yarating (Linux)
sudo cp deploy/audiobot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable audiobot
sudo systemctl start audiobot
```

## 📁 Loyiha Strukturasi

```
AudioToVoiceBot/
├── app/
│   ├── core/            # Asosiy konfiguratsiya
│   ├── handlers/        # Telegram handler'lar
│   ├── middlewares/     # Middleware'lar
│   ├── database/        # Database modellari
│   ├── services/        # Business logika
│   └── utils/           # Yordam funksiyalari
├── data/                # Ma'lumotlar va cache
├── logs/                # Log fayllar
├── deploy/              # Deploy skriptlari
├── tests/               # Testlar
├── requirements.txt     # Python paketlari
├── .env.example         # Environment namunasi
└── main.py             # Asosiy fayl
```

## 🔧 Foydalanish

### Oddiy foydalanuvchi:
1. Botni ishga tushiring: `/start`
2. Audio faylni yuboring
3. Voice message formatida qaytarib oling

### Admin funksiyalari:
- `/admin` - Admin panel
- `/stats` - Statistikalar
- `/channels` - Majburiy kanallar boshqaruvi
- `/users` - Foydalanuvchilar ro'yxati

### Majburiy obuna:
1. Botni kanal/guruhga admin sifatida qo'shing
2. Admin paneldan kanalni majburiy obunaga qo'shing
3. Foydalanuvchilar obuna bo'lmagunicha botdan foydalana olmaydi

## 🧪 Testlash

```bash
# Barcha testlarni ishga tushirish
pytest

# Coverage bilan
pytest --cov=app tests/

# Ma'lum bir testni ishga tushirish
pytest tests/test_audio_service.py
```

## 📊 Statistika

Bot quyidagi statistikalarni kuzatib boradi:
- Jami foydalanuvchilar soni
- Kunlik faol foydalanuvchilar
- Audio konversiyalar soni
- Eng mashhur audio formatlar
- Majburiy obuna statistikasi

## 🛠️ Development

### Yangi modul qo'shish:
1. `app/` papkasida yangi papka yarating
2. `__init__.py` faylini qo'shing
3. `main.py` da import qiling

### Yangi handler qo'shish:
1. `app/handlers/` da yangi fayl yarating
2. Handler'ni yozing
3. `app/handlers/__init__.py` da import qiling

### Yangi service qo'shish:
1. `app/services/` da yangi fayl yarating
2. Business logikani yozing
3. Handler'larda ishlatning

## 🔒 Xavfsizlik

- Barcha foydalanuvchi kiritmalarini tekshirish
- Rate limiting yordamida spam himoyasi
- SQL injection himoyasi
- Fayl hajmi va format tekshiruvi
- Admin huquqlarini tekshirish

## 🐛 Muammolarni Yechish

### Keng uchraydigan muammolar:

**FFmpeg topilmaydi:**
```bash
# PATH ga qo'shing yoki to'liq path ko'rsating
FFMPEG_PATH=/usr/bin/ffmpeg
```

**Database xatosi:**
```bash
# Ma'lumotlar bazasini qayta yarating
rm data/bot.db
python -c "from app.database import init_db; init_db()"
```

**Audio konversiya xatosi:**
- Fayl hajmini tekshiring (50MB gacha)
- Audio format qo'llab-quvvatlanishini tekshiring
- FFmpeg o'rnatilganligini tekshiring

## 📝 Changelog

### v1.0.0 (2025-11-17)
- Asosiy audio-voice konversiya
- Majburiy obuna tizimi
- Admin panel
- Statistika tizimi
- Modular arxitektura

## 🤝 Hissa Qo'shish

1. Repository'ni fork qiling
2. Feature branch yarating: `git checkout -b new-feature`
3. O'zgarishlarni commit qiling: `git commit -am 'Add new feature'`
4. Branch'ni push qiling: `git push origin new-feature`
5. Pull Request yarating

## 📜 Litsenziya

MIT License - [LICENSE](LICENSE) faylini ko'ring.

## 👨‍💻 Muallif

**Sizning Ismingiz** - [GitHub](https://github.com/yourusername)

## ⭐ Qo'llab-quvvatlash

Agar loyiha foydali bo'lsa, ⭐ qo'ying!

## 📞 Bog'lanish

- Telegram: [@yourusername](https://t.me/yourusername)
- Email: your.email@gmail.com
- Issues: [GitHub Issues](https://github.com/yourusername/AudioToVoiceBot/issues)
