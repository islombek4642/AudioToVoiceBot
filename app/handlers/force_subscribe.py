from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from app.core.logging import get_logger
from app.services.force_subscribe import force_subscribe_service

logger = get_logger(__name__)


async def check_subscription_callback(callback: CallbackQuery):
    """Obuna tekshirish callback handler'i"""
    try:
        # Middleware allaqachon ishlov bergan
        # Bu yerda qo'shimcha logika qo'shish mumkin
        pass
        
    except Exception as e:
        logger.error(f"Subscription callback'da xato: {e}")
        await callback.answer("❌ Xato yuz berdi.", show_alert=True)


def register_force_subscribe_handlers(dp: Dispatcher):
    """Force subscribe handler'larini ro'yxatdan o'tkazish"""
    dp.callback_query.register(
        check_subscription_callback,
        lambda c: c.data == "check_subscription"
    )
