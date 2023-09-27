import datetime
from redis import asyncio
from redis.asyncio import Redis
from sqlalchemy import Column, DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import DeclarativeMeta
from app.core.config import Settings


async def get_redis() -> Redis:
    return await asyncio.from_url(Settings.REDIS_URL)


engine = create_async_engine(Settings.DB_URL, echo=True, future=True)
Base: DeclarativeMeta = declarative_base()


async def get_db() -> AsyncSession:
    async with AsyncSession(engine) as session:
        return session


class User(Base):
    __tablename__: str = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, unique=True, index=True)
    user_firstname = Column(String)
    user_lastname = Column(String)
    birthday = Column(DateTime)
    user_status = Column(Boolean, default=True)
    user_city = Column(String)
    user_phone = Column(String)
    user_links = Column(String)
    user_avatar = Column(String)
    hashed_password = Column(String)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
