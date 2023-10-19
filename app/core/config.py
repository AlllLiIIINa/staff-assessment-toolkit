from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    APP_TITLE = "Internship_app"
    ALLOWED_HOST = str(os.getenv("ALLOWED_HOST"))
    ALLOWED_PORT = int(os.getenv("ALLOWED_PORT"))
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = os.getenv("DEBUG")
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_DB = os.getenv("POSTGRES_DB")
    DB_PORT = os.getenv("POSTGRES_PORT")
    DB_HOST = os.getenv("POSTGRES_HOST")
    REDIS_HOST = os.getenv("REDIS_HOST")
    # DB_HOST = os.getenv("POSTGRES_HOST_DOCKER")
    # REDIS_HOST = os.getenv("REDIS_HOST_DOCKER")
    DB_URL = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DB}"
    )
    TEST_DB = os.getenv("POSTGRES_TEST_DB")
    TEST_DB_URL = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB}"
    )
    REDIS_PORT = os.getenv("REDIS_PORT")
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"
    ACCESS_TOKEN_EXPIRY_TIME = int(os.getenv("ACCESS_TOKEN_EXPIRY_TIME"))
    REFRESH_TOKEN_EXPIRY_TIME = int(os.getenv("ACCESS_TOKEN_EXPIRY_TIME"))
    ALGORITHM = os.getenv("ALGORITHM")
    ALGORITHM_AUTH0 = os.getenv("ALGORITHM_AUTH0")
    TOKEN = os.getenv("TOKEN")
    AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    API_AUDIENCE = os.getenv("API_AUDIENCE")
