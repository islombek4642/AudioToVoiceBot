import asyncio
import sys
import os

# Path'ga app katalogini qo'shish
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import config
from app.core.logging import setup_logging, get_logger
from app.core.bot import (
    create_bot, 
    create_dispatcher, 
    setup_bot_commands, 
    setup_webhook,
    close_bot_resources
)
from app.database.database import init_database

logger = get_logger(__name__)


async def setup_application():
    """Dasturni sozlash"""
    try:
        # Konfiguratsiyani tekshirish
        if not config.validate():
            logger.error("Konfiguratsiya xatosi!")
            sys.exit(1)
        
        # Kerakli kataloglarni yaratish
        config.create_directories()
        
        # Ma'lumotlar bazasini sozlash
        await init_database(config.DATABASE_URL)
        logger.info("Ma'lumotlar bazasi sozlandi")
        
        # Bot va dispatcher yaratish
        bot = create_bot()
        dp = create_dispatcher()
        
        # Handler'larni import qilish va ro'yxatdan o'tkazish
        from app.handlers import register_all_handlers
        register_all_handlers(dp)
        
        # Middleware'larni ro'yxatdan o'tkazish
        from app.middlewares import register_all_middlewares
        register_all_middlewares(dp)
        
        # Bot buyruqlarini sozlash
        await setup_bot_commands(bot)
        
        # Webhook sozlash (agar kerak bo'lsa)
        await setup_webhook(bot)
        
        return bot, dp
        
    except Exception as e:
        logger.error(f"Dasturni sozlashda xato: {e}")
        raise


async def main():
    """Asosiy funksiya"""
    setup_logging()
    logger.info("Audio To Voice Bot ishga tushirildi")
    
    try:
        bot, dp = await setup_application()
        
        if config.WEBHOOK_ENABLED:
            # Webhook rejimi
            from aiohttp import web
            from aiohttp.web import run_app
            
            app = web.Application()
            
            # Webhook handler qo'shish
            from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application as webhook_setup
            
            webhook_handler = SimpleRequestHandler(
                dispatcher=dp,
                bot=bot,
                secret_token=None
            )
            
            webhook_handler.register(app, path=config.WEBHOOK_PATH)
            webhook_setup(app, dp, bot=bot)
            
            logger.info(f"Webhook rejimida ishga tushirildi: {config.WEBAPP_HOST}:{config.WEBAPP_PORT}")
            
            # Web server ishga tushirish
            run_app(
                app,
                host=config.WEBAPP_HOST,
                port=config.WEBAPP_PORT
            )
            
        else:
            # Polling rejimi
            logger.info("Polling rejimida ishga tushirildi")
            await dp.start_polling(
                bot,
                drop_pending_updates=True,
                allowed_updates=dp.resolve_used_update_types()
            )
            
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi (Ctrl+C)")
        
    except Exception as e:
        logger.error(f"Bot ishida xato: {e}")
        # Re-raise the exception to stop the application as expected
        raise e
        
    finally:
        if 'bot' in locals() and 'dp' in locals():
            await close_bot_resources(bot, dp)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi")
