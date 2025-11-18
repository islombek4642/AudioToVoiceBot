from aiogram import Dispatcher, F
from aiogram.types import Message, BufferedInputFile

from app.core.logging import get_logger
from app.services.audio_service import audio_service

logger = get_logger(__name__)


async def audio_document_handler(message: Message):
    """Audio document handler'i"""
    try:
        document = message.document
        
        if not document:
            return
        
        # Bot file ma'lumotlarini olish
        telegram_file = await message.bot.get_file(document.file_id)
        
        # Fayl tekshirish
        is_valid, validation_message = await audio_service.validate_audio_file(
            telegram_file, document.file_name
        )
        
        if not is_valid:
            await message.reply(validation_message)
            return
        
        # Processing xabari
        processing_msg = await message.reply("🔄 Audio fayl qayta ishlanmoqda...")
        
        try:
            # Audio faylni voice'ga aylantirish
            success, result_message, voice_file_path = await audio_service.convert_audio_to_voice(
                message.bot, telegram_file, message.from_user.id, document.file_name
            )
            
            if success and voice_file_path:
                # Voice faylni yuborish
                with open(voice_file_path, 'rb') as voice_file:
                    voice_data = voice_file.read()
                
                voice_input = BufferedInputFile(voice_data, filename="voice.ogg")
                
                await message.reply_voice(
                    voice=voice_input,
                    caption="✅ Audio muvaffaqiyatli voice message'ga aylantirildi!"
                )
                
                await processing_msg.delete()
                
            else:
                await processing_msg.edit_text(result_message)
                
        except Exception as e:
            logger.error(f"Audio konversiyada xato: {e}")
            await processing_msg.edit_text("❌ Audio faylni qayta ishlashda xato yuz berdi.")
            
    except Exception as e:
        logger.error(f"Audio handler'da xato: {e}")
        await message.reply("❌ Xato yuz berdi. Iltimos, qaytadan urinib ko'ring.")


async def audio_file_handler(message: Message):
    """Audio fayl handler'i"""
    try:
        audio = message.audio
        
        if not audio:
            return
        
        # Bot file ma'lumotlarini olish
        telegram_file = await message.bot.get_file(audio.file_id)
        
        # Fayl tekshirish
        is_valid, validation_message = await audio_service.validate_audio_file(
            telegram_file, f"{audio.performer or 'Audio'} - {audio.title or 'Unknown'}.mp3"
        )
        
        if not is_valid:
            await message.reply(validation_message)
            return
        
        # Processing xabari
        processing_msg = await message.reply("🔄 Audio fayl qayta ishlanmoqda...")
        
        try:
            # Audio faylni voice'ga aylantirish
            success, result_message, voice_file_path = await audio_service.convert_audio_to_voice(
                message.bot, telegram_file, message.from_user.id,
                f"{audio.performer or 'Audio'} - {audio.title or 'Unknown'}.mp3"
            )
            
            if success and voice_file_path:
                # Voice faylni yuborish
                with open(voice_file_path, 'rb') as voice_file:
                    voice_data = voice_file.read()
                
                voice_input = BufferedInputFile(voice_data, filename="voice.ogg")
                
                caption = "✅ Audio muvaffaqiyatli voice message'ga aylantirildi!"
                if audio.title:
                    caption += f"\n🎵 {audio.title}"
                if audio.performer:
                    caption += f"\n👤 {audio.performer}"
                
                await message.reply_voice(
                    voice=voice_input,
                    caption=caption
                )
                
                await processing_msg.delete()
                
            else:
                await processing_msg.edit_text(result_message)
                
        except Exception as e:
            logger.error(f"Audio konversiyada xato: {e}")
            await processing_msg.edit_text("❌ Audio faylni qayta ishlashda xato yuz berdi.")
            
    except Exception as e:
        logger.error(f"Audio handler'da xato: {e}")
        await message.reply("❌ Xato yuz berdi. Iltimos, qaytadan urinib ko'ring.")


async def voice_handler(message: Message):
    """Voice message handler'i"""
    await message.reply(
        "ℹ️ Bu allaqachon voice message. "
        "Agar boshqa formatga o'tkazish kerak bo'lsa, audio fayl sifatida yuboring."
    )


async def unsupported_file_handler(message: Message):
    """Qo'llab-quvvatlanmaydigan fayl handler'i"""
    help_text = """
❌ <b>Qo'llab-quvvatlanmaydigan fayl turi!</b>

<b>✅ Qo'llab-quvvatlanadigan formatlar:</b>
• MP3 (.mp3)
• WAV (.wav)
• OGG (.ogg)
• M4A (.m4a)
• FLAC (.flac)
• AAC (.aac)

<b>📏 Cheklovlar:</b>
• Maksimal hajm: 50MB
• Faylni audio sifatida yuboring

<b>💡 Maslahat:</b>
Faylni "Fayl sifatida yuborish" rejimida yuboring.
    """
    
    await message.reply(help_text)


def register_audio_handlers(dp: Dispatcher):
    """Audio handler'larini ro'yxatdan o'tkazish"""
    # Audio document handler
    dp.message.register(
        audio_document_handler,
        F.document & F.document.mime_type.startswith('audio/')
    )
    
    # Audio fayl handler
    dp.message.register(audio_file_handler, F.audio)
    
    # Voice message handler
    dp.message.register(voice_handler, F.voice)
    
    # Video note handler (doiraviy video)
    dp.message.register(
        unsupported_file_handler, 
        F.video_note
    )
