from typing import List, Optional, Tuple, Dict, Any
from aiogram import Bot
from aiogram.types import User, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from app.core.config import config
from app.core.logging import get_logger
from app.database.database import get_database

logger = get_logger(__name__)

CHAT_NOT_FOUND_LITERAL = "chat not found"


class ForceSubscribeService:
    """Majburiy obuna xizmati"""
    
    def __init__(self):
        self.db = get_database()
    
    async def check_user_subscriptions(self, bot: Bot, user_id: int) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Foydalanuvchining barcha majburiy kanallarga obuna bo'lganligini tekshirish
        
        Returns:
            Tuple[is_subscribed_to_all, list_of_unsubscribed_channels]
        """
        if not config.FORCE_SUB_ENABLED:
            return True, []
        
        try:
            # Barcha faol majburiy kanallarni olish
            channels = await self.db.channels.get_active_force_channels()
            
            if not channels:
                return True, []
            
            unsubscribed_channels = []
            
            for channel in channels:
                is_subscribed = await self._check_single_channel_subscription(
                    bot, user_id, channel['channel_id']
                )
                
                if not is_subscribed:
                    unsubscribed_channels.append(channel)
            
            is_all_subscribed = len(unsubscribed_channels) == 0
            
            logger.info(f"Foydalanuvchi {user_id}: obuna holati = {is_all_subscribed}")
            
            return is_all_subscribed, unsubscribed_channels
            
        except Exception as e:
            logger.error(f"Obuna tekshirishda xato: {e}")
            # Xato holatida foydalanuvchiga ruxsat berish
            return True, []
    
    async def _check_single_channel_subscription(self, bot: Bot, user_id: int, channel_id: int) -> bool:
        """Bitta kanalga obuna bo'lganligini tekshirish"""
        try:
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            
            # Foydalanuvchi statusini tekshirish
            if member.status in ['member', 'administrator', 'creator']:
                return True
            elif member.status == 'left':
                return False
            elif member.status == 'kicked':
                # Bloklangan foydalanuvchi
                return False
            else:
                return False
                
        except TelegramBadRequest as e:
            error_text = str(e).lower()
            if "user not found" in error_text:
                logger.warning(f"Foydalanuvchi {user_id} topilmadi")
                return False
            elif CHAT_NOT_FOUND_LITERAL in error_text:
                logger.warning(f"Kanal {channel_id} topilmadi")
                return True  # Kanal topilmasa, obuna shartini o'tkazish
            else:
                logger.error(f"Telegram API xatosi: {e}")
                return True  # Noma'lum xatolarda ruxsat berish
                
        except TelegramForbiddenError:
            logger.warning(f"Bot kanal {channel_id}ga kirish huquqiga ega emas")
            return True  # Bot ruxsati bo'lmasa, obuna shartini o'tkazish
            
        except Exception as e:
            logger.error(f"Obuna tekshirishda kutilmagan xato: {e}")
            return True  # Xato holatida ruxsat berish
    
    def create_subscription_keyboard(self, channels: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        """Obuna bo'lish uchun keyboard yaratish"""
        buttons = []

        for channel in channels:
            channel_name = (
                channel.get('channel_title')
                or channel.get('channel_username')
                or f"Kanal {channel['channel_id']}"
            )

            # Kanalga o'tish tugmasi
            if channel.get('channel_username'):
                url = f"https://t.me/{channel['channel_username'].replace('@', '')}"
            elif channel.get('invite_link'):
                url = channel['invite_link']
            else:
                # Agar link bo'lmasa, kanal ID orqali (-100 prefiksini olib tashlash)
                url = f"https://t.me/c/{str(channel['channel_id'])[4:]}"

            button = InlineKeyboardButton(
                text=f"📢 {channel_name}",
                url=url,
            )
            buttons.append([button])

        # Tekshirish tugmasi
        check_button = InlineKeyboardButton(
            text="✅ Obunani tekshirish",
            callback_data="check_subscription",
        )
        buttons.append([check_button])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    def get_subscription_message(self, channels: List[Dict[str, Any]]) -> str:
        """Obuna xabari matnini yaratish"""
        if not channels:
            return "✅ Barcha majburiy kanallarga obuna bo'lgansiz!"

        channel_list = []
        for i, channel in enumerate(channels, 1):
            channel_name = (
                channel.get('channel_title')
                or channel.get('channel_username')
                or f"Kanal {channel['channel_id']}"
            )
            channel_list.append(f"{i}. {channel_name}")

        channels_text = "\n".join(channel_list)

        message = f"""
🔒 <b>Majburiy obuna</b>

Botdan foydalanish uchun quyidagi kanal/guruhlarga obuna bo'lishingiz kerak:

{channels_text}

📌 Obuna bo'lgandan so'ng "✅ Obunani tekshirish" tugmasini bosing.
        """

        return message.strip()
    
    async def _validate_channel_and_bot_permissions(self, bot: Bot, channel_id: int) -> Tuple[bool, str, Optional[Any]]:
        """Kanal va bot ruxsatlarini tekshirish"""
        try:
            chat = await bot.get_chat(channel_id)
            bot_member = await bot.get_chat_member(channel_id, bot.id)
            
            if bot_member.status not in ['administrator', 'creator']:
                return False, "❌ Bot bu kanalda admin emas. Avval botni kanal adminliriga qo'shing.", None
            
            return True, "", chat
            
        except TelegramBadRequest as e:
            error_text = str(e).lower()
            if CHAT_NOT_FOUND_LITERAL in error_text:
                return False, "❌ Kanal topilmadi. Kanal ID'ni tekshiring.", None
            else:
                return False, f"❌ Telegram API xatosi: {e}", None
    
    def _prepare_channel_data(self, channel_id: int, admin_id: int, chat, channel_username: str = None, invite_link: str = None) -> Dict[str, Any]:
        """Kanal ma'lumotlarini tayyorlash"""
        return {
            'channel_id': channel_id,
            'channel_username': channel_username or chat.username,
            'channel_title': chat.title or chat.first_name,
            'channel_type': chat.type,
            'added_by': admin_id,
            'invite_link': invite_link
        }
    
    async def _try_create_invite_link(self, bot: Bot, channel_id: int, chat, channel_data: Dict[str, Any]) -> None:
        """Invite link yaratishga harakat qilish"""
        try:
            if chat.type in ['channel', 'supergroup']:
                invite_link_obj = await bot.create_chat_invite_link(channel_id)
                channel_data['invite_link'] = invite_link_obj.invite_link
        except Exception as e:
            logger.warning(f"Invite link yaratishda xato: {e}")
    
    async def add_force_channel(
        self, 
        bot: Bot, 
        channel_id: int, 
        admin_id: int,
        channel_username: str = None,
        invite_link: str = None
    ) -> Tuple[bool, str]:
        """Majburiy obuna kanalini qo'shish"""
        try:
            # Kanalning mavjudligini va bot ruxsatlarini tekshirish
            is_valid, error_msg, chat = await self._validate_channel_and_bot_permissions(bot, channel_id)
            if not is_valid:
                return False, error_msg
            
            # Kanal ma'lumotlarini to'ldirish
            channel_data = self._prepare_channel_data(channel_id, admin_id, chat, channel_username, invite_link)
            
            # Invite link olishga harakat qilish
            if not invite_link:
                await self._try_create_invite_link(bot, channel_id, chat, channel_data)
            
            # Ma'lumotlar bazasiga qo'shish
            success = await self.db.channels.add_force_channel(channel_data)
            
            if success:
                channel_name = channel_data['channel_title'] or channel_data['channel_username']
                return True, f"✅ Kanal '{channel_name}' majburiy obuna ro'yxatiga qo'shildi"
            else:
                return False, "❌ Ma'lumotlar bazasiga yozishda xato"
                
        except Exception as e:
            logger.error(f"Majburiy kanal qo'shishda xato: {e}")
            return False, f"❌ Kutilmagan xato: {str(e)}"
    
    async def remove_force_channel(self, channel_id: int) -> Tuple[bool, str]:
        """Majburiy obuna kanalini o'chirish"""
        try:
            success = await self.db.channels.deactivate_channel(channel_id)
            
            if success:
                return True, "✅ Kanal majburiy obuna ro'yxatidan o'chirildi"
            else:
                return False, "❌ Kanalni o'chirishda xato"
                
        except Exception as e:
            logger.error(f"Majburiy kanalni o'chirishda xato: {e}")
            return False, f"❌ Xato: {str(e)}"
    
    async def get_force_channels_list(self) -> List[Dict[str, Any]]:
        """Majburiy kanallar ro'yxatini olish"""
        try:
            return await self.db.channels.get_active_force_channels()
        except Exception as e:
            logger.error(f"Majburiy kanallar ro'yxatini olishda xato: {e}")
            return []
    
    async def create_channel_request(
        self,
        bot: Bot,
        channel_id: int,
        requester_id: int,
        channel_username: str = None,
        invite_link: str = None
    ) -> Tuple[bool, str]:
        """Kanal qo'shish so'rovi yaratish"""
        try:
            # Kanalning mavjudligini tekshirish
            try:
                chat = await bot.get_chat(channel_id)
                
                request_data = {
                    'channel_id': channel_id,
                    'channel_username': channel_username or chat.username,
                    'channel_title': chat.title or chat.first_name,
                    'channel_type': chat.type,
                    'requested_by': requester_id,
                    'invite_link': invite_link
                }
                
                success = await self.db.channels.create_channel_request(request_data)
                
                if success:
                    channel_name = request_data['channel_title'] or request_data['channel_username']
                    return True, f"✅ '{channel_name}' kanali uchun so'rov yuborildi. Admin tasdiqini kuting."
                else:
                    return False, "❌ So'rovni yuborishda xato"
                    
            except TelegramBadRequest as e:
                error_text = str(e).lower()
                if CHAT_NOT_FOUND_LITERAL in error_text:
                    return False, "❌ Kanal topilmadi. Kanal ID'ni yoki username'ni tekshiring."
                else:
                    return False, f"❌ Telegram API xatosi: {e}"
                    
        except Exception as e:
            logger.error(f"Kanal so'rovi yaratishda xato: {e}")
            return False, f"❌ Kutilmagan xato: {str(e)}"


# Global service instance
force_subscribe_service = ForceSubscribeService()
