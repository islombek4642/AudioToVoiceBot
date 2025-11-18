from aiogram import Dispatcher

from .auth import AuthMiddleware  
from .rate_limit import RateLimitMiddleware
from .force_subscribe import ForceSubscribeMiddleware


def register_all_middlewares(dp: Dispatcher):
    """Barcha middleware'larni ro'yxatdan o'tkazish"""
    # Middleware'lar tartib bo'yicha qo'shiladi
    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(ForceSubscribeMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    dp.callback_query.middleware(ForceSubscribeMiddleware())