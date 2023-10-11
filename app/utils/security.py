import bcrypt
from datetime import timedelta, datetime
from typing import Optional
from passlib.context import CryptContext
from jose import jwt
from app.core.config import Settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    @staticmethod
    async def verify_password(user_plain_password: str, user_hashed_password: str) -> bool:
        return password_context.verify(user_plain_password, user_hashed_password)

    @staticmethod
    async def get_password_hash(user_plain_password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(user_plain_password.encode(), salt)
        return hashed_password.decode('utf-8')


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=Settings.ACCESS_TOKEN_EXPIRY_TIME
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM
    )
    return encoded_jwt


async def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=Settings.REFRESH_TOKEN_EXPIRY_TIME
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM
    )
    return encoded_jwt
