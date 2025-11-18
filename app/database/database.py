import os
from typing import Optional
from app.database.models import (
    DatabaseManager,
    UserRepository,
    ChannelRepository,
    ConversionRepository,
    StatisticsRepository,
    RateLimitRepository
)


class Database:
    def __init__(self, db_path: str):
        # Ma'lumotlar bazasi katalogini yaratish
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.manager = DatabaseManager(db_path)
        self.users = UserRepository(self.manager)
        self.channels = ChannelRepository(self.manager)
        self.conversions = ConversionRepository(self.manager)
        self.statistics = StatisticsRepository(self.manager)
        self.rate_limits = RateLimitRepository(self.manager)

    async def init(self):
        await self.manager.init_database()

    async def close(self):
        pass


# Global database instance
db: Optional[Database] = None


async def init_database(db_path: str) -> Database:
    global db
    db = Database(db_path)
    await db.init()
    return db


def get_database() -> Database:
    if db is None:
        raise RuntimeError("Database not initialized")
    return db
