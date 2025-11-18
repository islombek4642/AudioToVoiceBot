from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, CallbackQuery

from app.core.config import config
from app.core.logging import get_logger
from app.services.force_subscribe import force_subscribe_service

logger = get_logger(__name__)


class ForceSubscribeMiddleware(BaseMiddleware):
    """Majburiy obuna middleware'i"""
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        try:
            user = event.from_user
            bot: Bot = data.get('bot')
            
            if not user or not bot:
                return await handler(event, data)
            
            # Admin uchun majburiy obuna yo'q
            if user.id == config.ADMIN_ID:
                return await handler(event, data)
            
            # Majburiy obuna o'chirilgan bo'lsa
            if not config.FORCE_SUB_ENABLED:
                return await handler(event, data)
            
            # Start va help buyruqlarini har doim ruxsat berish
            if isinstance(event, Message):
                if event.text and event.text.startswith(('/start', '/help', '/about')):
                    return await handler(event, data)
            
            # Callback query: obuna tekshirish
            if isinstance(event, CallbackQuery):
                if event.data == 'check_subscription':
                    is_subscribed, unsubscribed_channels = await force_subscribe_service.check_user_subscriptions(
                        bot, user.id
                    )
                    
                    if is_subscribed:
                        await event.answer("✅ Barcha kanallarga obuna bo'lgansiz!", show_alert=True)
                        await event.message.delete()
                        return await handler(event, data)
                    else:
                        await event.answer("❌ Hali obuna bo'lmagan kanallar bor!", show_alert=True)
                        return
            
            # Obuna holatini tekshirish
            is_subscribed, unsubscribed_channels = await force_subscribe_service.check_user_subscriptions(
                bot, user.id
            )
            
            if not is_subscribed:
                # Obuna xabarini yuborish
                message_text = await force_subscribe_service.get_subscription_message(unsubscribed_channels)
                keyboard = await force_subscribe_service.create_subscription_keyboard(unsubscribed_channels)
                
                if isinstance(event, Message):
                    await event.answer(message_text, reply_markup=keyboard)
                elif isinstance(event, CallbackQuery):
                    await event.message.edit_text(message_text, reply_markup=keyboard)
                
                return
            
            return await handler(event, data)
            
        except Exception as e:
            logger.error(f"Force subscribe middleware'da xato: {e}")
            return await handler(event, data)
