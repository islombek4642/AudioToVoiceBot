from aiogram import Dispatcher

from .start import register_start_handlers
from .audio import register_audio_handlers
from .admin import register_admin_handlers
from .force_subscribe import register_force_subscribe_handlers
from .channel_requests import register_channel_request_handlers


def register_all_handlers(dp: Dispatcher):
    """Barcha handler'larni ro'yxatdan o'tkazish"""
    register_start_handlers(dp)
    register_force_subscribe_handlers(dp)
    register_audio_handlers(dp)
    register_channel_request_handlers(dp)
    register_admin_handlers(dp)  # Admin handler'lar oxirida