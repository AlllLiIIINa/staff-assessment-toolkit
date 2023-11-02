import logging
import secrets
import string
import httpx
from datetime import datetime
from typing import Optional, Dict
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from pydantic_core._pydantic_core import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import Settings
from app.db.db import get_db
from app.db.models import User
from app.schemas.auth import TokenPayload
from app.services.users import UserService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user_signin/")


async def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


async def decode_and_verify_access_token(token: str) -> Optional[Dict]:
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

    raise HTTPException(status_code=401, detail="Invalid token")


async def create_user_in_auth0(email, password):
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


async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)) -> User:
    try:
        payload = await decode_and_verify_access_token(token)
        token_data = TokenPayload(**payload)
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            logging.error("Token expired")
            raise HTTPException(status_code=401, detail="Token expired", headers={"WWW-Authenticate": "Bearer"})

        user_id = token_data.user_id
        if not user_id:
            logging.error("Invalid user_id in the token")
            raise HTTPException(status_code=401, detail="Invalid user_id in the token")

    except(jwt.JWTError, ValidationError) as e:
        logging.error(f"Error decoding/validating token: {e}")
        try:
            payload = await decode_and_verify_access_token(token)
            email = None
            if payload['scope'] == 'access_token':
                email = payload["sub"]
            elif payload['scope'] == 'openid profile email':
                email = payload["email"]

            if email is None:
                raise HTTPException(status_code=403, detail="Could not validate credentials",
                                    headers={"WWW-Authenticate": "Bearer"})
        except JWTError as e:
            logging.error(e)
            raise HTTPException(status_code=403, detail="Could not validate credentials",
                                headers={"WWW-Authenticate": "Bearer"})
        user_repo = UserService(session)
        user = await user_repo.get_by_email(email)
        if user is None and payload['scope'] == 'openid profile email':
            new_user = await user_repo.create(email)
            return new_user
        if user is None:
            raise HTTPException(status_code=403, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    user_repo = UserService(session)
    user = await user_repo.get_by_email(token_data.sub)

    if not user:
        logging.error("Could not find user")
        raise HTTPException(status_code=404, detail="Could not find user")
    return user
