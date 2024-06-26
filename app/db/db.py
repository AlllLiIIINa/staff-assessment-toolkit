from redis import asyncio
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import Settings


async def get_redis() -> Redis:
    return await asyncio.from_url(Settings.REDIS_URL)


engine = create_async_engine(Settings.DB_URL, echo=True, future=True)
Base = declarative_base()


async def get_db() -> AsyncSession:
    async with AsyncSession(engine) as session:
        return session
