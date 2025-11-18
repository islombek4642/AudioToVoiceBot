import aiosqlite
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum


class UserStatus(Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    BANNED = "banned"


class ChannelType(Enum):
    CHANNEL = "channel"
    GROUP = "group"
    SUPERGROUP = "supergroup"


class RequestStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_database(self):
        async with aiosqlite.connect(self.db_path) as db:
            await self._create_tables(db)
            await db.commit()

    async def _create_tables(self, db: aiosqlite.Connection):
        # Foydalanuvchilar jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language_code TEXT DEFAULT 'uz',
                status TEXT DEFAULT 'active',
                is_admin BOOLEAN DEFAULT 0,
                registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_conversions INTEGER DEFAULT 0
            )
        ''')

        # Majburiy kanallar jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS force_subscribe_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id BIGINT NOT NULL,
                channel_username TEXT,
                channel_title TEXT,
                channel_type TEXT DEFAULT 'channel',
                is_active BOOLEAN DEFAULT 1,
                added_by BIGINT NOT NULL,
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                invite_link TEXT
            )
        ''')

        # Kanal so'rovlari jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS channel_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id BIGINT NOT NULL,
                channel_username TEXT,
                channel_title TEXT,
                channel_type TEXT DEFAULT 'channel',
                requested_by BIGINT NOT NULL,
                request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                reviewed_by BIGINT,
                review_date DATETIME,
                review_comment TEXT,
                invite_link TEXT
            )
        ''')

        # Audio konversiyalar jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS audio_conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id BIGINT NOT NULL,
                original_filename TEXT,
                file_size BIGINT,
                audio_format TEXT,
                conversion_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                processing_time REAL,
                success BOOLEAN DEFAULT 1,
                error_message TEXT
            )
        ''')

        # Foydalanuvchi faoliyati jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id BIGINT NOT NULL,
                activity_type TEXT NOT NULL,
                activity_data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Bot statistikasi jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS bot_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_date DATE NOT NULL,
                total_users INTEGER DEFAULT 0,
                active_users INTEGER DEFAULT 0,
                new_users INTEGER DEFAULT 0,
                total_conversions INTEGER DEFAULT 0,
                successful_conversions INTEGER DEFAULT 0,
                failed_conversions INTEGER DEFAULT 0
            )
        ''')

        # Rate limiting jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS rate_limits (
                user_id BIGINT PRIMARY KEY,
                message_count INTEGER DEFAULT 0,
                window_start DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Indexlar yaratish
        await db.execute('CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_users_status ON users(status)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_force_channels_active ON force_subscribe_channels(is_active)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_channel_requests_status ON channel_requests(status)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_conversions_user_id ON audio_conversions(user_id)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_conversions_date ON audio_conversions(conversion_date)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_activity_user_id ON user_activity(user_id)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON user_activity(timestamp)')


class UserRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    async def create_user(self, user_data: Dict[str, Any]) -> bool:
        async with aiosqlite.connect(self.db.db_path) as db:
            try:
                await db.execute('''
                    INSERT OR IGNORE INTO users 
                    (user_id, username, first_name, last_name, language_code)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    user_data['user_id'],
                    user_data.get('username'),
                    user_data.get('first_name'),
                    user_data.get('last_name'),
                    user_data.get('language_code', 'uz')
                ))
                await db.commit()
                return True
            except Exception as e:
                print(f"User yaratishda xato: {e}")
                return False

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM users WHERE user_id = ?', (user_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def update_user_activity(self, user_id: int):
        async with aiosqlite.connect(self.db.db_path) as db:
            await db.execute(
                'UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE user_id = ?',
                (user_id,)
            )
            await db.commit()

    async def increment_conversions(self, user_id: int):
        async with aiosqlite.connect(self.db.db_path) as db:
            await db.execute(
                'UPDATE users SET total_conversions = total_conversions + 1 WHERE user_id = ?',
                (user_id,)
            )
            await db.commit()

    async def set_user_status(self, user_id: int, status: UserStatus):
        async with aiosqlite.connect(self.db.db_path) as db:
            await db.execute(
                'UPDATE users SET status = ? WHERE user_id = ?',
                (status.value, user_id)
            )
            await db.commit()

    async def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM users ORDER BY registration_date DESC LIMIT ? OFFSET ?',
                (limit, offset)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_users_by_status(self, status: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM users WHERE status = ? ORDER BY last_activity DESC LIMIT ? OFFSET ?',
                (status, limit, offset)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_admin_users(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM users WHERE is_admin = 1 ORDER BY registration_date DESC LIMIT ? OFFSET ?',
                (limit, offset)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


class ChannelRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    async def add_force_channel(self, channel_data: Dict[str, Any]) -> bool:
        async with aiosqlite.connect(self.db.db_path) as db:
            try:
                await db.execute('''
                    INSERT INTO force_subscribe_channels 
                    (channel_id, channel_username, channel_title, channel_type, added_by, invite_link)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    channel_data['channel_id'],
                    channel_data.get('channel_username'),
                    channel_data.get('channel_title'),
                    channel_data.get('channel_type', 'channel'),
                    channel_data['added_by'],
                    channel_data.get('invite_link')
                ))
                await db.commit()
                return True
            except Exception as e:
                print(f"Kanal qo'shishda xato: {e}")
                return False

    async def get_active_force_channels(self) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM force_subscribe_channels WHERE is_active = 1'
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def deactivate_channel(self, channel_id: int) -> bool:
        async with aiosqlite.connect(self.db.db_path) as db:
            await db.execute(
                'UPDATE force_subscribe_channels SET is_active = 0 WHERE channel_id = ?',
                (channel_id,)
            )
            await db.commit()
            return True

    async def create_channel_request(self, request_data: Dict[str, Any]) -> bool:
        async with aiosqlite.connect(self.db.db_path) as db:
            try:
                await db.execute('''
                    INSERT INTO channel_requests 
                    (channel_id, channel_username, channel_title, channel_type, requested_by, invite_link)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    request_data['channel_id'],
                    request_data.get('channel_username'),
                    request_data.get('channel_title'),
                    request_data.get('channel_type', 'channel'),
                    request_data['requested_by'],
                    request_data.get('invite_link')
                ))
                await db.commit()
                return True
            except Exception as e:
                print(f"So'rov yaratishda xato: {e}")
                return False

    async def get_pending_requests(self) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM channel_requests WHERE status = "pending" ORDER BY request_date ASC'
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_user_requests(self, user_id: int, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                '''
                SELECT * FROM channel_requests
                WHERE requested_by = ?
                ORDER BY request_date DESC
                LIMIT ? OFFSET ?
                ''',
                (user_id, limit, offset)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_request_by_id(self, request_id: int) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM channel_requests WHERE id = ?',
                (request_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_requests_by_status(
        self,
        status: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                '''
                SELECT * FROM channel_requests
                WHERE status = ?
                ORDER BY request_date DESC
                LIMIT ? OFFSET ?
                ''',
                (status, limit, offset)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_request_stats(self) -> Dict[str, int]:
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                '''
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending,
                    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) AS approved,
                    SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) AS rejected
                FROM channel_requests
                '''
            )
            row = await cursor.fetchone()
            if not row:
                return {"total": 0, "pending": 0, "approved": 0, "rejected": 0}
            return dict(row)

    async def approve_request(self, request_id: int, admin_id: int, comment: str = None) -> bool:
        async with aiosqlite.connect(self.db.db_path) as db:
            await db.execute('''
                UPDATE channel_requests 
                SET status = "approved", reviewed_by = ?, review_date = CURRENT_TIMESTAMP, review_comment = ?
                WHERE id = ?
            ''', (admin_id, comment, request_id))
            await db.commit()
            return True

    async def reject_request(self, request_id: int, admin_id: int, comment: str = None) -> bool:
        async with aiosqlite.connect(self.db.db_path) as db:
            await db.execute('''
                UPDATE channel_requests 
                SET status = "rejected", reviewed_by = ?, review_date = CURRENT_TIMESTAMP, review_comment = ?
                WHERE id = ?
            ''', (admin_id, comment, request_id))
            await db.commit()
            return True


class ConversionRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    async def log_conversion(self, conversion_data: Dict[str, Any]) -> bool:
        async with aiosqlite.connect(self.db.db_path) as db:
            try:
                await db.execute('''
                    INSERT INTO audio_conversions 
                    (user_id, original_filename, file_size, audio_format, processing_time, success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    conversion_data['user_id'],
                    conversion_data.get('original_filename'),
                    conversion_data.get('file_size'),
                    conversion_data.get('audio_format'),
                    conversion_data.get('processing_time'),
                    conversion_data.get('success', True),
                    conversion_data.get('error_message')
                ))
                await db.commit()
                return True
            except Exception as e:
                print(f"Konversiya log'da xato: {e}")
                return False

    async def get_user_conversions(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('''
                SELECT * FROM audio_conversions 
                WHERE user_id = ? 
                ORDER BY conversion_date DESC 
                LIMIT ?
            ''', (user_id, limit))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


class StatisticsRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    async def get_user_count(self) -> int:
        async with aiosqlite.connect(self.db.db_path) as db:
            cursor = await db.execute('SELECT COUNT(*) FROM users')
            result = await cursor.fetchone()
            return result[0]

    async def get_active_users_today(self) -> int:
        today = datetime.now().date()
        async with aiosqlite.connect(self.db.db_path) as db:
            cursor = await db.execute('''
                SELECT COUNT(DISTINCT user_id) FROM user_activity 
                WHERE DATE(timestamp) = ?
            ''', (today,))
            result = await cursor.fetchone()
            return result[0]

    async def get_conversions_today(self) -> int:
        today = datetime.now().date()
        async with aiosqlite.connect(self.db.db_path) as db:
            cursor = await db.execute('''
                SELECT COUNT(*) FROM audio_conversions 
                WHERE DATE(conversion_date) = ?
            ''', (today,))
            result = await cursor.fetchone()
            return result[0]

    async def get_popular_formats(self, limit: int = 10) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute('''
                SELECT audio_format, COUNT(*) as count 
                FROM audio_conversions 
                WHERE success = 1 AND audio_format IS NOT NULL
                GROUP BY audio_format 
                ORDER BY count DESC 
                LIMIT ?
            ''', (limit,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def log_activity(self, user_id: int, activity_type: str, activity_data: str = None):
        async with aiosqlite.connect(self.db.db_path) as db:
            await db.execute('''
                INSERT INTO user_activity (user_id, activity_type, activity_data)
                VALUES (?, ?, ?)
            ''', (user_id, activity_type, activity_data))
            await db.commit()


class RateLimitRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    async def check_rate_limit(self, user_id: int, max_messages: int, window_seconds: int) -> bool:
        async with aiosqlite.connect(self.db.db_path) as db:
            now = datetime.now()
            window_start = now - timedelta(seconds=window_seconds)
            
            # Eski window ma'lumotlarini tozalash
            await db.execute(
                'DELETE FROM rate_limits WHERE window_start < ?',
                (window_start,)
            )
            
            # Foydalanuvchining hozirgi window'dagi xabar sonini tekshirish
            cursor = await db.execute(
                'SELECT message_count FROM rate_limits WHERE user_id = ?',
                (user_id,)
            )
            result = await cursor.fetchone()
            
            if result is None:
                # Yangi entry yaratish
                await db.execute(
                    'INSERT INTO rate_limits (user_id, message_count) VALUES (?, 1)',
                    (user_id,)
                )
                await db.commit()
                return True
            
            message_count = result[0]
            if message_count >= max_messages:
                return False
            
            # Message count ni oshirish
            await db.execute(
                'UPDATE rate_limits SET message_count = message_count + 1 WHERE user_id = ?',
                (user_id,)
            )
            await db.commit()
            return True
