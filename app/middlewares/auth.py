from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from app.core.logging import get_logger
from app.database.database import get_database

logger = get_logger(__name__)


class AuthMiddleware(BaseMiddleware):
    """Foydalanuvchi autentifikatsiya middleware'i"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        try:
            user = event.from_user
            if not user:
                return await handler(event, data)
            
            db = get_database()
            
            # Foydalanuvchini ma'lumotlar bazasiga qo'shish/yangilash
            user_data = {
                'user_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'language_code': user.language_code
            }
            
            await db.users.create_user(user_data)
            await db.users.update_user_activity(user.id)
            
            # Ma'lumotlarni data'ga qo'shish
            data['user_data'] = await db.users.get_user(user.id)
            
            return await handler(event, data)
            
        except Exception as e:
            logger.error(f"Auth middleware'da xato: {e}")
            return await handler(event, data)
