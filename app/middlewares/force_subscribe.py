from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, CallbackQuery

from app.core.config import config
from app.core.logging import get_logger
from app.services.force_subscribe import force_subscribe_service

logger = get_logger(__name__)


def _is_admin_user(user) -> bool:
    return user.id == config.ADMIN_ID


def _is_force_subscribe_disabled() -> bool:
    return not config.FORCE_SUB_ENABLED


def _is_unrestricted_command(event: Message) -> bool:
    return bool(event.text and event.text.startswith(('/start', '/help', '/about')))


async def _handle_check_subscription_callback(
    event: CallbackQuery,
    bot: Bot,
    user_id: int,
    handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
    data: Dict[str, Any],
) -> bool:
    if event.data != 'check_subscription':
        return False

    is_subscribed, _ = await force_subscribe_service.check_user_subscriptions(bot, user_id)

    if is_subscribed:
        await event.answer("✅ Barcha kanallarga obuna bo'lgansiz!", show_alert=True)
        await event.message.delete()
        await handler(event, data)
    else:
        await event.answer("❌ Hali obuna bo'lmagan kanallar bor!", show_alert=True)

    return True


def _should_skip_checks(user, bot) -> bool:
    return not user or not bot or _is_admin_user(user) or _is_force_subscribe_disabled()


async def _handle_callback_query(event: CallbackQuery, bot: Bot, user_id: int, handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]], data: Dict[str, Any]) -> bool:
    return await _handle_check_subscription_callback(event, bot, user_id, handler, data)


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
            if _is_admin_user(user):
                return await handler(event, data)

            # Majburiy obuna o'chirilgan bo'lsa
            if _is_force_subscribe_disabled():
                return await handler(event, data)

            # Start va help buyruqlarini har doim ruxsat berish
            if isinstance(event, Message):
                if _is_unrestricted_command(event):
                    return await handler(event, data)

            # Callback query: obuna tekshirish
            if isinstance(event, CallbackQuery):
                handled = await _handle_check_subscription_callback(
                    event,
                    bot,
                    user.id,
                    handler,
                    data,
                )
                if handled:
                    return

            # Obuna holatini tekshirish
            is_subscribed, unsubscribed_channels = await force_subscribe_service.check_user_subscriptions(
                bot, user.id
            )
            
            if not is_subscribed:
                # Obuna xabarini yuborish
                message_text = force_subscribe_service.get_subscription_message(unsubscribed_channels)
                keyboard = force_subscribe_service.create_subscription_keyboard(unsubscribed_channels)
                
                if isinstance(event, Message):
                    await event.answer(message_text, reply_markup=keyboard)
                elif isinstance(event, CallbackQuery):
                    await event.message.edit_text(message_text, reply_markup=keyboard)
                
                return
            
            return await handler(event, data)
            
        except Exception as e:
            logger.error(f"Force subscribe middleware'da xato: {e}")
            return await handler(event, data)
