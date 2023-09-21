from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aioredis
import redis

import sqlalchemy
from databases import Database
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.config import settings


@asynccontextmanager
async def connect(_application: FastAPI) -> AsyncGenerator:

    pool = aioredis.ConnectionPool.from_url(
        str(settings.REDIS_URL), max_connections=10, decode_responses=True
    )
    redis.redis_client = aioredis.Redis(connection_pool=pool)

    yield

    await pool.disconnect()


database = Database(settings.DB_URL)

metadata = sqlalchemy.MetaData()

Base = declarative_base()

engine = create_engine(settings.DB_URL, echo=True, future=True)

metadata.create_all(engine)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

metadata.create_all(engine)
