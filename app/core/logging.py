import sys
import os
from loguru import logger
from app.core.config import config


def setup_logging():
    """Logging tizimini sozlash"""
    # Standart logging'ni o'chirish
    logger.remove()
    
    # Console logging
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    logger.add(
        sys.stdout,
        format=log_format,
        level=config.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # Fayl logging
    if config.LOG_FILE_PATH:
        os.makedirs(os.path.dirname(config.LOG_FILE_PATH), exist_ok=True)
        
        logger.add(
            config.LOG_FILE_PATH,
            format=log_format,
            level=config.LOG_LEVEL,
            rotation=config.LOG_MAX_SIZE,
            retention=config.LOG_BACKUP_COUNT,
            compression="zip",
            backtrace=True,
            diagnose=True
        )
    
    # Debug rejimida qo'shimcha ma'lumot
    if config.DEBUG_MODE:
        logger.add(
            "logs/debug.log",
            format=log_format,
            level="DEBUG",
            rotation="1 day",
            retention="7 days",
            compression="zip"
        )
    
    logger.info("Logging tizimi sozlandi")


def get_logger(name: str = None):
    """Logger ni olish"""
    if name:
        return logger.bind(name=name)
    return logger
