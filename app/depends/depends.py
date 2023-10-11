import logging
from datetime import datetime
from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from jose import jwt
from pydantic_core._pydantic_core import ValidationError
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import Settings
from app.db.db import get_db
from app.db.models import User
from app.services.users import UserService


reusable_oauth = OAuth2PasswordBearer(
    tokenUrl="/user_signin/",
    scheme_name="JWT"
)


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
    user_email: Optional[str] = None
    user_firstname: Optional[str] = None
    user_lastname: Optional[str] = None
    user_birthday: Optional[str] = None
    user_city: Optional[str] = None
    user_phone: Optional[str] = None
    user_links: Optional[str] = None
    user_avatar: Optional[str] = None


async def get_current_user(token: str = Depends(reusable_oauth), session: AsyncSession = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(
            token, Settings.SECRET_KEY, algorithms=[Settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            logging.error(f"Token expired")
            raise HTTPException(status_code=401, detail="Token expired", headers={"WWW-Authenticate": "Bearer"})

    except(jwt.JWTError, ValidationError) as e:
        logging.error(f"Error decoding/validating token: {e}")
        raise HTTPException(status_code=403, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    user_repo = UserService(session)
    user = await user_repo.get_by_email(token_data.sub)

    if not user:
        logging.error(f"Could not find user")
        raise HTTPException(status_code=404, detail="Could not find user")

    return user
