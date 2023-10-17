import logging
from typing import Union
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import Settings
from app.db.models import User
from app.schemas.user import UserBase
from app.services.users import UserService
from app.utils.security import create_access_token, Hasher
from fastapi import HTTPException
from app.depends.depends import create_user_in_auth0


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def user_auth(self, user_email, user_hashed_password) -> Union[User, None]:
        user_repo = UserService(self.session)
        user = await user_repo.get_by_email(user_email=user_email)
        if user is None:
            logging.error(f"Error retrieving user with email {user_email}")
            return None
        else:
            if not await Hasher.verify_password(user_hashed_password, user.user_hashed_password):
                logging.error(
                    f"Error password match. Entered password: {user_hashed_password}, password in the database: {User.user_hashed_password}")
                raise HTTPException(
                    status_code=404,
                    detail=f"Error password match. Entered password: {user_hashed_password}, password in the database: {User.user_hashed_password}"
                )
            return user

    async def get_user_token(self, form_data: OAuth2PasswordRequestForm):
        user = await self.user_auth(form_data.username, form_data.password)
        if user is None:
            user_repo = UserService(self.session)
            user_data = UserBase(user_email=form_data.username, user_hashed_password=None)
            user = await user_repo.create(user_data)
            auth0_user = create_user_in_auth0(form_data.username, form_data.password)
            if auth0_user:
                access_token_expires = timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRY_TIME)
                access_token = await create_access_token(
                    data={"sub": form_data.username, "password": form_data.password},
                    expires_delta=access_token_expires, algorithm="RS256"
                )
                return access_token
            return {"access_token": user, "token_type": "bearer"}
        else:
            access_token_expires = timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRY_TIME)
            access_token = await create_access_token(
                data={"sub": form_data.username, "password": form_data.password},
                expires_delta=access_token_expires, algorithm="HS256"
            )
            return {"access_token": access_token, "token_type": "bearer"}
