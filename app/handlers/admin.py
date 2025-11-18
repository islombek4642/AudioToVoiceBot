from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
from typing import List, Dict, Any
import math
import aiosqlite
import shutil
from pathlib import Path

from app.core.config import config
from app.core.logging import get_logger
from app.database.database import get_database
from app.services.broadcast_service import broadcast_service
from app.utils.keyboards import AdminKeyboards
from app.services.force_subscribe import force_subscribe_service
from app.utils.messages import (
    MSG_NO_ADMIN_PERMISSION,
    MSG_GENERIC_ERROR,
    MSG_GENERIC_ERROR_BANG,
    MSG_STATS_ERROR,
    MSG_USERNAME_MISSING,
)

logger = get_logger(__name__)


class AdminStates(StatesGroup):
    waiting_channel_id = State()
    waiting_broadcast_message = State()
    waiting_broadcast_target = State()
    waiting_user_search = State()
    waiting_admin_id = State()


# Admin Tekshirish Funksiyasi
def is_admin(user_id: int) -> bool:
    """Admin ekanligini tekshirish (faqat asosiy admin)"""
    return user_id == config.ADMIN_ID


async def is_admin_async(user_id: int) -> bool:
    """Admin ekanligini tekshirish (asosiy + qo'shimcha adminlar)"""
    # Asosiy adminmi
    if user_id == config.ADMIN_ID:
        return True
    
    # Ma'lumotlar bazasidan qo'shimcha adminlarni tekshirish
    try:
        db = get_database()
        user = await db.users.get_user(user_id)
        if user and user.get('is_admin', False):
            return True
    except Exception:
        pass
    
    return False


# ASOSIY ADMIN PANEL
async def admin_handler(message: Message):
    """Asosiy admin panel"""
    logger.info(f"Admin panel /admin buyrug'i ishlatildi - User: {message.from_user.id}")
    
    if not await is_admin_async(message.from_user.id):
        logger.warning(f"Admin panel'ga ruxsatsiz kirish urinishi /admin orqali: {message.from_user.id}")
        await message.reply(MSG_NO_ADMIN_PERMISSION)
        return
    
    try:
        logger.info("Admin panel yuklanyapti...")
        db = get_database()
        
        # Asosiy statistikani olish
        total_users = await db.statistics.get_user_count()
        active_today = await db.statistics.get_active_users_today()
        conversions_today = await db.statistics.get_conversions_today()
        
        logger.info(f"Admin panelga statistika yuklandi: users={total_users}, active={active_today}, conversions={conversions_today}")
        
        admin_text = f"""
🔧 <b>Admin Panel</b>

📊 <b>Tezkor statistika:</b>
👥 Jami foydalanuvchilar: <b>{total_users}</b>
✅ Bugun faollar: <b>{active_today}</b>
🎵 Bugun konversiyalar: <b>{conversions_today}</b>

⚡ Panel orqali bot to'liq boshqariladi.
        """
        
        await message.answer(
            admin_text.strip(),
            reply_markup=AdminKeyboards.main_admin_menu()
        )
        
    except Exception as e:
        logger.error(f"Admin panel'da xato: {e}")
        await message.reply("❌ Admin panel'ni yuklashda xato.")


# CALLBACK QUERY HANDLERS
async def admin_callback_handler(callback: CallbackQuery, state: FSMContext):
    """Admin callback handler"""
    if not await is_admin_async(callback.from_user.id):
        logger.warning(f"Admin panel'ga ruxsatsiz kirish urinishi: {callback.from_user.id}")
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    data = callback.data
    logger.info(f"Admin callback bosildi: '{data}' - User: {callback.from_user.id}")
    
    try:
        exact_actions = {
            "admin_back": show_admin_main_menu,
            "admin_stats": show_stats_menu,
            "admin_users": show_users_menu,
            "admin_channels": show_channels_menu,
            "admin_requests": show_requests_menu,
            "admin_broadcast": show_broadcast_menu,
            "admin_exit": None,
        }
        if data in exact_actions:
            if data == "admin_exit":
                logger.info("Admin panel chiqish tugmasi bosildi")
                await callback.message.delete()
                await callback.answer("Admin panel yopildi.")
            else:
                logger.info(f"Exact admin action: {data}")
                await exact_actions[data](callback)
            return

        # Prefix-based routing
        if data.startswith("stats_"):
            logger.info(f"Statistika bo'limi: {data}")
            await handle_stats_callbacks(callback, data)
        elif data.startswith("users_"):
            logger.info(f"Foydalanuvchilar bo'limi: {data}")
            await handle_users_callbacks(callback, data, state)
        elif data.startswith("channels_"):
            logger.info(f"Kanallar bo'limi: {data}")
            await handle_channels_callbacks(callback, data, state)
        elif data.startswith("requests_"):
            logger.info(f"So'rovlar bo'limi: {data}")
            await handle_requests_callbacks(callback, data)
        elif data.startswith("broadcast_"):
            logger.info(f"Broadcast bo'limi: {data}")
            await handle_broadcast_callbacks(callback, data, state)
        else:
            logger.warning(f"Noma'lum callback data: {data}")
            
    except Exception as e:
        logger.error(f"Admin callback'da xato: {e} - Data: {data}")
        await callback.answer(MSG_GENERIC_ERROR, show_alert=True)


# MENU FUNCTIONS
async def show_admin_main_menu(callback: CallbackQuery):
    """Asosiy admin menu"""
    logger.info("Admin asosiy menu ko'rsatildi")
    db = get_database()
    total_users = await db.statistics.get_user_count()
    active_today = await db.statistics.get_active_users_today()
    conversions_today = await db.statistics.get_conversions_today()
    
    text = f"""
🔧 <b>Admin Panel</b>

📊 <b>Tezkor statistika:</b>
👥 Jami foydalanuvchilar: <b>{total_users}</b>
✅ Bugun faollar: <b>{active_today}</b>
🎵 Bugun konversiyalar: <b>{conversions_today}</b>

⚡ Panel orqali bot to'liq boshqariladi.
    """
    
    await callback.message.edit_text(
        text.strip(),
        reply_markup=AdminKeyboards.main_admin_menu()
    )


