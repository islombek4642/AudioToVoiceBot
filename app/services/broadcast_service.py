import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from aiogram import Bot
from aiogram.types import Message
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError, TelegramBadRequest

from app.core.logging import get_logger
from app.database.database import get_database

logger = get_logger(__name__)


class BroadcastService:
    """Broadcast xabarlari xizmati"""
    
    def __init__(self):
        self.db = get_database()
        self.history_file = Path("data/broadcast_history.json")
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            self.history_file.write_text("[]", encoding="utf-8")
    
    async def broadcast_message(
        self, 
        bot: Bot, 
        message_text: str = None,
        message_object: Message = None,
        target_type: str = "all",
        admin_id: int = None
    ) -> Dict[str, Any]:
        """
        Broadcast xabar yuborish
        
        Args:
            bot: Bot instance
            message_text: Yuborilishi kerak bo'lgan matn
            message_object: Forward/copy qilinadigan xabar
            target_type: "all", "active", "blocked" 
            admin_id: Admin ID (logging uchun)
        
        Returns:
            Dict with results: success_count, failed_count, total_count
        """
        try:
            # Foydalanuvchilarni olish
            users = await self._get_target_users(target_type)
            
            if not users:
                return {
                    "success": False,
                    "message": "Foydalanuvchilar topilmadi",
                    "total_count": 0,
                    "success_count": 0,
                    "failed_count": 0
                }
            
            # Broadcast natijalarini tracking qilish
            results = {
                "total_count": len(users),
                "success_count": 0,
                "failed_count": 0,
                "blocked_count": 0,
                "retry_count": 0,
                "errors": {}
            }
            
            # Xabar yuborishni boshlash
            start_time = datetime.now()
            logger.info(f"Broadcast boshlandi: {results['total_count']} foydalanuvchiga")
            
            # Batch'lar bo'yicha yuborish (30ta bir vaqtda)
            batch_size = 30
            for i in range(0, len(users), batch_size):
                batch = users[i:i + batch_size]
                
                # Parallel yuborish
                tasks = []
                for user in batch:
                    task = self._send_to_user(
                        bot, user['user_id'], message_text, message_object
                    )
                    tasks.append(task)
                
                # Batch'ni yuborish
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Natijalarni hisoblash
                for result in batch_results:
                    if isinstance(result, dict):
                        if result['success']:
                            results['success_count'] += 1
                        else:
                            results['failed_count'] += 1
                            error_type = result.get('error_type', 'unknown')
                            if error_type == 'blocked':
                                results['blocked_count'] += 1
                            elif error_type == 'retry':
                                results['retry_count'] += 1
                    else:
                        results['failed_count'] += 1
                        logger.error(f"Batch task error: {result}")
                
                # Rate limiting uchun kutish
                await asyncio.sleep(1)
            
            # Natijalarni logging qilish
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(
                f"Broadcast yakunlandi: "
                f"{results['success_count']}/{results['total_count']} muvaffaqiyatli. "
                f"Vaqt: {duration:.2f}s"
            )
            
            # Natijalarni ma'lumotlar bazasiga saqlash
            await self._log_broadcast_result(
                admin_id=admin_id,
                target_type=target_type,
                message_text=message_text[:100] if message_text else "Media",
                results=results,
                duration=duration
            )
            
            results['success'] = True
            results['duration'] = duration
            return results
            
        except Exception as e:
            logger.error(f"Broadcast'da umumiy xato: {e}")
            return {
                "success": False,
                "message": f"Xato: {str(e)}",
                "total_count": 0,
                "success_count": 0,
                "failed_count": 0
            }
    
    async def _get_target_users(self, target_type: str) -> List[Dict[str, Any]]:
        """Target foydalanuvchilarni olish"""
        try:
            if target_type == "all":
                return await self.db.users.get_all_users(limit=10000)  # Barcha foydalanuvchilar
            elif target_type == "active":
                # Faol foydalanuvchilarni olish (oxirgi 7 kun ichida faol bo'lganlar)
                return await self._get_active_users()
            elif target_type == "blocked":
                # Bloklangan foydalanuvchilarni olish
                return await self._get_blocked_users()
            else:
                return []
                
        except Exception as e:
            logger.error(f"Target users olishda xato: {e}")
            return []
    
    async def _get_active_users(self) -> List[Dict[str, Any]]:
        """Faol foydalanuvchilarni olish"""
        try:
            # Bu funksiya database'da yaratilishi kerak
            # Hozircha barcha active foydalanuvchilarni qaytaramiz
            users = await self.db.users.get_all_users(limit=10000)
            return [user for user in users if user['status'] == 'active']
        except Exception as e:
            logger.error(f"Active users olishda xato: {e}")
            return []
    
    async def _get_blocked_users(self) -> List[Dict[str, Any]]:
        """Bloklangan foydalanuvchilarni olish"""
        try:
            users = await self.db.users.get_all_users(limit=10000)
            return [user for user in users if user['status'] == 'blocked']
        except Exception as e:
            logger.error(f"Blocked users olishda xato: {e}")
            return []
    
    async def _send_to_user(
        self,
        bot: Bot,
        user_id: int,
        message_text: str = None,
        message_object: Message = None
    ) -> Dict[str, Any]:
        """Bitta foydalanuvchiga xabar yuborish"""
        try:
            if message_text:
                # Oddiy matn xabar
                await bot.send_message(chat_id=user_id, text=message_text)
            elif message_object:
                # Xabarni copy qilish
                await message_object.copy_to(chat_id=user_id)
            else:
                return {"success": False, "error_type": "no_content"}
            
            return {"success": True}
            
        except TelegramForbiddenError:
            # Foydalanuvchi botni bloklagan
            await self.db.users.set_user_status(user_id, "blocked")
            return {"success": False, "error_type": "blocked"}
        
        except TelegramRetryAfter as e:
            # Rate limit
            await asyncio.sleep(e.retry_after)
            return {"success": False, "error_type": "retry", "retry_after": e.retry_after}
        
        except TelegramBadRequest as e:
            # Noto'g'ri so'rov (user topilmagan, etc.)
            return {"success": False, "error_type": "bad_request", "error": str(e)}
        
        except Exception as e:
            # Boshqa xatolar
            logger.error(f"User {user_id} ga xabar yuborishda xato: {e}")
            return {"success": False, "error_type": "unknown", "error": str(e)}
    
    async def _log_broadcast_result(
        self,
        admin_id: int,
        target_type: str,
        message_text: str,
        results: Dict[str, Any],
        duration: float
    ):
        """Broadcast natijasini logging qilish"""
        try:
            entry = {
                "id": datetime.now().isoformat(),
                "admin_id": admin_id,
                "target_type": target_type,
                "message_preview": message_text,
                "results": results,
                "duration": duration,
                "timestamp": datetime.now().strftime('%d.%m.%Y %H:%M')
            }

            history = self._read_history()
            history.append(entry)
            self.history_file.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
            logger.info(
                f"Broadcast result saved: admin={admin_id}, target={target_type}, "
                f"total={results['total_count']}, success={results['success_count']}"
            )
            
        except Exception as e:
            logger.error(f"Broadcast result logging'da xato: {e}")
    
    async def get_broadcast_stats(self) -> Dict[str, Any]:
        """Broadcast statistikasini olish"""
        try:
            history = self._read_history()
            if not history:
                return {
                    "total_broadcasts": 0,
                    "total_messages_sent": 0,
                    "success_rate": 0.0,
                    "last_broadcast": None
                }

            total_broadcasts = len(history)
            total_messages = sum(item["results"].get("total_count", 0) for item in history)
            total_success = sum(item["results"].get("success_count", 0) for item in history)
            success_rate = round((total_success / total_messages) * 100, 2) if total_messages else 0.0

            return {
                "total_broadcasts": total_broadcasts,
                "total_messages_sent": total_messages,
                "success_rate": success_rate,
                "last_broadcast": history[-1]
            }
        except Exception as e:
            logger.error(f"Broadcast stats olishda xato: {e}")
            return {}
    
    async def cancel_broadcast(self, broadcast_id: str) -> bool:
        """Broadcast'ni to'xtatish (agar async bo'lsa)"""
        try:
            history = self._read_history()
            history.append({
                "id": broadcast_id,
                "canceled": True,
                "timestamp": datetime.now().strftime('%d.%m.%Y %H:%M')
            })
            self.history_file.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
            logger.info(f"Broadcast {broadcast_id} to'xtatildi")
            return True
        except Exception as e:
            logger.error(f"Broadcast cancel qilishda xato: {e}")
            return False

    def _read_history(self) -> List[Dict[str, Any]]:
        try:
            data = self.history_file.read_text(encoding="utf-8")
            return json.loads(data)
        except Exception:
            return []


# Global service instance
broadcast_service = BroadcastService()
