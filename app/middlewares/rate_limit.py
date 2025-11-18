from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

from app.core.config import config
from app.core.logging import get_logger
from app.database.database import get_database

logger = get_logger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """Rate limiting middleware'i"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        try:
            user = event.from_user
            if not user:
                return await handler(event, data)
            
            # Admin uchun rate limit yo'q
            if user.id == config.ADMIN_ID:
                return await handler(event, data)
            
            db = get_database()
            
            # Rate limit tekshirish
            is_allowed = await db.rate_limits.check_rate_limit(
                user.id,
                config.RATE_LIMIT_MESSAGES,
                config.RATE_LIMIT_WINDOW
            )
            
            if not is_allowed:
                await event.answer(
                    f"⏱ Juda tez xabar yuboryapsiz! "
                    f"{config.RATE_LIMIT_WINDOW} soniya kuting."
                )
                return
            
            return await handler(event, data)
            
        except Exception as e:
            logger.error(f"Rate limit middleware'da xato: {e}")
            return await handler(event, data)