async def show_stats_menu(callback: CallbackQuery):
    """Statistika menu"""
    logger.info("Statistika menu ko'rsatildi")
    await callback.message.edit_text(
        "📊 <b>Statistika bo'limi</b>\n\nKerakli ma'lumotni tanlang:",
        reply_markup=AdminKeyboards.stats_menu()
    )


async def show_users_menu(callback: CallbackQuery):
    """Foydalanuvchilar menu"""
    logger.info("Foydalanuvchilar menu ko'rsatildi")
    await callback.message.edit_text(
        "👥 <b>Foydalanuvchilar boshqaruvi</b>\n\nKerakli amalni tanlang:",
        reply_markup=AdminKeyboards.users_menu()
    )


async def show_channels_menu(callback: CallbackQuery):
    """Kanallar menu"""
    logger.info("Kanallar menu ko'rsatildi")
    await callback.message.edit_text(
        "📢 <b>Kanallar boshqaruvi</b>\n\nKerakli amalni tanlang:",
        reply_markup=AdminKeyboards.channels_menu()
    )


async def show_requests_menu(callback: CallbackQuery):
    """So'rovlar menu"""
    logger.info("So'rovlar menu ko'rsatildi")
    await callback.message.edit_text(
        "📝 <b>Kanal so'rovlari</b>\n\nKerakli bo'limni tanlang:",
        reply_markup=AdminKeyboards.requests_menu()
    )


async def show_broadcast_menu(callback: CallbackQuery):
    """Broadcast menu"""
    logger.info("Broadcast menu ko'rsatildi")
    await callback.message.edit_text(
        "📡 <b>Broadcast xabarlari</b>\n\nXabar turini tanlang:",
        reply_markup=AdminKeyboards.broadcast_menu()
    )


# STATISTIKA HANDLERS
async def handle_stats_callbacks(callback: CallbackQuery, data: str):
    """Statistika callback'larini boshqarish"""
    logger.info(f"Stats callback ishga tushdi: {data}")
    db = get_database()
    
    actions = {
        "stats_general": lambda: show_general_stats(callback, db),
        "stats_users": lambda: show_user_stats(callback, db),
        "stats_conversions": lambda: show_conversion_stats(callback, db),
        "stats_today": lambda: show_today_stats(callback, db),
        "stats_week": lambda: show_week_stats(callback, db),
        "stats_channels": lambda: show_channels_stats(callback),
    }
    if data == "stats_refresh":
        logger.info("Statistika yangilash chaqirildi")
        await show_stats_menu(callback)
        await callback.answer("🔄 Statistika yangilandi.")
        return
    action = actions.get(data)
    if action:
        logger.info(f"Stats action: {data}")
        await action()
    else:
        logger.warning(f"Noma'lum stats callback: {data}")


async def show_general_stats(callback: CallbackQuery, db):
    """Umumiy statistika"""
    total_users = await db.statistics.get_user_count()
    active_today = await db.statistics.get_active_users_today()
    conversions_today = await db.statistics.get_conversions_today()
    
    text = f"""
📊 <b>Umumiy statistika</b>

👥 <b>Foydalanuvchilar:</b>
• Jami: {total_users}
• Bugun faol: {active_today}

🎵 <b>Konversiyalar:</b>
• Bugun: {conversions_today}

📅 <b>Sana:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}
    """
    
    await callback.message.edit_text(
        text.strip(),
        reply_markup=AdminKeyboards.stats_menu()
    )


async def show_user_stats(callback: CallbackQuery, db):
    """Foydalanuvchilar statistikasi"""
    try:
        total_users = await db.statistics.get_user_count()
        active_users = await db.statistics.get_active_users_today()
        active_ratio = (active_users / total_users * 100) if total_users else 0

        text = (
            "👥 <b>Foydalanuvchilar statistikasi</b>\n\n"
            "📊 <b>Umumiy:</b>\n"
            f"• Jami: {total_users}\n"
            f"• Bugun faol: {active_users}\n"
            f"• Faol foiz: {active_ratio:.1f}%\n\n"
            f"📅 <b>Sana:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=AdminKeyboards.stats_menu()
        )
        
    except Exception as e:
        logger.error(f"User stats'da xato: {e}")
        await callback.answer(MSG_STATS_ERROR, show_alert=True)


async def show_conversion_stats(callback: CallbackQuery, db):
    """Konversiya statistikasi"""
    try:
        conversions_today = await db.statistics.get_conversions_today()
        
        text = f"""
🎵 <b>Konversiya statistikasi</b>

📊 <b>Bugun:</b>
• Konversiyalar: {conversions_today}
• O'rtacha: {conversions_today/24:.1f} soatiga

📅 <b>Sana:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}
        """
        
        await callback.message.edit_text(
            text.strip(),
            reply_markup=AdminKeyboards.stats_menu()
        )
        
    except Exception as e:
        logger.error(f"Conversion stats'da xato: {e}")
        await callback.answer(MSG_STATS_ERROR, show_alert=True)


async def show_today_stats(callback: CallbackQuery, db):
    """Bugungi statistika"""
    try:
        total_users = await db.statistics.get_user_count()
        active_today = await db.statistics.get_active_users_today()
        conversions_today = await db.statistics.get_conversions_today()
        
        text = f"""
📅 <b>Bugungi statistika</b>

👥 <b>Foydalanuvchilar:</b>
• Jami: {total_users}
• Bugun faol: {active_today}

🎵 <b>Konversiyalar:</b>
• Bugun: {conversions_today}

⏰ <b>Vaqt:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}
        """
        
        await callback.message.edit_text(
            text.strip(),
            reply_markup=AdminKeyboards.stats_menu()
        )
        
    except Exception as e:
        logger.error(f"Today stats'da xato: {e}")
        await callback.answer(MSG_STATS_ERROR, show_alert=True)


async def show_week_stats(callback: CallbackQuery, db):
    """Haftalik statistika"""
    try:
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        async with aiosqlite.connect(db.manager.db_path) as conn:
            cursor = await conn.execute(
                '''
                SELECT COUNT(DISTINCT user_id) FROM user_activity
                WHERE DATE(timestamp) BETWEEN ? AND ?
                ''', (str(week_ago), str(today))
            )
            active_week = (await cursor.fetchone())[0]

        total_users = await db.statistics.get_user_count()
        text = f"""
📅 <b>Haftalik statistika</b>

👥 <b>Aktiv foydalanuvchilar:</b> {active_week}
👥 <b>Jami foydalanuvchilar:</b> {total_users}
📈 <b>Faollik:</b> {(active_week/total_users*100 if total_users else 0):.1f}%

⏰ <b>Oraliq:</b> {week_ago.strftime('%d.%m.%Y')} - {today.strftime('%d.%m.%Y')}
        """

        await callback.message.edit_text(
            text.strip(),
            reply_markup=AdminKeyboards.stats_menu()
        )

    except Exception as e:
        logger.error(f"Week stats'da xato: {e}")
        await callback.answer(MSG_STATS_ERROR, show_alert=True)


