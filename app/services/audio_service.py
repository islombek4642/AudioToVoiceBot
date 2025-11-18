import os
import time
import asyncio
import subprocess
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
import aiofiles
from aiogram.types import File as TelegramFile, InputFile
from aiogram import Bot

from app.core.config import config
from app.core.logging import get_logger
from app.database.database import get_database

logger = get_logger(__name__)


class AudioProcessor:
    """Audio fayllarni qayta ishlash uchun sinf"""
    
    def __init__(self):
        self.temp_dir = Path(config.TEMP_AUDIO_DIR)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.supported_formats = [fmt.lower().strip() for fmt in config.SUPPORTED_AUDIO_FORMATS]
        self.max_size = config.MAX_AUDIO_SIZE
    
    async def process_audio_file(
        self, 
        bot: Bot, 
        telegram_file: TelegramFile, 
        user_id: int,
        original_filename: str = None
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Audio faylni qayta ishlash
        
        Returns:
            Tuple[success, file_path_or_error, metadata]
        """
        start_time = time.time()
        temp_input_path = None
        temp_output_path = None
        
        try:
            # Fayl o'lchamini tekshirish
            if telegram_file.file_size > self.max_size:
                return False, f"Fayl hajmi juda katta. Maksimal: {self.max_size // (1024*1024)}MB", None
            
            # Fayl formatini tekshirish
            file_extension = self._get_file_extension(telegram_file.file_path or original_filename)
            if not self._is_supported_format(file_extension):
                return False, f"Qo'llab-quvvatlanmaydigan format. Qo'llab-quvvatlanadigan: {', '.join(self.supported_formats)}", None
            
            # Faylni yuklab olish
            temp_input_path = self.temp_dir / f"input_{user_id}_{int(time.time())}.{file_extension}"
            await bot.download_file(telegram_file.file_path, temp_input_path)
            
            logger.info(f"Fayl yuklandi: {temp_input_path}")
            
            # Audio faylni OGG formatiga o'tkazish (Telegram voice uchun)
            temp_output_path = self.temp_dir / f"output_{user_id}_{int(time.time())}.ogg"
            
            success, error_msg = await self._convert_to_voice(
                str(temp_input_path), 
                str(temp_output_path)
            )
            
            if not success:
                return False, error_msg, None
            
            # Metadata yaratish
            processing_time = time.time() - start_time
            metadata = {
                'user_id': user_id,
                'original_filename': original_filename,
                'file_size': telegram_file.file_size,
                'audio_format': file_extension,
                'processing_time': processing_time,
                'success': True
            }
            
            # Ma'lumotlar bazasiga yozish
            db = get_database()
            await db.conversions.log_conversion(metadata)
            await db.users.increment_conversions(user_id)
            
            logger.info(f"Audio muvaffaqiyatli qayta ishlandi. Vaqt: {processing_time:.2f}s")
            
            return True, str(temp_output_path), metadata
            
        except Exception as e:
            error_msg = f"Audio qayta ishlashda xato: {str(e)}"
            logger.error(error_msg)
            
            # Xatolikni ma'lumotlar bazasiga yozish
            try:
                db = get_database()
                await db.conversions.log_conversion({
                    'user_id': user_id,
                    'original_filename': original_filename,
                    'file_size': telegram_file.file_size if telegram_file else 0,
                    'audio_format': file_extension if 'file_extension' in locals() else 'unknown',
                    'processing_time': time.time() - start_time,
                    'success': False,
                    'error_message': str(e)
                })
            except Exception as db_error:
                logger.error(f"Ma'lumotlar bazasiga xato yozishda muammo: {db_error}")
            
            return False, error_msg, None
            
        finally:
            # Vaqtinchalik fayllarni tozalash
            await self._cleanup_temp_files([temp_input_path, temp_output_path])
    
    async def _convert_to_voice(self, input_path: str, output_path: str) -> Tuple[bool, Optional[str]]:
        """Audio faylni voice formatiga o'tkazish FFmpeg orqali"""
        try:
            # FFmpeg buyrug'i
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-ac', '1',  # Mono
                '-ar', '48000',  # 48kHz sample rate
                '-c:a', 'libopus',  # Opus codec
                '-b:a', '64k',  # 64kbps bitrate
                '-vbr', 'on',  # Variable bitrate
                '-y',  # Overwrite output file
                output_path
            ]
            
            # FFmpeg'ni async ravishda ishga tushirish
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.debug(f"Audio muvaffaqiyatli konvert qilindi: {output_path}")
                return True, None
            else:
                error_msg = f"FFmpeg xatosi: {stderr.decode('utf-8', errors='ignore')}"
                logger.error(error_msg)
                return False, error_msg
            
        except FileNotFoundError:
            error_msg = "FFmpeg o'rnatilmagan yoki PATH'da yo'q"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Audio konversiyasida xato: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _get_file_extension(self, filename: str) -> str:
        """Fayl kengaytmasini olish"""
        if not filename:
            return ""
        return Path(filename).suffix[1:].lower()  # Nuqtani olib tashlash
    
    def _is_supported_format(self, extension: str) -> bool:
        """Format qo'llab-quvvatlanishini tekshirish"""
        return extension.lower() in self.supported_formats
    
    async def _cleanup_temp_files(self, file_paths: list):
        """Vaqtinchalik fayllarni tozalash"""
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.debug(f"Vaqtinchalik fayl o'chirildi: {file_path}")
                except Exception as e:
                    logger.warning(f"Vaqtinchalik faylni o'chirishda xato: {e}")
    
    async def cleanup_old_temp_files(self, max_age_hours: int = 1):
        """Eski vaqtinchalik fayllarni tozalash"""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        logger.debug(f"Eski vaqtinchalik fayl o'chirildi: {file_path}")
            
        except Exception as e:
            logger.error(f"Eski fayllarni tozalashda xato: {e}")


