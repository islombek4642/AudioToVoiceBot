import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Bot konfiguratsiyasi
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "")
    
    # Admin ma'lumotlari
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "")
    
    # Ma'lumotlar bazasi
    DATABASE_URL: str = os.getenv("DATABASE_URL", "data/bot.db")
    DATABASE_BACKUP_INTERVAL: int = int(os.getenv("DATABASE_BACKUP_INTERVAL", "3600"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "logs/bot.log")
    LOG_MAX_SIZE: int = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # Audio processing
    MAX_AUDIO_SIZE: int = int(os.getenv("MAX_AUDIO_SIZE", "52428800"))  # 50MB
    SUPPORTED_AUDIO_FORMATS: List[str] = os.getenv("SUPPORTED_AUDIO_FORMATS", "mp3,wav,ogg,m4a,flac,aac").split(",")
    TEMP_AUDIO_DIR: str = os.getenv("TEMP_AUDIO_DIR", "data/temp")
    
    # Rate limiting
    RATE_LIMIT_MESSAGES: int = int(os.getenv("RATE_LIMIT_MESSAGES", "10"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # Majburiy obuna
    FORCE_SUB_ENABLED: bool = os.getenv("FORCE_SUB_ENABLED", "true").lower() == "true"
    MIN_ADMIN_APPROVE_TIME: int = int(os.getenv("MIN_ADMIN_APPROVE_TIME", "300"))  # 5 daqiqa
    
    # Webhook (ixtiyoriy)
    WEBHOOK_ENABLED: bool = os.getenv("WEBHOOK_ENABLED", "false").lower() == "true"
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_PATH: str = os.getenv("WEBHOOK_PATH", "/webhook")
    WEBAPP_HOST: str = os.getenv("WEBAPP_HOST", "localhost")
    WEBAPP_PORT: int = int(os.getenv("WEBAPP_PORT", "8080"))
    
    # Debug
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    PYTEST_MODE: bool = os.getenv("PYTEST_MODE", "false").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Konfiguratsiya to'g'riligini tekshirish"""
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN kiritilmagan")
            
        if cls.ADMIN_ID == 0:
            errors.append("ADMIN_ID kiritilmagan")
            
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL kiritilmagan")
            
        if errors:
            print("Konfiguratsiya xatolari:")
            for error in errors:
                print(f"  - {error}")
            return False
            
        return True

    @classmethod
    def create_directories(cls):
        """Kerakli kataloglarni yaratish"""
        directories = [
            os.path.dirname(cls.DATABASE_URL),
            os.path.dirname(cls.LOG_FILE_PATH),
            cls.TEMP_AUDIO_DIR,
            "data/backups"
        ]
        
        for directory in directories:
            if directory:
                os.makedirs(directory, exist_ok=True)


# Global config instance
config = Config()
