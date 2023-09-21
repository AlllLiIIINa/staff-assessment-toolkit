import asyncio
import asyncio_redis

import sqlalchemy
from databases import Database
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_utils import database_exists, create_database


from app.core.config import settings


@asyncio.coroutine
def connect():
    connection = yield from asyncio_redis.Connection.create(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT
    )
    yield from connection.set('key', 'value')
    connection.close()


db = Database(settings.DB_URL)
metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(settings.DB_URL, pool_size=3, max_overflow=0)
if not database_exists(engine.url):
    create_database(engine.url)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

metadata.create_all(engine)
