from dotenv import load_dotenv
import os


load_dotenv()


class Settings:
    APP_TITLE = "Internship_app"
    ALLOWED_HOST = os.getenv("ALLOWED_HOST")
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = os.getenv("DEBUG")
    ALLOWED_PORT = os.getenv("PORT")
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_DB = os.getenv("POSTGRES_DB")
    DB_PORT = os.getenv("POSTGRES_PORT")
    DB_HOST = os.getenv("POSTGRES_HOST")
    DB_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DB}"
    )
    TEST_DB = os.getenv("POSTGRES_TEST_DB")
    TEST_DB_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB}"
    )
    ACCESS_TOKEN_EXPIRY_TIME = 60 * 30
    REFRESH_TOKEN_EXPIRY_TIME = 60 * 24 * 365
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")


settings = Settings()
