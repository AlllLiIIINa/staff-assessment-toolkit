import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import Settings
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
async def test_db():
    engine = create_async_engine(Settings.TEST_DB_URL, echo=True, future=True)
    async with AsyncSession(engine) as session:
        yield session