# FOYDALANUVCHILAR HANDLERS
async def handle_users_callbacks(callback: CallbackQuery, data: str, state: FSMContext):
    """Foydalanuvchilar callback'larini boshqarish"""
    logger.info(f"Users callback ishga tushdi: {data}")
    
    # Admin ID o'chirib tashlash
    if data.startswith("users_remove_admin_"):
        user_id_to_remove = int(data.replace("users_remove_admin_", ""))
        await remove_admin(callback, user_id_to_remove)
        return
    
    actions = {
        "users_list": lambda: show_users_list(callback),
        "users_search": lambda: start_user_search(callback, state),
        "users_active": lambda: show_active_users(callback),
        "users_blocked": lambda: show_blocked_users(callback),
        "users_admins": lambda: show_admin_users(callback),
        "users_add_admin": lambda: start_add_admin(callback, state),
        "users_stats": lambda: show_user_stats(callback, get_database()),
    }
    action = actions.get(data)
    if action:
        logger.info(f"Users action: {data}")
        await action()
    else:
        logger.warning(f"Noma'lum users callback: {data}")


async def start_user_search(callback: CallbackQuery, state: FSMContext):
    """Foydalanuvchi qidirishni boshlash"""
    await callback.message.edit_text(
        "🔍 <b>Foydalanuvchi qidirish</b>\n\n"
        "Qidirish uchun ma'lumot kiriting:\n\n"
        "<b>Qidirishingiz mumkin:</b>\n"
        "• User ID\n"
        "• Username (@username)\n"
        "• Ism\n\n"
        "❌ Bekor qilish uchun /cancel"
    )
    await state.set_state(AdminStates.waiting_user_search)


