from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.core.config import config
from app.core.logging import get_logger
from app.database.database import get_database
from app.services.force_subscribe import force_subscribe_service
from app.utils.keyboards import UserKeyboards, AdminKeyboards
from app.utils.messages import (
    MSG_GENERIC_ERROR,
    MSG_GENERIC_ERROR_BANG,
    MSG_USERNAME_MISSING,
)

logger = get_logger(__name__)


class ChannelRequestStates(StatesGroup):
    waiting_channel_info = State()
    waiting_admin_comment = State()


# FOYDALANUVCHI KANAL SO'ROVI TIZIMI
async def request_channel_handler(message: Message):
    """Kanal so'rovi buyrug'i"""
    try:
        await message.answer(
            "📢 <b>Kanal qo'shish so'rovi</b>\n\n"
            "Kanallarni majburiy obuna tizimiga qo'shish uchun so'rov yuborishingiz mumkin.\n\n"
            "📋 <b>Talablar:</b>\n"
            "• Bot kanalda admin bo'lishi kerak\n"
            "• Kanal faol va foydalanuvchilarga foydali bo'lishi kerak\n"
            "• Spam yoki noo'rin kontent bo'lmasligi kerak\n\n"
            "🎯 Kerakli amalni tanlang:",
            reply_markup=UserKeyboards.request_channel_menu()
        )
        
    except Exception as e:
        logger.error(f"Request channel handler'da xato: {e}")
        await message.reply(MSG_GENERIC_ERROR)


