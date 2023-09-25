from redis import asyncio
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import Settings


async def get_redis_db() -> Redis:
    redis = await asyncio.from_url(Settings.REDIS_URL)
    return redis


async def get_postgresql_db():
    engine = create_async_engine(Settings.DB_URL, echo=True, future=True)
    return engine