async def show_active_users(callback: CallbackQuery):
    """Faol foydalanuvchilar ro'yxati"""
    db = get_database()
    
    try:
        users = await db.users.get_all_users(limit=50)  # Faqat 50ta
        active_users = [user for user in users if user['status'] == 'active']
        
        if not active_users:
            await callback.message.edit_text(
                "👥 Faol foydalanuvchilar topilmadi.",
                reply_markup=AdminKeyboards.users_menu()
            )
            return
        
        text = f"👥 <b>Faol foydalanuvchilar</b> ({len(active_users)})\n\n"
        
        for i, user in enumerate(active_users[:10], 1):  # Faqat 10tasini ko'rsatish
            username = f"@{user['username']}" if user['username'] else MSG_USERNAME_MISSING
            text += f"✅ <b>{user['first_name']}</b> ({username})\n"
            text += f"   🆔 <code>{user['user_id']}</code>\n"
            text += f"   📅 {user['registration_date'][:10]}\n\n"
        
        if len(active_users) > 10:
            text += f"... va yana {len(active_users) - 10} ta faol foydalanuvchi\n\n"
        
        await callback.message.edit_text(
            text.strip(),
            reply_markup=AdminKeyboards.users_menu()
        )
        
    except Exception as e:
        logger.error(f"Active users'da xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR, show_alert=True)


async def show_blocked_users(callback: CallbackQuery):
    """Bloklangan foydalanuvchilar ro'yxati"""
    db = get_database()
    try:
        users = await db.users.get_users_by_status("blocked", limit=50)
        if not users:
            await callback.message.edit_text(
                "🚫 Bloklangan foydalanuvchilar topilmadi.",
                reply_markup=AdminKeyboards.users_menu()
            )
            return

        text = "🚫 <b>Bloklangan foydalanuvchilar</b>\n\n"
        for user in users[:10]:
            username = f"@{user['username']}" if user['username'] else MSG_USERNAME_MISSING
            text += (
                f"🚫 <b>{user['first_name']}</b> ({username})\n"
                f"   🆔 <code>{user['user_id']}</code>\n"
                f"   📅 {user['last_activity'][:16] if user.get('last_activity') else '—'}\n\n"
            )

        await callback.message.edit_text(
            text.strip(),
            reply_markup=AdminKeyboards.users_menu()
        )
    except Exception as e:
        logger.error(f"Blocked users'da xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR, show_alert=True)


async def show_admin_users(callback: CallbackQuery):
    """Admin foydalanuvchilar ro'yxati"""
    db = get_database()
    try:
        admins = await db.users.get_admin_users(limit=50)
        
        text = "👑 <b>Admin foydalanuvchilar</b>\n\n"
        
        # Asosiy admin (config'dan)
        text += "⭐ <b>Asosiy Admin</b>\n"
        text += f"   🆔 <code>{config.ADMIN_ID}</code>\n\n"
        
        # Qo'shimcha adminlar
        if admins:
            text += "➕ <b>Qo'shimcha adminlar:</b>\n"
            buttons = []
            for admin in admins:
                if admin['user_id'] != config.ADMIN_ID:  # Asosiy adminni takrorlamaslik
                    username = f"@{admin['username']}" if admin['username'] else MSG_USERNAME_MISSING
                    text += (
                        f"👑 <b>{admin['first_name']}</b> ({username})\n"
                        f"   🆔 <code>{admin['user_id']}</code>\n"
                        f"   📅 {admin['registration_date'][:10]}\n"
                    )
                    # O'chirish tugmasi
                    buttons.append([
                        InlineKeyboardButton(
                            text=f"❌ {admin['first_name']} o'chirish",
                            callback_data=f"users_remove_admin_{admin['user_id']}"
                        )
                    ])
                    text += "\n"
        else:
            text += "📭 Qo'shimcha adminlar yo'q\n"
        
        # Orqaga tugmasi
        buttons.append([
            InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="users_add_admin")
        ])
        buttons.append([
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_users")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await callback.message.edit_text(
            text.strip(),
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Admin users'da xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR, show_alert=True)


async def start_add_admin(callback: CallbackQuery, state: FSMContext):
    """Admin qo'shishni boshlash"""
    await callback.message.edit_text(
        "👑 <b>Admin qo'shish</b>\n\n"
        "Yangi admin qilmoqchi bo'lgan foydalanuvchining ID'sini yuboring:\n\n"
        "❓ <b>ID'ni qanday olish mumkin:</b>\n"
        "• Foydalanuvchi botga /start yuborishi kerak\n"
        "• Keyin siz Foydalanuvchilar > Ro'yxat bo'limidan ID'ni ko'rishingiz mumkin\n\n"
        "❌ Bekor qilish uchun /cancel"
    )
    await state.set_state(AdminStates.waiting_admin_id)


async def remove_admin(callback: CallbackQuery, user_id: int):
    """Admin huquqini olib tashlash"""
    if user_id == config.ADMIN_ID:
        await callback.answer("❌ Asosiy adminni o'chirib bo'lmaydi!", show_alert=True)
        return
    
    db = get_database()
    try:
        # Admin huquqini olib tashlash
        await db.users.update_user(user_id, {"is_admin": False})
        
        # Foydalanuvchi ma'lumotlarini olish
        user = await db.users.get_user(user_id)
        user_name = user['first_name'] if user else str(user_id)
        
        await callback.answer(f"✅ {user_name} endi admin emas!", show_alert=True)
        
        # Ro'yxatni yangilash
        await show_admin_users(callback)
        
        logger.info(f"Admin o'chirildi: {user_id} by {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"Admin o'chirishda xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR, show_alert=True)


async def show_users_list(callback: CallbackQuery, page: int = 1):
    """Foydalanuvchilar ro'yxati"""
    db = get_database()
    
    try:
        limit = 10
        offset = (page - 1) * limit
        users = await db.users.get_all_users(limit, offset)
        total_users = await db.statistics.get_user_count()
        total_pages = math.ceil(total_users / limit)
        
        if not users:
            await callback.message.edit_text(
                "👥 Foydalanuvchilar topilmadi.",
                reply_markup=AdminKeyboards.users_menu()
            )
            return
        
        text = f"👥 <b>Foydalanuvchilar</b> (Sahifa {page}/{total_pages})\n\n"
        
        for i, user in enumerate(users, 1):
            status_emoji = "✅" if user['status'] == 'active' else "🚫"
            username = f"@{user['username']}" if user['username'] else MSG_USERNAME_MISSING
            text += f"{status_emoji} <b>{user['first_name']}</b> ({username})\n"
            text += f"   🆔 <code>{user['user_id']}</code>\n"
            text += f"   📅 {user['registration_date'][:10]}\n\n"
        
        keyboard = AdminKeyboards.pagination_menu(page, total_pages, "users_list")
        
        await callback.message.edit_text(
            text.strip(),
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Foydalanuvchilar ro'yxatida xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR, show_alert=True)


# KANALLAR HANDLERS
async def handle_channels_callbacks(callback: CallbackQuery, data: str, state: FSMContext):
    """Kanallar callback'larini boshqarish"""
    logger.info(f"Channels callback ishga tushdi: {data}")
    actions = {
        "channels_force_list": lambda: show_force_channels_list(callback),
        "channels_add": lambda: start_add_channel(callback, state),
        "channels_requests": lambda: show_channel_requests(callback),
        "channels_stats": lambda: show_channels_stats(callback),
    }
    action = actions.get(data)
    if action:
        logger.info(f"Channels action: {data}")
        await action()
    else:
        logger.warning(f"Noma'lum channels callback: {data}")


async def show_channel_requests(callback: CallbackQuery):
    """Kanal so'rovlarini ko'rsatish"""
    try:
        # Bu yerda pending requests ro'yxatini ko'rsatish kerak
        # Hozircha placeholder
        
        text = """
📝 <b>Kanal so'rovlari</b>

Hozircha so'rovlar yo'q.

📝 <b>So'rov turlari:</b>
• ⏳ Kutilayotgan
• ✅ Tasdiqlangan  
• ❌ Rad etilgan

⏰ <b>Vaqt:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}
        """
        
        await callback.message.edit_text(
            text.strip(),
            reply_markup=AdminKeyboards.channels_menu()
        )
        
    except Exception as e:
        logger.error(f"Channel requests'da xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR, show_alert=True)


async def show_channels_stats(callback: CallbackQuery):
    """Kanallar statistikasi"""
    try:
        channels = await force_subscribe_service.get_force_channels_list()
        active_channels = [ch for ch in channels if ch.get('is_active', False)]
        
        text = f"""
📊 <b>Kanallar statistikasi</b>

📢 <b>Majburiy kanallar:</b>
• Jami: {len(channels)}
• Faol: {len(active_channels)}
• Nofaol: {len(channels) - len(active_channels)}

📅 <b>Sana:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}
        """
        
        await callback.message.edit_text(
            text.strip(),
            reply_markup=AdminKeyboards.channels_menu()
        )
        
    except Exception as e:
        logger.error(f"Channels stats'da xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR, show_alert=True)


async def show_force_channels_list(callback: CallbackQuery):
    """Majburiy kanallar ro'yxati"""
    try:
        channels = await force_subscribe_service.get_force_channels_list()
        
        if not channels:
            await callback.message.edit_text(
                "📢 Majburiy kanallar ro'yxati bo'sh.",
                reply_markup=AdminKeyboards.channels_menu()
            )
            return
        
        text = "📢 <b>Majburiy kanallar</b>\n\n"
        
        for i, channel in enumerate(channels, 1):
            status_emoji = "✅" if channel['is_active'] else "⏸"
            channel_name = channel['channel_title'] or channel['channel_username'] or f"Kanal {channel['channel_id']}"
            text += f"{status_emoji} <b>{channel_name}</b>\n"
            text += f"   🆔 <code>{channel['channel_id']}</code>\n"
            if channel['channel_username']:
                text += f"   🔗 @{channel['channel_username']}\n"
            text += f"   📅 {channel['added_date'][:10]}\n\n"
        
        await callback.message.edit_text(
            text.strip(),
            reply_markup=AdminKeyboards.channels_menu()
        )
        
    except Exception as e:
        logger.error(f"Kanallar ro'yxatida xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR, show_alert=True)


async def start_add_channel(callback: CallbackQuery, state: FSMContext):
    """Kanal qo'shishni boshlash"""
    await callback.message.edit_text(
        "📢 <b>Kanal qo'shish</b>\n\n"
        "Kanal ID yoki @username kiriting:\n\n"
        "<b>Misol:</b>\n"
        "• <code>-1001234567890</code>\n"
        "• <code>@kanal_username</code>\n\n"
        "❌ Bekor qilish uchun /cancel"
    )
    await state.set_state(AdminStates.waiting_channel_id)


# So'rovlar va broadcast handlerlar keyingi qismda davom etadi...


# REQUESTS HANDLERS  
async def handle_requests_callbacks(callback: CallbackQuery, data: str):
    """So'rovlar callback'larini boshqarish"""
    logger.info(f"Requests callback ishga tushdi: {data}")
    db = get_database()
    actions = {
        "requests_pending": lambda: show_pending_requests(callback, db),
        "requests_approved": lambda: show_approved_requests(callback, db),
        "requests_rejected": lambda: show_rejected_requests(callback, db),
        "requests_stats": lambda: show_requests_stats(callback, db),
    }
    if data == "requests_refresh":
        logger.info("So'rovlar yangilash chaqirildi")
        await show_requests_menu(callback)
        await callback.answer("🔄 So'rovlar yangilandi.")
        return
    action = actions.get(data)
    if action:
        logger.info(f"Requests action: {data}")
        await action()
    else:
        logger.warning(f"Noma'lum requests callback: {data}")


async def show_pending_requests(callback: CallbackQuery, db):
    """Kutilayotgan so'rovlar"""
    try:
        requests = await db.channels.get_pending_requests()

        if not requests:
            await callback.message.edit_text(
                "⏳ Kutilayotgan so'rovlar yo'q.",
                reply_markup=AdminKeyboards.requests_menu()
            )
            return

        lines = ["⏳ <b>Kutilayotgan so'rovlar</b>"]
        for i, request in enumerate(requests[:10], 1):
            channel_name = request.get('channel_title') or request.get('channel_username') or f"ID: {request.get('channel_id')}"
            request_date = request.get('request_date', '')
            lines.append(
                (
                    f"\n{i}. <b>{channel_name}</b>\n"
                    f"   🆔 <code>{request.get('channel_id')}</code>\n"
                    f"   👤 <code>{request.get('requested_by')}</code>\n"
                    f"   📅 {request_date[:16] if request_date else '—'}"
                )
            )

        if len(requests) > 10:
            lines.append(f"\n… va yana {len(requests) - 10} ta so'rov")

        keyboard = AdminKeyboards.request_action_menu(requests[0].get('id'))
        await callback.message.edit_text(
            "\n".join(lines),
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Kutilayotgan so'rovlarda xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR, show_alert=True)


async def show_approved_requests(callback: CallbackQuery, db):
    """Tasdiqlangan so'rovlar"""
    try:
        requests = await db.channels.get_requests_by_status("approved", limit=10)

        if not requests:
            await callback.message.edit_text(
                "✅ Tasdiqlangan so'rovlar yo'q.",
                reply_markup=AdminKeyboards.requests_menu()
            )
            return

        lines = ["✅ <b>Tasdiqlangan so'rovlar</b>"]
        for i, request in enumerate(requests, 1):
            channel_name = request.get('channel_title') or request.get('channel_username') or f"ID: {request.get('channel_id')}"
            review_date = request.get('review_date', '')
            reviewer = request.get('reviewed_by')
            lines.append(
                (
                    f"\n{i}. <b>{channel_name}</b>\n"
                    f"   🆔 <code>{request.get('channel_id')}</code>\n"
                    f"   ✅ <code>{reviewer or 'admin'}</code>\n"
                    f"   🕒 {review_date[:16] if review_date else '—'}"
                )
            )

        await callback.message.edit_text(
            "\n".join(lines),
            reply_markup=AdminKeyboards.requests_menu()
        )
        
    except Exception as e:
        logger.error(f"Approved requests'da xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR, show_alert=True)


async def show_rejected_requests(callback: CallbackQuery, db):
    """Rad etilgan so'rovlar"""
    try:
        requests = await db.channels.get_requests_by_status("rejected", limit=10)

        if not requests:
            await callback.message.edit_text(
                "❌ Rad etilgan so'rovlar yo'q.",
                reply_markup=AdminKeyboards.requests_menu()
            )
            return

        lines = ["❌ <b>Rad etilgan so'rovlar</b>"]
        for i, request in enumerate(requests, 1):
            channel_name = request.get('channel_title') or request.get('channel_username') or f"ID: {request.get('channel_id')}"
            review_date = request.get('review_date', '')
            reviewer = request.get('reviewed_by')
            comment = request.get('review_comment')
            block = (
                f"\n{i}. <b>{channel_name}</b>\n"
                f"   🆔 <code>{request.get('channel_id')}</code>\n"
                f"   ❌ <code>{reviewer or 'admin'}</code>\n"
                f"   🕒 {review_date[:16] if review_date else '—'}"
            )
            lines.append(block)
            if comment:
                lines.append(f"   💬 Izoh: {comment}")

        await callback.message.edit_text(
            "\n".join(lines),
            reply_markup=AdminKeyboards.requests_menu()
        )
        
    except Exception as e:
        logger.error(f"Rejected requests'da xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR, show_alert=True)


async def show_requests_stats(callback: CallbackQuery, db):
    """So'rovlar statistikasi"""
    try:
        stats = await db.channels.get_request_stats()
        stats = stats or {}

        text = (
            "📊 <b>So'rovlar statistikasi</b>\n\n"
            "📝 <b>Umumiy:</b>\n"
            f"• Jami so'rovlar: {stats.get('total', 0)}\n"
            f"• Kutilayotgan: {stats.get('pending', 0)}\n"
            f"• Tasdiqlangan: {stats.get('approved', 0)}\n"
            f"• Rad etilgan: {stats.get('rejected', 0)}\n\n"
            f"⏰ <b>Yangilangan vaqt:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=AdminKeyboards.requests_menu()
        )
        
    except Exception as e:
        logger.error(f"Requests stats'da xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR, show_alert=True)


# BROADCAST HANDLERS
async def handle_broadcast_callbacks(callback: CallbackQuery, data: str, state: FSMContext):
    """Broadcast callback'larini boshqarish"""
    logger.info(f"Broadcast callback ishga tushdi: {data}")
    actions = {
        "broadcast_all": lambda: start_broadcast_all(callback, state),
        "broadcast_active": lambda: start_broadcast_active(callback, state),
        "broadcast_text": lambda: start_broadcast_text(callback, state),
        "broadcast_media": lambda: start_broadcast_media(callback, state),
        "broadcast_group": lambda: start_broadcast_group(callback),
        "broadcast_status": lambda: show_broadcast_status(callback),
    }
    action = actions.get(data)
    if action:
        logger.info(f"Broadcast action: {data}")
        await action()
    else:
        logger.warning(f"Noma'lum broadcast callback: {data}")


async def start_broadcast_all(callback: CallbackQuery, state: FSMContext):
    """Barchaga xabar yuborishni boshlash"""
    await callback.message.edit_text(
        "📡 <b>Barcha foydalanuvchilarga xabar</b>\n\n"
        "Yubormoqchi bo'lgan xabaringizni kiriting:\n\n"
        "<b>Qo'llab-quvvatlanadigan:</b>\n"
        "• Matn\n"
        "• Rasm + matn\n"
        "• Video + matn\n\n"
        "❌ Bekor qilish uchun /cancel"
    )
    await state.set_state(AdminStates.waiting_broadcast_message)
    await state.update_data(broadcast_target="all")


async def start_broadcast_active(callback: CallbackQuery, state: FSMContext):
    """Faol foydalanuvchilarga xabar yuborishni boshlash"""
    await callback.message.edit_text(
        "📡 <b>Faol foydalanuvchilarga xabar</b>\n\n"
        "Yubormoqchi bo'lgan xabaringizni kiriting:\n\n"
        "<b>Faol foydalanuvchilar:</b> Oxirgi 7 kun ichida bot ishlatganlar\n\n"
        "<b>Qo'llab-quvvatlanadigan:</b>\n"
        "• Matn\n"
        "• Rasm + matn\n"
        "• Video + matn\n\n"
        "❌ Bekor qilish uchun /cancel"
    )
    await state.set_state(AdminStates.waiting_broadcast_message)
    await state.update_data(broadcast_target="active")


async def start_broadcast_text(callback: CallbackQuery, state: FSMContext):
    """Matn xabar yuborishni boshlash"""
    await callback.message.edit_text(
        "📝 <b>Matn xabar yuborish</b>\n\n"
        "Yubormoqchi bo'lgan matn xabaringizni kiriting:\n\n"
        "<b>Qo'llab-quvvatlanadigan:</b>\n"
        "• HTML formatlar\n"
        "• <b>Bold</b>, <i>Italic</i>\n"
        "• <code>Code</code>\n"
        "• <a href='https://example.com'>Linklar</a>\n\n"
        "❌ Bekor qilish uchun /cancel"
    )
    await state.set_state(AdminStates.waiting_broadcast_message)
    await state.update_data(broadcast_target="all")


async def start_broadcast_media(callback: CallbackQuery, state: FSMContext):
    """Media xabar yuborishni boshlash"""
    await callback.message.edit_text(
        "🖼 <b>Media xabar yuborish</b>\n\n"
        "Rasm, video yoki audio fayl yuboring:\n\n"
        "<b>Qo'llab-quvvatlanadigan:</b>\n"
        "• Rasm (JPEG, PNG, GIF)\n"
        "• Video (MP4, AVI)\n"
        "• Audio (MP3, OGG)\n"
        "• Fayl bilan birga matn\n\n"
        "❌ Bekor qilish uchun /cancel"
    )
    await state.set_state(AdminStates.waiting_broadcast_message)
    await state.update_data(broadcast_target="all")


async def start_broadcast_group(callback: CallbackQuery):
    """Guruh bo'yicha xabar yuborishni boshlash"""
    await callback.message.edit_text(
        "🎯 <b>Guruh bo'yicha xabar yuborish</b>\n\n"
        "Qaysi foydalanuvchilar guruhiga xabar yubormoqchisiz?",
        reply_markup=AdminKeyboards.broadcast_group_menu()
    )


async def show_broadcast_status(callback: CallbackQuery):
    """Broadcast holatini ko'rsatish"""
    try:
        stats = await broadcast_service.get_broadcast_stats()

        last = stats.get('last_broadcast')
        if not last:
            text = (
                "📊 <b>Broadcast holati</b>\n\n"
                "Hozircha broadcast yuborilmagan."
            )
        else:
            last_results = last.get('results', {})
            text = (
                "📊 <b>Broadcast holati</b>\n\n"
                f"📅 <b>Oxirgi yuborilgan:</b> {last.get('timestamp')}\n"
                f"🎯 Maqsad: {last.get('target_type')}\n"
                f"👥 Foydalanuvchilar: {last_results.get('total_count', 0)}\n"
                f"✅ Muvaffaqiyatli: {last_results.get('success_count', 0)}\n"
                f"🚫 Xato: {last_results.get('failed_count', 0)}\n"
                f"⏱ Vaqt: {last.get('duration', 0):.2f}s\n\n"
                "📈 <b>Umumiy statistika:</b>\n"
                f"• Jami broadcast: {stats.get('total_broadcasts', 0)}\n"
                f"• Jami xabarlar: {stats.get('total_messages_sent', 0)}\n"
                f"• Muvaffaqiyat darajasi: {stats.get('success_rate', 0.0)}%"
            )

        await callback.message.edit_text(
            text,
            reply_markup=AdminKeyboards.broadcast_menu()
        )
        
    except Exception as e:
        logger.error(f"Broadcast status'da xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR, show_alert=True)


# STATE HANDLERS
async def handle_channel_id_input(message: Message, state: FSMContext):
    """Kanal ID kiritish"""
    if not is_admin(message.from_user.id):
        return
    
    channel_input = message.text.strip()
    
    try:
        channel_username = None
        invite_link = None

        if channel_input.startswith('@'):
            channel_username = channel_input.replace('@', '')
            try:
                chat = await message.bot.get_chat(channel_input)
                channel_id = chat.id
            except Exception as e:
                await message.answer("❌ Kanal topilmadi. Username to'g'ri ekanligini tekshiring.")
                await state.clear()
                return
        elif channel_input.startswith('-100'):
            channel_id = int(channel_input)
            try:
                chat = await message.bot.get_chat(channel_id)
                channel_username = chat.username
            except Exception as e:
                await message.answer("❌ Kanal topilmadi. ID to'g'ri ekanligini tekshiring.")
                await state.clear()
                return
        else:
            await message.answer("❌ Noto'g'ri format!\n\n"
                               "To'g'ri formatlar:\n"
                               "• @username\n"
                               "• -100XXXXXXXXXX (kanal ID)")
            await state.clear()
            return
        
        if chat.type not in ['channel', 'supergroup']:
            await message.answer("❌ Faqat kanal yoki supergroup qo'shish mumkin.")
            await state.clear()
            return

        # Bot adminligini tekshirish
        try:
            bot_member = await message.bot.get_chat_member(channel_id, message.bot.id)
            if bot_member.status not in ['administrator', 'creator']:
                await message.answer("❌ Bot bu kanalda admin emas!\n\n"
                                   "🔧 Qadamlar:\n"
                                   "1. Kanalga o'ting\n"
                                   "2. Botni admin qiling\n"
                                   "3. Qayta urinib ko'ring")
                await state.clear()
                return
        except Exception as e:
            logger.error(f"Bot adminligini tekshirib bo'lmadi: {e}")
            await message.answer("⚠️ Bot adminligini tekshirib bo'lmadi.\n"
                               "Bot kanalda admin ekanligiga ishonch hosil qiling.")
            await state.clear()
            return

        try:
            link_obj = await message.bot.create_chat_invite_link(channel_id)
            invite_link = link_obj.invite_link
        except Exception as e:
            logger.warning(f"Invite link yaratib bo'lmadi: {e}")
            invite_link = None
        
        success, message_text = await force_subscribe_service.add_force_channel(
            message.bot,
            channel_id,
            message.from_user.id,
            f"@{channel_username}" if channel_username else None,
            invite_link
        )
        
        if success:
            await message.answer(f"✅ {message_text}")
        else:
            await message.answer(f"❌ {message_text}")
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Kanal ID raqam bo'lishi kerak.")
    except Exception as e:
        logger.error(f"Kanal qo'shishda xato: {e}")
        await message.answer(MSG_GENERIC_ERROR)
        await state.clear()


async def handle_admin_id_input(message: Message, state: FSMContext):
    """Admin ID kiritish"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        # ID'ni tekshirish
        admin_id_input = message.text.strip()
        if not admin_id_input.isdigit():
            await message.answer("❌ ID faqat raqamlardan iborat bo'lishi kerak.\n\n"
                               "Iltimos, to'g'ri ID kiriting yoki /cancel tugmasini bosing.")
            return
        
        new_admin_id = int(admin_id_input)
        
        # Asosiy adminmi tekshirish
        if new_admin_id == config.ADMIN_ID:
            await message.answer("ℹ️ Bu allaqachon asosiy admin!")
            await state.clear()
            return
        
        db = get_database()
        
        # Foydalanuvchi mavjudligini tekshirish
        user = await db.users.get_user(new_admin_id)
        if not user:
            await message.answer("❌ Bunday foydalanuvchi topilmadi!\n\n"
                               "Foydalanuvchi avval botga /start yuborgan bo'lishi kerak.")
            await state.clear()
            return
        
        # Allaqachon adminmi tekshirish
        if user.get('is_admin', False):
            await message.answer(f"ℹ️ {user['first_name']} allaqachon admin!")
            await state.clear()
            return
        
        # Admin qilish
        await db.users.update_user(new_admin_id, {"is_admin": True})
        
        await message.answer(
            f"✅ <b>Muvaffaqiyatli!</b>\n\n"
            f"👤 <b>{user['first_name']}</b> endi admin!\n"
            f"🆔 ID: <code>{new_admin_id}</code>\n\n"
            f"Admin panelga kirish uchun /admin buyrug'ini ishlatishi mumkin.",
            reply_markup=AdminKeyboards.users_menu()
        )
        
        logger.info(f"Yangi admin qo'shildi: {new_admin_id} by {message.from_user.id}")
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Noto'g'ri ID formati!")
    except Exception as e:
        logger.error(f"Admin qo'shishda xato: {e}")
        await message.answer(MSG_GENERIC_ERROR)
        await state.clear()


async def handle_broadcast_message_input(message: Message, state: FSMContext):
    """Broadcast xabar kiritish"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        data = await state.get_data()
        target_type = data.get('broadcast_target', 'all')

        message_text = None
        message_object = None

        if message.content_type == 'text':
            message_text = message.html_text or message.text
        else:
            message_object = message

        result = await broadcast_service.broadcast_message(
            bot=message.bot,
            message_text=message_text,
            message_object=message_object,
            target_type=target_type,
            admin_id=message.from_user.id
        )

        if result.get('success'):
            summary = (
                "📡 <b>Broadcast yakunlandi</b>\n\n"
                f"🎯 Maqsad: {target_type}\n"
                f"👥 Jami foydalanuvchilar: {result.get('total_count', 0)}\n"
                f"✅ Yetib borgan: {result.get('success_count', 0)}\n"
                f"🚫 Xato: {result.get('failed_count', 0)}\n"
                f"⛔ Bloklaganlar: {result.get('blocked_count', 0)}\n"
                f"⏱ Vaqt: {result.get('duration', 0):.2f}s"
            )
        else:
            failure_reason = result.get('message', "Noma'lum xato")
            summary = (
                "❌ Broadcast muvaffaqiyatsiz bo'ldi.\n"
                f"Sabab: {failure_reason}"
            )

        await message.answer(summary)
        await state.clear()
        
    except Exception as e:
        logger.error(f"Broadcast xabarida xato: {e}")
        await message.answer(MSG_GENERIC_ERROR)
        await state.clear()


# Cancel handler
async def cancel_handler(message: Message, state: FSMContext):
    """Bekor qilish"""
    if not is_admin(message.from_user.id):
        return
    
    current_state = await state.get_state()
    await state.clear()

    if current_state == AdminStates.waiting_channel_id.state:
        await message.answer("❌ Kanal qo'shish bekor qilindi.", reply_markup=AdminKeyboards.channels_menu())
    elif current_state == AdminStates.waiting_broadcast_message.state:
        await message.answer("❌ Broadcast bekor qilindi.", reply_markup=AdminKeyboards.broadcast_menu())
    elif current_state == AdminStates.waiting_user_search.state:
        await message.answer("❌ Qidiruv bekor qilindi.", reply_markup=AdminKeyboards.users_menu())
    else:
        await message.answer("❌ Amal bekor qilindi.")


# ADMIN COMMAND HANDLERS
async def stats_command_handler(message: Message):
    """Stats buyrug'i handler'i"""
    logger.info(f"Stats buyrug'i ishlatildi - User: {message.from_user.id}")
    
    if not is_admin(message.from_user.id):
        await message.reply(MSG_NO_ADMIN_PERMISSION)
        return
    
    try:
        db = get_database()
        total_users = await db.statistics.get_user_count()
        active_today = await db.statistics.get_active_users_today()
        conversions_today = await db.statistics.get_conversions_today()
        
        stats_text = f"""
📊 <b>Bot statistikasi</b>

👥 <b>Foydalanuvchilar:</b>
• Jami: {total_users}
• Bugun faol: {active_today}

🎵 <b>Konversiyalar:</b>
• Bugun: {conversions_today}

📅 <b>Sana:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}
        """
        
        await message.answer(
            stats_text.strip(),
            reply_markup=AdminKeyboards.stats_menu()
        )
        
    except Exception as e:
        logger.error(f"Stats buyrug'ida xato: {e}")
        await message.answer(MSG_STATS_ERROR)


async def users_command_handler(message: Message):
    """Users buyrug'i handler'i"""
    logger.info(f"Users buyrug'i ishlatildi - User: {message.from_user.id}")
    
    if not is_admin(message.from_user.id):
        await message.reply(MSG_NO_ADMIN_PERMISSION)
        return
    
    try:
        await message.answer(
            "👥 <b>Foydalanuvchilar boshqaruvi</b>\n\nKerakli amalni tanlang:",
            reply_markup=AdminKeyboards.users_menu()
        )
        
    except Exception as e:
        logger.error(f"Users buyrug'ida xato: {e}")
        await message.answer("❌ Foydalanuvchilar menyusida xato.")


async def channels_command_handler(message: Message):
    """Channels buyrug'i handler'i"""
    logger.info(f"Channels buyrug'i ishlatildi - User: {message.from_user.id}")
    
    if not is_admin(message.from_user.id):
        await message.reply(MSG_NO_ADMIN_PERMISSION)
        return
    
    try:
        await message.answer(
            "📢 <b>Kanallar boshqaruvi</b>\n\nKerakli amalni tanlang:",
            reply_markup=AdminKeyboards.channels_menu()
        )
        
    except Exception as e:
        logger.error(f"Channels buyrug'ida xato: {e}")
        await message.answer("❌ Kanallar menyusida xato.")


async def broadcast_command_handler(message: Message):
    """Broadcast buyrug'i handler'i"""
    logger.info(f"Broadcast buyrug'i ishlatildi - User: {message.from_user.id}")
    
    if not is_admin(message.from_user.id):
        await message.reply(MSG_NO_ADMIN_PERMISSION)
        return
    
    try:
        await message.answer(
            "📡 <b>Broadcast xabarlari</b>\n\nXabar turini tanlang:",
            reply_markup=AdminKeyboards.broadcast_menu()
        )
        
    except Exception as e:
        logger.error(f"Broadcast buyrug'ida xato: {e}")
        await message.answer("❌ Broadcast menyusida xato.")


async def backup_command_handler(message: Message):
    """Backup buyrug'i handler'i"""
    logger.info(f"Backup buyrug'i ishlatildi - User: {message.from_user.id}")
    
    if not is_admin(message.from_user.id):
        await message.reply(MSG_NO_ADMIN_PERMISSION)
        return
    
    try:
        import shutil
        import os
        from datetime import datetime
        
        # Backup katalogi
        backup_dir = Path('data') / 'backups'
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup fayl nomini yaratish
        backup_filename = f"bot_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = backup_dir / backup_filename
        
        # Ma'lumotlar bazasini backup qilish
        if os.path.exists(config.DATABASE_URL):
            shutil.copy2(config.DATABASE_URL, backup_path)
            
            backup_text = f"""
💾 <b>Ma'lumotlar bazasi backup</b>

✅ <b>Muvaffaqiyatli yaratildi</b>

📁 <b>Fayl:</b> <code>{backup_filename}</code>
📅 <b>Vaqt:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
📊 <b>Hajm:</b> {os.path.getsize(backup_path) / 1024:.1f} KB

📌 <b>Joylashuv:</b> <code>{backup_path.as_posix()}</code>
            """
            
            await message.answer(backup_text.strip())
            logger.info(f"Backup yaratildi: {backup_path}")
        else:
            await message.answer("❌ Ma'lumotlar bazasi topilmadi.")
        
    except Exception as e:
        logger.error(f"Backup buyrug'ida xato: {e}")
        await message.answer(f"❌ Backup yaratishda xato: {str(e)}")


def register_admin_handlers(dp: Dispatcher):
    """Admin handler'larini ro'yxatdan o'tkazish"""
    logger.info("Admin handler'lar ro'yxatdan o'tkazilmoqda...")
    
    # Asosiy buyruqlar
    dp.message.register(admin_handler, Command("admin"))
    
    # Admin tugri buyruqlar
    dp.message.register(stats_command_handler, Command("stats"))
    dp.message.register(users_command_handler, Command("users"))
    dp.message.register(channels_command_handler, Command("channels"))
    dp.message.register(broadcast_command_handler, Command("broadcast"))
    dp.message.register(backup_command_handler, Command("backup"))
    
    logger.info("Admin /admin va qo'shimcha buyruqlar ro'yxatdan o'tkazildi")
    
    # Callback handlers
    dp.callback_query.register(
        admin_callback_handler,
        F.data.startswith(("admin_", "stats_", "users_", "channels_", "requests_", "broadcast_"))
    )
    logger.info("Admin callback handler'lar ro'yxatdan o'tkazildi")
    
    # State handlers
    dp.message.register(handle_channel_id_input, AdminStates.waiting_channel_id)
    dp.message.register(handle_admin_id_input, AdminStates.waiting_admin_id)
    dp.message.register(handle_broadcast_message_input, AdminStates.waiting_broadcast_message)
    dp.message.register(cancel_handler, Command("cancel"))
    logger.info("Admin barcha handler'lar muvaffaqiyatli ro'yxatdan o'tkazildi")
