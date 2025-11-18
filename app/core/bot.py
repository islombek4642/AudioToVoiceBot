from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.core.config import config
from app.core.logging import get_logger

logger = get_logger(__name__)


def create_bot() -> Bot:
    """Bot instansini yaratish"""
    if not config.BOT_TOKEN:
        raise ValueError("BOT_TOKEN konfiguratsiyada topilmadi")
    
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True,
            protect_content=False
        )
    )
    
    logger.info("Bot yaratildi")
    return bot


def create_dispatcher() -> Dispatcher:
    """Dispatcher yaratish"""
    dp = Dispatcher()
    logger.info("Dispatcher yaratildi")
    return dp


async def setup_bot_commands(bot: Bot):
    """Bot buyruqlarini sozlash"""
    from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
    
    # Oddiy foydalanuvchilar uchun buyruqlar
    default_commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam"),
        BotCommand(command="about", description="Bot haqida"),
        BotCommand(command="settings", description="Sozlamalar"),
    ]
    
    # Admin uchun buyruqlar
    admin_commands = default_commands + [
        BotCommand(command="admin", description="Admin panel"),
        BotCommand(command="stats", description="Statistika"),
        BotCommand(command="channels", description="Kanallar boshqaruvi"),
        BotCommand(command="users", description="Foydalanuvchilar"),
        BotCommand(command="broadcast", description="Xabar yuborish"),
        BotCommand(command="backup", description="Ma'lumotlar zaxirasi"),
    ]
    
    try:
        # Barcha foydalanuvchilar uchun
        await bot.set_my_commands(default_commands, BotCommandScopeDefault())
        
        # Admin uchun
        if config.ADMIN_ID:
            await bot.set_my_commands(
                admin_commands, 
                BotCommandScopeChat(chat_id=config.ADMIN_ID)
            )
        
        logger.info("Bot buyruqlari sozlandi")
        
    except Exception as e:
        logger.error(f"Bot buyruqlarini sozlashda xato: {e}")


async def setup_webhook(bot: Bot):
    """Webhook sozlash (agar kerak bo'lsa)"""
    if not config.WEBHOOK_ENABLED or not config.WEBHOOK_URL:
        await bot.delete_webhook()
        logger.info("Polling rejimi - webhook o'chirildi")
        return
    
    try:
        webhook_url = f"{config.WEBHOOK_URL}{config.WEBHOOK_PATH}"
        await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True
        )
        logger.info(f"Webhook o'rnatildi: {webhook_url}")
        
    except Exception as e:
        logger.error(f"Webhook o'rnatishda xato: {e}")
        raise


async def close_bot_resources(bot: Bot, dp: Dispatcher):
    """Bot resurslarini yopish"""
    try:
        await dp.storage.close()
        await bot.session.close()
        logger.info("Bot resurslari yopildi")
    except Exception as e:
        logger.error(f"Bot resurslarini yopishda xato: {e}")
