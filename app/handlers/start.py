from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from datetime import datetime

from app.core.config import config
from app.core.logging import get_logger
from app.database.database import get_database
from app.utils.messages import UNKNOWN_TEXT

logger = get_logger(__name__)


async def start_handler(message: Message):
    """Start buyrug'i handler'i"""
    try:
        db = get_database()
        
        # Foydalanuvchini ma'lumotlar bazasiga qo'shish
        user_data = {
            'user_id': message.from_user.id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
            'language_code': message.from_user.language_code
        }
        
        await db.users.create_user(user_data)
        await db.statistics.log_activity(message.from_user.id, 'start_command')
        
        welcome_text = f"""
🎵 <b>Audio To Voice Bot</b>ga xush kelibsiz!

Salom <b>{message.from_user.first_name}</b>! 👋

Bu bot audio fayllarni voice message formatiga aylantirib beradi.

<b>🔧 Qanday ishlatiladi:</b>
📁 Audio faylni yuboring (MP3, WAV, OGG, M4A, FLAC, AAC)
⚡ Bot uni voice message'ga aylantiradi
📤 Tayyor voice message'ni olasiz

<b>📏 Cheklovlar:</b>
• Maksimal fayl hajmi: 50MB
• Qo'llab-quvvatlanadigan formatlar: MP3, WAV, OGG, M4A, FLAC, AAC

<b>🚀 Boshlash uchun audio fayl yuboring!</b>

/help - Batafsil yordam
/about - Bot haqida
        """
        
        await message.answer(welcome_text.strip())
        logger.info(f"Yangi foydalanuvchi: {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Start handler'da xato: {e}")
        await message.answer("❌ Xato yuz berdi. Iltimos, qaytadan urinib ko'ring.")


async def help_handler(message: Message):
    """Help buyrug'i handler'i"""
    help_text = """
<b>🆘 Yordam</b>

<b>📋 Buyruqlar:</b>
/start - Botni ishga tushirish
/help - Bu yordam xabari
/about - Bot haqida ma'lumot
/settings - Sozlamalar

<b>🎵 Audio konversiya:</b>
1. Audio faylni yuboring
2. Bot uni voice message'ga aylantiradi
3. Tayyor voice message'ni yuklab oling

<b>📏 Texnik ma'lumotlar:</b>
• Qo'llab-quvvatlanadigan formatlar: MP3, WAV, OGG, M4A, FLAC, AAC
• Maksimal fayl hajmi: 50MB
• Natija formati: OGG (Opus codec)
• Sifat: Telegram voice message standartida

<b>❓ Savollar yoki muammolar?</b>
Admin bilan bog'laning: @xamidullayev_i
    """
    
    await message.answer(help_text.strip())


async def about_handler(message: Message):
    """About buyrug'i handler'i"""
    about_text = """
<b>🤖 Bot haqida</b>

<b>📛 Nomi:</b> Audio To Voice Bot
<b>📋 Versiya:</b> 1.0.0
<b>🔧 Vazifasi:</b> Audio fayllarni voice message'ga aylantirish

<b>🌟 Xususiyatlar:</b>
• ⚡ Tez konversiya
• 🎯 Yuqori sifat
• 🔒 Xavfsizlik
• 🌍 O'zbek tili qo'llab-quvvatlashi

<b>💻 Texnologiyalar:</b>
• Python 3.13 + Aiogram 3.22
• FFmpeg orqali audio processing
• SQLite3 ma'lumotlar bazasi
• Modular arxitektura

<b>👨‍💻 Ishlab chiqilgan:</b> 2025-yil

<b>📞 Qo'llab-quvvatlash:</b> @xamidullayev_i
    """
    
    await message.answer(about_text.strip())


async def _get_user_stats(db, user_id):
    """Foydalanuvchi statistikasini olish"""
    try:
        user = await db.users.get_user(user_id)
        if user:
            # Format dates
            reg_date = datetime.fromisoformat(user['registration_date']).strftime('%d.%m.%Y')
            if user['last_activity']:
                last_activity = datetime.fromisoformat(user['last_activity']).strftime('%d.%m.%Y %H:%M')
            else:
                last_activity = reg_date
            return reg_date, last_activity
        else:
            return "Noma'lum", "Noma'lum"
    except Exception:
        return "Noma'lum", "Noma'lum"


async def _get_user_conversions_count(db, user_id):
    """Foydalanuvchi konversiyalari sonini olish"""
    try:
        user = await db.users.get_user(user_id)
        return user.get('conversions_count', 0) if user else 0
    except Exception:
        return 0


async def settings_handler(message: Message):
    """Settings buyrug'i handler'i"""
    try:
        from app.database.database import get_database

        db = get_database()
        user_id = message.from_user.id

        # Foydalanuvchi statistikasini olish
        reg_date, last_activity = await _get_user_stats(db, user_id)

        # Konversiya statistikasi
        conversions_count = await _get_user_conversions_count(db, user_id)
        
        settings_text = f"""
⚙️ <b>Sozlamalar</b>

👤 <b>Foydalanuvchi:</b> {message.from_user.first_name or UNKNOWN_TEXT}
🆔 <b>ID:</b> <code>{user_id}</code>
🌐 <b>Til:</b> {message.from_user.language_code or 'uz'}

📊 <b>Statistika:</b>
• 📅 Ro'yxatdan o'tgan: {reg_date}
• 🕐 Oxirgi faollik: {last_activity}
• 🎵 Konversiyalar: {conversions_count} ta

🔧 <b>Bot sozlamalari:</b>
• 📏 Maksimal fayl hajmi: 50MB
• 🎼 Qo'llab-quvvatlanadigan formatlar: MP3, WAV, OGG, M4A, FLAC, AAC
• 🎯 Chiqish formati: Voice message (OGG/Opus)
• ⚡ FFmpeg orqali yuqori sifatli konversiya

💡 <b>Foydali ma'lumot:</b>
Botdan bepul foydalanishingiz mumkin. Barcha audio fayllaringiz xavfsiz qayta ishlanadi va o'chiriladi.
        """
        
        await message.answer(settings_text.strip())
        
    except Exception as e:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Settings handler'da xato: {e}")
        
        # Xato bo'lsa, oddiy variant
        settings_text = f"""
⚙️ <b>Sozlamalar</b>

👤 <b>Foydalanuvchi:</b> {message.from_user.first_name or UNKNOWN_TEXT}
🆔 <b>ID:</b> <code>{message.from_user.id}</code>
🌐 <b>Til:</b> {message.from_user.language_code or 'uz'}

🔧 <b>Bot imkoniyatlari:</b>
• Audio fayllarni voice message'ga aylantirish
• 50MB gacha fayl hajmi
• Yuqori sifatli konversiya
• Barcha mashhur formatlar qo'llab-quvvatlanadi
        """
        
        await message.answer(settings_text.strip())


def register_start_handlers(dp: Dispatcher):
    """Start handler'larini ro'yxatdan o'tkazish"""
    dp.message.register(start_handler, CommandStart())
    dp.message.register(help_handler, Command("help"))
    dp.message.register(about_handler, Command("about"))
    dp.message.register(settings_handler, Command("settings"))
