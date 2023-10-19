import logging
from typing import Union
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import Settings
from app.db.models import User
from app.schemas.user import UserBase, UserUpdate
from app.services.users import UserService
from app.utils.security import create_access_token, Hasher
from fastapi import HTTPException, Depends
from app.depends.depends import create_user_in_auth0, get_current_user


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
                    data={"sub": form_data.username, "user_id": str(user.user_id)},
                    expires_delta=access_token_expires, algorithm="RS256"
                )
                return access_token
            return {"access_token": user, "token_type": "bearer"}
        else:
            access_token_expires = timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRY_TIME)
            access_token = await create_access_token(
                data={"sub": form_data.username, "user_id": str(user.user_id)},
                expires_delta=access_token_expires, algorithm="HS256"
            )
            return {"access_token": access_token, "token_type": "bearer"}


class ValidationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(__class__.__name__)

    async def update_user(
            self,
            user: User,
            user_id: str,
            user_data: UserUpdate
    ):
        user_service = UserService(self.session)

        if user.user_id != user_id:
            self.logger.error("User attempted to update another user's profile, which is not allowed.")
            raise HTTPException(status_code=403, detail="You cannot update another user's profile")

        if user_data.user_email and user_data.user_email != user.user_email:
            self.logger.error("User attempted to update their email, which is not allowed.")
            raise HTTPException(status_code=400, detail="You cannot update your email")

        if user_data.user_hashed_password:
            user_data.user_hashed_password = await Hasher.get_password_hash(user_data.user_hashed_password)
            user.user_hashed_password = user_data.user_hashed_password

        if user_data.user_firstname is not None:
            user.user_firstname = user_data.user_firstname

        return await user_service.update(user_id, user_data)

    async def delete_user(self, current_user: User, user_id: str):
        user_repo = UserService(self.session)

        if current_user.user_id != user_id:
            self.logger.error("User attempted to delete another user's profile, which is not allowed.")
            raise HTTPException(status_code=403, detail="You cannot delete another user's profile")

        return await user_repo.delete(user_id)
