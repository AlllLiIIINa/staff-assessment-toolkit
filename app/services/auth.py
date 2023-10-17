import logging
from typing import Optional
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Union
from app.core.config import Settings
from app.db.db import get_db
from app.db.models import User
from app.depends.depends import get_current_user, create_user_in_auth0
from app.services.users import UserService
from app.utils.security import create_access_token, Hasher
from pydantic import BaseModel, Field, EmailStr, FilePath, HttpUrl, ConfigDict

auth_router = APIRouter()


async def user_auth(user_email, user_hashed_password, session: AsyncSession) -> Union[User, None]:
    user_repo = UserService(session)
    user = await user_repo.get_by_email(user_email=user_email)
    if user is None:
        logging.error(f"Error retrieving user with email {user_email}")
        user = await user_repo.create(user_email)
        return user
    else:
        if not await Hasher.verify_password(user_hashed_password, user.user_hashed_password):
            logging.error(
                f"Error password match. Entered password: {user_hashed_password}, password in the database: {User.user_hashed_password}")
            raise HTTPException(
                status_code=404,
                detail=f"Error password match. Entered password: {user_hashed_password}, password in the database: {User.user_hashed_password}"
            )
        return user


class SignIn(BaseModel):
    access_token: str
    token_type: str


class SignUp(BaseModel):
    user_firstname: str = Field(None, title="First name")
    user_lastname: str = Field(None, title="Last name")
    user_email: EmailStr = Field(None, title="Email address")
    user_hashed_password: str = Field(None, title="Password", min_length=6)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "user_email": "user@gmail.com",
                "user_hashed_password": "PassWord123",
                "user_firstname": "David",
                "user_lastname": "White",
            }
        }
    )


class UserOut(BaseModel):
    user_email: Optional[EmailStr] = None
    user_firstname: Optional[str] = None
    user_lastname: Optional[str] = None
    user_birthday: Optional[str] = None
    user_city: Optional[str] = None
    user_phone: Optional[str] = None
    user_links: Optional[HttpUrl] = None
    user_avatar: Optional[FilePath] = None


@auth_router.post("/user_signin/", response_model=SignIn)
async def user_signin(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_db)):
    user = await user_auth(form_data.username, form_data.password, session)
    if isinstance(user, str):
        user_repo = UserService(session)
        user = await user_repo.create(user_email=form_data.username)
        auth0_user = create_user_in_auth0(form_data.username, form_data.password)
        if auth0_user:
            access_token_expires = timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRY_TIME)
            access_token = await create_access_token(
                data={"sub": form_data.username, "password": form_data.password},
                expires_delta=access_token_expires,
            )
            return access_token
        return {"access_token": user, "token_type": "bearer"}
    else:
        access_token_expires = timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRY_TIME)
        access_token = await create_access_token(
            data={"sub": form_data.username, "password": form_data.password},
            expires_delta=access_token_expires,
        )
        return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get('/me', response_model=UserOut, operation_id="me")
async def get_me(user: User = Depends(get_current_user)):
    return user
