import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from app.core.config import settings


@pytest.fixture
def postgres_session():
    engine = create_engine(settings.DB_TEST_URL, pool_size=3, max_overflow=0)
    if not database_exists(engine.url):
        create_database(engine.url)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    yield session
    session.close()


def test_postgresql_connection(postgres_session):
    result = postgres_session.execute(text("SELECT 1"))
    assert result.scalar() == 1