async def request_channel_callback(callback: CallbackQuery, state: FSMContext):
    """Kanal so'rovi callback"""
    data = callback.data
    user_id = callback.from_user.id
    
    try:
        if data == "request_channel":
            await start_channel_request(callback, state)
        elif data == "my_requests":
            await show_my_requests(callback, user_id, page=1)
        elif data.startswith("my_requests_page_"):
            try:
                page = int(data.split("_")[-1])
                page = max(1, page)
            except ValueError:
                page = 1
            await show_my_requests(callback, user_id, page=page)
        elif data == "request_help":
            await show_request_help(callback)
        elif data == "cancel":
            await callback.message.delete()
            await state.clear()
            await callback.answer("❌ Bekor qilindi.")
            
    except Exception as e:
        logger.error(f"Request callback'da xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR, show_alert=True)


async def start_channel_request(callback: CallbackQuery, state: FSMContext):
    """Kanal so'rovini boshlash"""
    await callback.message.edit_text(
        "📢 <b>Yangi kanal so'rovi</b>\n\n"
        "Qo'shmoqchi bo'lgan kanal haqida ma'lumot kiriting:\n\n"
        "<b>Format:</b>\n"
        "<b>Kanal ID/Username:</b> @kanal_username yoki -1001234567890\n"
        "<b>Kanal nomi:</b> Kanal to'liq nomi\n"
        "<b>Tavsif:</b> Kanal nima haqida\n"
        "<b>Invite link:</b> https://t.me/+abc123 (agar bor bo'lsa)\n\n"
        "<b>Misol:</b>\n"
        "@test_kanal\n"
        "Test Kanali\n"
        "Dasturlash bo'yicha maslahatlar\n"
        "https://t.me/+abc123\n\n"
        "❌ Bekor qilish uchun /cancel",
        reply_markup=UserKeyboards.cancel_menu()
    )
    await state.set_state(ChannelRequestStates.waiting_channel_info)


async def handle_channel_request_input(message: Message, state: FSMContext):
    """Kanal ma'lumotlarini kiritish"""
    try:
        user_input = message.text.strip()
        lines = user_input.split('\n')
        
        if len(lines) < 2:
            await message.reply(
                "❌ Noto'g'ri format!\n\n"
                "Kamida kanal ID/username va nomini kiriting."
            )
            return
        
        # Ma'lumotlarni parsing qilish
        channel_info = lines[0].strip()
        channel_name = lines[1].strip()
        
        invite_link = lines[3].strip() if len(lines) > 3 else ""
        
        # Kanal ID yoki username'ni aniqlash
        channel_id = None
        channel_username = None
        
        if channel_info.startswith('@'):
            channel_username = channel_info
        elif channel_info.startswith('-') or channel_info.isdigit():
            try:
                channel_id = int(channel_info)
            except ValueError:
                await message.reply("❌ Noto'g'ri kanal ID formati.")
                return
        else:
            await message.reply(
                "❌ Kanal ID -1001234567890 formatida yoki @username formatida bo'lishi kerak."
            )
            return
        
        # So'rovni yaratish
        request_data = {
            'channel_id': channel_id or 0,  # Placeholder for username
            'channel_username': channel_username,
            'channel_title': channel_name,
            'channel_type': 'channel',
            'requested_by': message.from_user.id,
            'invite_link': invite_link if invite_link.startswith('http') else None
        }
        
        # So'rovni ma'lumotlar bazasiga saqlash
        db = get_database()
        
        # Agar username bo'lsa, ID ni olishga harakat qilish
        if channel_username and not channel_id:
            try:
                chat = await message.bot.get_chat(channel_username)
                request_data['channel_id'] = chat.id
                request_data['channel_title'] = chat.title or channel_name
                request_data['channel_type'] = chat.type
            except Exception as e:
                logger.warning(f"Username orqali kanal ma'lumotini olishda xato: {e}")
                # Username bo'yicha so'rov yuboriladi
        
        success = await db.channels.create_channel_request(request_data)
        
        if success:
            # Admin'ga xabar yuborish
            await notify_admin_about_request(message.bot, request_data, message.from_user)
            
            await message.answer(
                "✅ <b>So'rov muvaffaqiyatli yuborildi!</b>\n\n"
                f"📢 <b>Kanal:</b> {channel_name}\n"
                f"👤 <b>So'rovchi:</b> {message.from_user.first_name}\n\n"
                "🔔 Admin ko'rib chiqgandan so'ng sizga xabar beriladi.\n"
                "📊 So'rovlaringizni /my_requests buyrug'i orqali kuzatishingiz mumkin."
            )
        else:
            await message.answer("❌ So'rovni yuborishda xato yuz berdi.")
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Channel request input'da xato: {e}")
        await message.reply("❌ Xato yuz berdi. Qaytadan urinib ko'ring.")
        await state.clear()


async def show_my_requests(callback: CallbackQuery, user_id: int, page: int = 1):
    """Foydalanuvchining so'rovlarini ko'rsatish"""
    try:
        db = get_database()
        per_page = 5
        offset = (page - 1) * per_page
        requests = await db.channels.get_user_requests(user_id, limit=per_page + 1, offset=offset)
        has_next = len(requests) > per_page
        if has_next:
            requests = requests[:per_page]
        has_prev = page > 1
        
        if not requests:
            text = (
                "📊 <b>Sizning so'rovlaringiz</b>\n\n"
                "Hozircha kanal so'rovlari topilmadi.\n\n"
                "📌 Yangi kanal qo'shish uchun '📢 Kanal qo'shish so'rovi' tugmasini bosing."
            )
        else:
            lines = ["📊 <b>Sizning so'rovlaringiz</b>"]
            status_map = {
                "pending": "⏳ Kutilmoqda",
                "approved": "✅ Tasdiqlangan",
                "rejected": "❌ Rad etilgan"
            }
            for idx, req in enumerate(requests, start=offset + 1):
                channel_name = req.get('channel_title') or req.get('channel_username') or f"ID: {req.get('channel_id')}"
                status = req.get('status', 'pending')
                status_label = status_map.get(status, status.capitalize())
                request_date = req.get('request_date', '')
                reviewed_comment = req.get('review_comment')
                review_date = req.get('review_date')
                lines.append(
                    (
                        f"\n{idx}. <b>{channel_name}</b>\n"
                        f"   {status_label}\n"
                        f"   📅 {request_date[:16] if request_date else '—'}"
                    )
                )
                if status != 'pending':
                    reviewer = req.get('reviewed_by')
                    review_line = f"   👤 Admin: <code>{reviewer}</code>" if reviewer else ""
                    date_line = f"   🕒 {review_date[:16]}" if review_date else ""
                    if review_line:
                        lines.append(review_line)
                    if date_line:
                        lines.append(date_line)
                    if reviewed_comment:
                        lines.append(f"   💬 Izoh: {reviewed_comment}")
            text = "\n".join(lines)
            text += "\n\nℹ️ Yangi so'rov yuborganingizdan so'ng natijasi shu yerda ko'rinadi."
        
        keyboard = UserKeyboards.user_requests_navigation(page, has_prev, has_next)
        await callback.message.edit_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"My requests'da xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR, show_alert=True)


async def show_request_help(callback: CallbackQuery):
    """So'rov yordam ma'lumotlari"""
    help_text = """
❓ <b>Kanal so'rovi haqida yordam</b>

📋 <b>So'rov yuborish jarayoni:</b>
1. "📢 Kanal qo'shish so'rovi" tugmasini bosing
2. Kanal ma'lumotlarini to'ldiring
3. So'rovni yuboring
4. Admin javobini kuting

✅ <b>Tasdiqlanish shartlari:</b>
• Bot kanalda admin bo'lishi kerak
• Kanal foydalanuvchilarga foydali bo'lishi kerak
• Spam yoki noo'rin kontent bo'lmasligi kerak
• Kanal faol va yangilanib turishi kerak

⏱ <b>Ko'rib chiqish vaqti:</b>
Odatda 24 soat ichida javob beriladi.

📞 <b>Qo'shimcha savollar:</b>
Admin bilan bog'laning: @admin_username
    """
    
    await callback.message.edit_text(
        help_text.strip(),
        reply_markup=UserKeyboards.request_channel_menu()
    )


# ADMIN SO'ROVLARNI BOSHQARISH TIZIMI
async def notify_admin_about_request(bot, request_data, user):
    """Admin'ga yangi so'rov haqida xabar yuborish"""
    try:
        if not config.ADMIN_ID:
            return
        
        channel_name = request_data['channel_title']
        channel_id = request_data['channel_id']
        username = f"@{user.username}" if user.username else MSG_USERNAME_MISSING
        
        admin_text = f"""
🔔 <b>Yangi kanal so'rovi!</b>

📢 <b>Kanal:</b> {channel_name}
🆔 <b>ID:</b> <code>{channel_id}</code>
👤 <b>So'rovchi:</b> {user.first_name} ({username})
🆔 <b>User ID:</b> <code>{user.id}</code>

⚡ Admin panel orqali ko'rib chiqing: /admin
        """
        
        await bot.send_message(
            chat_id=config.ADMIN_ID,
            text=admin_text.strip()
        )
        
    except Exception as e:
        logger.error(f"Admin'ga xabar yuborishda xato: {e}")


async def handle_request_approval(callback: CallbackQuery, state: FSMContext):
    """So'rovni tasdiqlash"""
    data = callback.data
    
    if not data.startswith("request_"):
        return
    
    parts = data.split("_")
    if len(parts) < 3:
        return
    
    action = parts[1]  # approve, reject, view
    request_id = parts[2]
    
    try:
        db = get_database()
        
        if action == "approve":
            # So'rovni tasdiqlash
            success = await db.channels.approve_request(
                int(request_id), 
                callback.from_user.id
            )
            
            if success:
                await callback.answer("✅ So'rov tasdiqlandi!", show_alert=True)
                # Foydalanuvchiga xabar yuborish
                await notify_user_about_approval(callback.bot, int(request_id), True)
                await show_pending_requests(callback, db)
            else:
                await callback.answer("❌ Tasdiqlashda xato!", show_alert=True)
        
        elif action == "reject":
            # Izoh so'rash
            await callback.message.edit_text(
                "❌ <b>So'rovni rad etish</b>\n\n"
                "Rad etish sababini kiriting:",
                reply_markup=UserKeyboards.cancel_menu()
            )
            await state.set_state(ChannelRequestStates.waiting_admin_comment)
            await state.update_data(request_id=request_id, action="reject")
        
        elif action == "view":
            # So'rov tafsilotlarini ko'rsatish
            await show_request_details(callback, int(request_id), db)
        else:
            await callback.answer("❓ Noma'lum amal.")
            
    except Exception as e:
        logger.error(f"Request approval'da xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR_BANG, show_alert=True)


async def handle_admin_comment_input(message: Message, state: FSMContext):
    """Admin izohini kiritish"""
    if message.from_user.id != config.ADMIN_ID:
        return
    
    try:
        data = await state.get_data()
        request_id = data.get('request_id')
        action = data.get('action')
        comment = message.text.strip()
        
        if not request_id or not action:
            await message.reply("❌ Sessiya ma'lumotlari yo'q.")
            await state.clear()
            return
        
        db = get_database()
        
        if action == "reject":
            success = await db.channels.reject_request(
                int(request_id),
                message.from_user.id,
                comment
            )
            
            if success:
                await message.answer("✅ So'rov rad etildi.")
                # Foydalanuvchiga xabar yuborish
                await notify_user_about_approval(message.bot, int(request_id), False, comment)
            else:
                await message.answer("❌ Rad etishda xato!")
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Admin comment'da xato: {e}")
        await message.reply(MSG_GENERIC_ERROR)
        await state.clear()


async def notify_user_about_approval(bot, request_id: int, approved: bool, comment: str = None):
    """Foydalanuvchiga so'rov natijasi haqida xabar yuborish"""
    try:
        db = get_database()
        request = await db.channels.get_request_by_id(request_id)
        if not request:
            logger.warning(f"So'rov topilmadi, foydalanuvchiga xabar yuborilmadi: {request_id}")
            return

        user_id = request.get('requested_by')
        if not user_id:
            logger.warning(f"So'rovda foydalanuvchi ID yo'q: {request_id}")
            return

        channel_name = request.get('channel_title') or request.get('channel_username') or f"ID: {request.get('channel_id')}"
        status_text = "✅ So'rovingiz tasdiqlandi!" if approved else "❌ So'rovingiz rad etildi."
        next_step = "Bot endi kanalni majburiy obuna ro'yxatiga qo'shadi." if approved else "Agar xatoni to'g'rilab qayta yubormoqchi bo'lsangiz, /request_channel buyrug'idan foydalaning."

        text_lines = [
            status_text,
            f"\n📢 <b>Kanal:</b> {channel_name}",
            f"🆔 <b>So'rov ID:</b> {request_id}",
            f"📅 <b>Yuborilgan:</b> {request.get('request_date', '')[:16] if request.get('request_date') else '—'}",
            f"ℹ️ {next_step}"
        ]

        if not approved and comment:
            text_lines.append(f"\n💬 <b>Admin izohi:</b> {comment}")

        await bot.send_message(
            chat_id=user_id,
            text="\n".join(text_lines),
            disable_web_page_preview=True
        )
        logger.info(f"Foydalanuvchiga so'rov natijasi yuborildi: user={user_id}, request={request_id}, approved={approved}")
        
    except Exception as e:
        logger.error(f"User notification'da xato: {e}")


async def show_request_details(callback: CallbackQuery, request_id: int, db):
    """So'rov tafsilotlarini ko'rsatish"""
    try:
        request_data = await db.channels.get_request_by_id(request_id)
        if not request_data:
            await callback.answer("❌ So'rov topilmadi.", show_alert=True)
            return

        status_map = {
            "pending": "⏳ Kutilmoqda",
            "approved": "✅ Tasdiqlangan",
            "rejected": "❌ Rad etilgan"
        }

        channel_name = request_data.get('channel_title') or request_data.get('channel_username') or f"ID: {request_data.get('channel_id')}"
        status = request_data.get('status', 'pending')
        status_label = status_map.get(status, status.capitalize())
        request_date = request_data.get('request_date', '')
        review_date = request_data.get('review_date', '')
        review_comment = request_data.get('review_comment')
        invite_link = request_data.get('invite_link')
        requested_by = request_data.get('requested_by')
        reviewed_by = request_data.get('reviewed_by')

        details = [
            "👁 <b>So'rov tafsilotlari</b>",
            f"\n📢 <b>Kanal:</b> {channel_name}",
            f"🆔 <b>ID:</b> <code>{request_data.get('channel_id')}</code>",
            f"👤 <b>So'rovchi:</b> <code>{requested_by}</code>",
            f"📅 <b>Yuborilgan:</b> {request_date[:16] if request_date else '—'}",
            f"📌 <b>Holat:</b> {status_label}"
        ]

        if invite_link:
            details.append(f"🔗 <b>Link:</b> {invite_link}")

        if status != 'pending':
            if reviewed_by:
                details.append(f"👮 <b>Admin:</b> <code>{reviewed_by}</code>")
            if review_date:
                details.append(f"🕒 <b>Ko'rib chiqildi:</b> {review_date[:16]}")
            if review_comment:
                details.append(f"💬 <b>Izoh:</b> {review_comment}")

        await callback.message.edit_text(
            "\n".join(details),
            reply_markup=AdminKeyboards.request_action_menu(request_id)
        )
        
    except Exception as e:
        logger.error(f"Request details'da xato: {e}")
        await callback.answer(MSG_GENERIC_ERROR_BANG, show_alert=True)


def register_channel_request_handlers(dp: Dispatcher):
    """Kanal so'rovlari handler'larini ro'yxatdan o'tkazish"""
    # Foydalanuvchi buyruqlari
    dp.message.register(request_channel_handler, Command("request_channel"))
    
    # Callback handlers
    dp.callback_query.register(
        request_channel_callback,
        F.data.in_(["request_channel", "my_requests", "request_help", "cancel"])
    )
    
    # Admin approval handlers
    dp.callback_query.register(
        handle_request_approval,
        F.data.startswith("request_")
    )
    
    # State handlers
    dp.message.register(handle_channel_request_input, ChannelRequestStates.waiting_channel_info)
    dp.message.register(handle_admin_comment_input, ChannelRequestStates.waiting_admin_comment)
