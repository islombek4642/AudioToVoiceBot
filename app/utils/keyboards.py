from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


STATISTICS_TEXT = "📊 Statistika"
BACK_TEXT = "🔙 Orqaga"


class AdminKeyboards:
    """Admin paneli uchun keyboard'lar"""
    
    @staticmethod
    def main_admin_menu() -> InlineKeyboardMarkup:
        """Asosiy admin menu"""
        buttons = [
            [
                InlineKeyboardButton(text=STATISTICS_TEXT, callback_data="admin_stats"),
                InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton(text="📢 Kanallar", callback_data="admin_channels"),
                InlineKeyboardButton(text="📝 So'rovlar", callback_data="admin_requests")
            ],
            [
                InlineKeyboardButton(text="📡 Broadcast", callback_data="admin_broadcast"),
                InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="admin_settings")
            ],
            [
                InlineKeyboardButton(text="🔧 Texnik", callback_data="admin_technical"),
                InlineKeyboardButton(text="🚪 Chiqish", callback_data="admin_exit")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def stats_menu() -> InlineKeyboardMarkup:
        """Statistika menu"""
        buttons = [
            [
                InlineKeyboardButton(text="📈 Umumiy", callback_data="stats_general"),
                InlineKeyboardButton(text="👤 Foydalanuvchilar", callback_data="stats_users")
            ],
            [
                InlineKeyboardButton(text="🎵 Konversiyalar", callback_data="stats_conversions"),
                InlineKeyboardButton(text="📢 Kanallar", callback_data="stats_channels")
            ],
            [
                InlineKeyboardButton(text="📅 Bugun", callback_data="stats_today"),
                InlineKeyboardButton(text="📆 Bu hafta", callback_data="stats_week")
            ],
            [
                InlineKeyboardButton(text="🔄 Yangilash", callback_data="stats_refresh"),
                InlineKeyboardButton(text=BACK_TEXT, callback_data="admin_back")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def users_menu() -> InlineKeyboardMarkup:
        """Foydalanuvchilar menu"""
        buttons = [
            [
                InlineKeyboardButton(text="📋 Ro'yxat", callback_data="users_list"),
                InlineKeyboardButton(text="🔍 Qidirish", callback_data="users_search")
            ],
            [
                InlineKeyboardButton(text="✅ Faollar", callback_data="users_active"),
                InlineKeyboardButton(text="🚫 Bloklangan", callback_data="users_blocked")
            ],
            [
                InlineKeyboardButton(text="👑 Adminlar", callback_data="users_admins"),
                InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="users_add_admin")
            ],
            [
                InlineKeyboardButton(text=STATISTICS_TEXT, callback_data="users_stats"),
                InlineKeyboardButton(text=BACK_TEXT, callback_data="admin_back")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def channels_menu() -> InlineKeyboardMarkup:
        """Kanallar menu"""
        buttons = [
            [
                InlineKeyboardButton(text="📋 Majburiy kanallar", callback_data="channels_force_list"),
                InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="channels_add")
            ],
            [
                InlineKeyboardButton(text="📝 So'rovlar", callback_data="channels_requests"),
                InlineKeyboardButton(text=STATISTICS_TEXT, callback_data="channels_stats")
            ],
            [
                InlineKeyboardButton(text="🔧 Sozlamalar", callback_data="channels_settings"),
                InlineKeyboardButton(text=BACK_TEXT, callback_data="admin_back")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def broadcast_menu() -> InlineKeyboardMarkup:
        """Broadcast menu"""
        buttons = [
            [
                InlineKeyboardButton(text="📢 Barchaga", callback_data="broadcast_all"),
                InlineKeyboardButton(text="👥 Faoللarga", callback_data="broadcast_active")
            ],
            [
                InlineKeyboardButton(text="🎯 Guruhga", callback_data="broadcast_group"),
                InlineKeyboardButton(text="📝 Matn", callback_data="broadcast_text")
            ],
            [
                InlineKeyboardButton(text="🖼 Media", callback_data="broadcast_media"),
                InlineKeyboardButton(text="📊 Holat", callback_data="broadcast_status")
            ],
            [
                InlineKeyboardButton(text=BACK_TEXT, callback_data="admin_back")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def broadcast_group_menu() -> InlineKeyboardMarkup:
        """Broadcast guruh tanlash menyusi"""
        buttons = [
            [InlineKeyboardButton(text="🆕 Yangi foydalanuvchilar", callback_data="broadcast_group_new")],
            [InlineKeyboardButton(text="🛌 Noaktiv foydalanuvchilar", callback_data="broadcast_group_inactive")],
            [InlineKeyboardButton(text="👑 VIP/Premium", callback_data="broadcast_group_vip")],
            [InlineKeyboardButton(text=BACK_TEXT, callback_data="broadcast_group_back")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def requests_menu() -> InlineKeyboardMarkup:
        """So'rovlar menu"""
        buttons = [
            [
                InlineKeyboardButton(text="⏳ Kutilayotgan", callback_data="requests_pending"),
                InlineKeyboardButton(text="✅ Tasdiqlangan", callback_data="requests_approved")
            ],
            [
                InlineKeyboardButton(text="❌ Rad etilgan", callback_data="requests_rejected"),
                InlineKeyboardButton(text=STATISTICS_TEXT, callback_data="requests_stats")
            ],
            [
                InlineKeyboardButton(text="🔄 Yangilash", callback_data="requests_refresh"),
                InlineKeyboardButton(text=BACK_TEXT, callback_data="admin_back")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def user_action_menu(user_id: int) -> InlineKeyboardMarkup:
        """Foydalanuvchi harakatlari menu"""
        buttons = [
            [
                InlineKeyboardButton(text="👤 Ma'lumotlar", callback_data=f"user_info_{user_id}"),
                InlineKeyboardButton(text=STATISTICS_TEXT, callback_data=f"user_stats_{user_id}")
            ],
            [
                InlineKeyboardButton(text="🚫 Bloklash", callback_data=f"user_block_{user_id}"),
                InlineKeyboardButton(text="✅ Aktivlash", callback_data=f"user_activate_{user_id}")
            ],
            [
                InlineKeyboardButton(text="💬 Xabar", callback_data=f"user_message_{user_id}"),
                InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"user_delete_{user_id}")
            ],
            [
                InlineKeyboardButton(text=BACK_TEXT, callback_data="users_list")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def channel_action_menu(channel_id: int) -> InlineKeyboardMarkup:
        """Kanal harakatlari menu"""
        buttons = [
            [
                InlineKeyboardButton(text="👁 Ko'rish", callback_data=f"channel_view_{channel_id}"),
                InlineKeyboardButton(text=STATISTICS_TEXT, callback_data=f"channel_stats_{channel_id}")
            ],
            [
                InlineKeyboardButton(text="⏸ Faolsizlashtirish", callback_data=f"channel_disable_{channel_id}"),
                InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"channel_delete_{channel_id}")
            ],
            [
                InlineKeyboardButton(text=BACK_TEXT, callback_data="channels_force_list")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def request_action_menu(request_id: int) -> InlineKeyboardMarkup:
        """So'rov harakatlari menu"""
        buttons = [
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"request_approve_{request_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"request_reject_{request_id}")
            ],
            [
                InlineKeyboardButton(text="👁 Ko'rish", callback_data=f"request_view_{request_id}"),
                InlineKeyboardButton(text="💬 Izoh", callback_data=f"request_comment_{request_id}")
            ],
            [
                InlineKeyboardButton(text=BACK_TEXT, callback_data="requests_pending")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def confirm_action(action: str, target_id: str) -> InlineKeyboardMarkup:
        """Harakatni tasdiqlash"""
        buttons = [
            [
                InlineKeyboardButton(text="✅ Ha", callback_data=f"confirm_{action}_{target_id}"),
                InlineKeyboardButton(text="❌ Yo'q", callback_data=f"cancel_{action}_{target_id}")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def pagination_menu(current_page: int, total_pages: int, callback_prefix: str) -> InlineKeyboardMarkup:
        """Sahifalash menu"""
        buttons = []
        
        # Sahifalash tugmalari
        nav_buttons = []
        if current_page > 1:
            nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"{callback_prefix}_page_{current_page-1}"))
        
        nav_buttons.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="noop"))
        
        if current_page < total_pages:
            nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"{callback_prefix}_page_{current_page+1}"))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # Orqaga tugmasi
        buttons.append([InlineKeyboardButton(text=BACK_TEXT, callback_data="admin_back")])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)


class UserKeyboards:
    """Oddiy foydalanuvchilar uchun keyboard'lar"""
    
    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """Asosiy menu"""
        buttons = [
            [KeyboardButton(text="🎵 Audio yuborish")],
            [KeyboardButton(text="📊 Statistikam"), KeyboardButton(text="ℹ️ Yordam")],
            [KeyboardButton(text="⚙️ Sozlamalar"), KeyboardButton(text="📞 Aloqa")]
        ]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    
    @staticmethod
    def request_channel_menu() -> InlineKeyboardMarkup:
        """Kanal so'rovi menu"""
        buttons = [
            [
                InlineKeyboardButton(text="📢 Kanal qo'shish so'rovi", callback_data="request_channel"),
                InlineKeyboardButton(text="📊 So'rovlarim", callback_data="my_requests")
            ],
            [
                InlineKeyboardButton(text="❓ Yordam", callback_data="request_help")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def cancel_menu() -> InlineKeyboardMarkup:
        """Bekor qilish menu"""
        buttons = [
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def user_requests_navigation(current_page: int, has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
        """Foydalanuvchi so'rovlari uchun navigatsiya"""
        buttons = []
        nav_row = []
        if has_prev:
            nav_row.append(
                InlineKeyboardButton(
                    text="⬅️",
                    callback_data=f"my_requests_page_{max(1, current_page - 1)}"
                )
            )
        nav_row.append(
            InlineKeyboardButton(
                text=f"{current_page}",
                callback_data="noop"
            )
        )
        if has_next:
            nav_row.append(
                InlineKeyboardButton(
                    text="➡️",
                    callback_data=f"my_requests_page_{current_page + 1}"
                )
            )
        if nav_row:
            buttons.append(nav_row)

        buttons.append(
            [
                InlineKeyboardButton(text="➕ Yangi so'rov", callback_data="request_channel"),
                InlineKeyboardButton(text="❓ Yordam", callback_data="request_help")
            ]
        )
        buttons.append(
            [InlineKeyboardButton(text="❌ Yopish", callback_data="cancel")]
        )

        return InlineKeyboardMarkup(inline_keyboard=buttons)
