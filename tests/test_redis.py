import pytest
import asyncio_redis
from app.core.config import settings
from asyncio_redis.connection import Connection


@pytest.fixture
async def redis_connection() -> Connection:
    connection = await asyncio_redis.Connection.create(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT
    )
    yield connection
    await connection.close()


@pytest.fixture
async def test_redis(redis_connection: Connection):
    await redis_connection.set('key', 'value')
    result = await redis_connection.get('key')
    assert result == 'value'
