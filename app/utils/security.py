import logging
import bcrypt
import httpx
from datetime import timedelta, datetime
from typing import Optional, Dict
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt
from app.core.config import Settings
from app.depends.exceptions import ErrorCreatingAccessToken, ErrorCreatingRefreshToken, InvalidToken, \
    ErrorCreatingUserAuth0

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin/")


class Hasher:
    @staticmethod
    async def verify_password(user_plain_password: str, user_hashed_password: str) -> bool:
        return password_context.verify(user_plain_password, user_hashed_password)

    @staticmethod
    async def get_password_hash(user_plain_password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(user_plain_password.encode(), salt)
        return hashed_password.decode('utf-8')


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, algorithm: str = "HS256"):
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=Settings.ACCESS_TOKEN_EXPIRY_TIME
            )
        to_encode.update({"exp": expire})
        if algorithm == "HS256":
            encoded_jwt = jwt.encode(
                to_encode, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM
            )
        elif algorithm == "RS256":
            encoded_jwt = jwt.encode(to_encode, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM_AUTH0)
        else:
            raise ValueError("Unsupported algorithm")

        return encoded_jwt

    except Exception as e:
        logging.error(f"Error creating access token: {e}")
        raise ErrorCreatingAccessToken(e)


async def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    try:
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

    except Exception as e:
        logging.error(f"Error creating refresh token: {e}")
        raise ErrorCreatingRefreshToken(e)


async def decode_and_verify_access_token(token: str) -> Optional[Dict]:
    try:
        try:
            auth0_decoded = jwt.decode(
                token,
                Settings.SECRET_KEY,
                algorithms=[Settings.ALGORITHM_AUTH0],
                audience=Settings.API_AUDIENCE,
            )
            return auth0_decoded
        except jwt.JWTError:
            pass

        try:
            app_decoded = jwt.decode(
                token,
                Settings.SECRET_KEY,
                algorithms=[Settings.ALGORITHM]
            )
            return app_decoded
        except jwt.JWTError:
            pass

    except Exception as e:
        logging.error(f"Invalid token: {e}")
        raise InvalidToken(e)


async def create_user_in_auth0(email, password):
    try:
        url = f"https://{Settings.AUTH0_DOMAIN}/dbconnections/signup"

        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "client_id": Settings.CLIENT_ID,
            "email": email,
            "password": password,
            "connection": "Username-Password-Authentication"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, auth=(Settings.CLIENT_ID, Settings.CLIENT_SECRET))

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to create user in Auth0. Status code: {response.status_code}")
                return None

    except Exception as e:
        logging.error(f"Error creating user in auth0: {e}")
        raise ErrorCreatingUserAuth0(e)