class AudioService:
    """Audio xizmat sinfi"""
    
    def __init__(self):
        self.processor = AudioProcessor()
    
    async def convert_audio_to_voice(
        self, 
        bot: Bot, 
        telegram_file: TelegramFile, 
        user_id: int,
        original_filename: str = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Audio faylni voice message'ga o'tkazish
        
        Returns:
            Tuple[success, message, voice_file_path]
        """
        try:
            success, result, metadata = await self.processor.process_audio_file(
                bot, telegram_file, user_id, original_filename
            )
            
            if success:
                return True, "✅ Audio muvaffaqiyatli voice message'ga aylantirildi!", result
            else:
                return False, f"❌ Xato: {result}", None
                
        except Exception as e:
            error_msg = f"Xizmatda xato: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    async def get_audio_info(self, file_path: str) -> Dict[str, Any]:
        """Audio fayl haqida ma'lumot olish FFprobe orqali"""
        try:
            # FFprobe buyrug'i
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                import json
                probe_data = json.loads(stdout.decode('utf-8'))
                
                # Audio stream ma'lumotlarini olish
                audio_stream = next(
                    (stream for stream in probe_data.get('streams', []) 
                     if stream.get('codec_type') == 'audio'), 
                    {}
                )
                
                info = {
                    'duration': float(probe_data.get('format', {}).get('duration', 0)),
                    'channels': int(audio_stream.get('channels', 0)),
                    'sample_rate': int(audio_stream.get('sample_rate', 0)),
                    'bit_rate': int(audio_stream.get('bit_rate', 0)),
                    'file_size': os.path.getsize(file_path),
                    'format': Path(file_path).suffix[1:].lower(),
                    'codec': audio_stream.get('codec_name', 'unknown')
                }
                
                return info
            else:
                # FFprobe ishlamasa, basic ma'lumotlar
                return {
                    'duration': 0,
                    'channels': 0,
                    'sample_rate': 0,
                    'bit_rate': 0,
                    'file_size': os.path.getsize(file_path),
                    'format': Path(file_path).suffix[1:].lower(),
                    'codec': 'unknown'
                }
            
        except Exception as e:
            logger.error(f"Audio ma'lumotini olishda xato: {e}")
            return {}
    
    async def validate_audio_file(self, telegram_file: TelegramFile, filename: str = None) -> Tuple[bool, str]:
        """Audio faylni tekshirish"""
        try:
            # Hajmni tekshirish
            if telegram_file.file_size > config.MAX_AUDIO_SIZE:
                max_mb = config.MAX_AUDIO_SIZE // (1024 * 1024)
                return False, f"❌ Fayl juda katta! Maksimal hajm: {max_mb}MB"
            
            # Formatni tekshirish
            extension = self.processor._get_file_extension(telegram_file.file_path or filename)
            if not self.processor._is_supported_format(extension):
                formats = ", ".join(config.SUPPORTED_AUDIO_FORMATS)
                return False, f"❌ Format qo'llab-quvvatlanmaydi! Qo'llab-quvvatlanadigan formatlar: {formats}"
            
            return True, "✅ Fayl to'g'ri"
            
        except Exception as e:
            logger.error(f"Fayl tekshirishda xato: {e}")
            return False, f"❌ Fayl tekshirishda xato: {str(e)}"


# Global service instance
audio_service = AudioService()
