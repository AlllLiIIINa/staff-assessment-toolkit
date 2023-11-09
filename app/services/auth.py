import logging
from datetime import timedelta, datetime
from typing import Union
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import Settings
from app.db.db import get_db
from app.db.models import User
from app.depends.exceptions import ErrorPasswordMatch, ErrorAuthentication, \
    TokenExpired, ErrorRetrievingUser, InvalidCredentials, ErrorUpdateEmail, ErrorDeleteAnotherProfile, \
    ErrorRetrievingToken, ErrorUpdatingUserProfile, ErrorDeletingUserProfile, ErrorRetrievingCurrentUser
from app.schemas.auth import TokenPayload
from app.schemas.user import UserBase
from app.schemas.user import UserUpdate
from app.services.users import UserService
from app.utils.security import create_access_token, Hasher, create_user_in_auth0, oauth2_scheme, \
    decode_and_verify_access_token


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(__class__.__name__)
        self.user_service = UserService(self.session)

    async def user_auth(self, user_email, user_hashed_password) -> Union[User, None]:
        try:
            user = await self.user_service.get_by_email(user_email=user_email)

            if user is None:
                logging.error(f"Error retrieving user with email {user_email}")
                return None

            else:
                if not await Hasher.verify_password(user_hashed_password, user.user_hashed_password):
                    logging.error(
                        f"Error password match. Entered password: {user_hashed_password}, "
                        f"password in the database: {User.user_hashed_password}")
                    raise ErrorPasswordMatch()

                return user

        except Exception as e:
            logging.error(f"Error user authentication: {e}")
            raise ErrorAuthentication(e)

    async def get_user_token(self, form_data: OAuth2PasswordRequestForm):
        try:
            user = await self.user_auth(form_data.username, form_data.password)

            if user is None:
                user_data = UserBase(user_email=form_data.username, user_hashed_password=None)
                user = await self.user_service.create(user_data)
                auth0_user = create_user_in_auth0(form_data.username, form_data.password)

                if auth0_user:
                    access_token_expires = timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRY_TIME)
                    access_token = await create_access_token(
                        data={"sub": form_data.username, "user_id": str(user.user_id)},
                        expires_delta=access_token_expires, algorithm=Settings.ALGORITHM_AUTH0
                    )
                    return access_token
                return {"access_token": user, "token_type": "bearer"}

            else:
                access_token_expires = timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRY_TIME)
                access_token = await create_access_token(
                    data={"sub": form_data.username, "user_id": str(user.user_id)},
                    expires_delta=access_token_expires, algorithm=Settings.ALGORITHM
                )
                return {"access_token": access_token, "token_type": "bearer"}

        except Exception as e:
            logging.error(f"Error getting user token with email {form_data.username}: {e}")
            raise ErrorRetrievingToken(e)

    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)) -> User:
        try:
            user_service = UserService(session)
            payload = await decode_and_verify_access_token(token)
            token_data = TokenPayload(**payload)

            try:
                if datetime.fromtimestamp(token_data.exp) < datetime.now():
                    logging.error("Token expired")
                    raise TokenExpired()

                user_id = token_data.user_id

                if not user_id:
                    logging.error("Invalid user_id in the token")

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
                        raise InvalidCredentials

                except JWTError as e:
                    logging.error(e)
                    raise InvalidCredentials
                user = await user_service.get_by_email(email)

                if user is None and payload['scope'] == 'openid profile email':
                    new_user = await user_service.create(email)
                    return new_user

                if user is None:
                    raise InvalidCredentials

            user = await user_service.get_by_email(token_data.sub)

            if not user:
                logging.error("Could not find user")
                raise ErrorRetrievingUser(e=token_data.user_id)

            return user

        except Exception as e:
            logging.error(f"Error getting current user: {e}")
            raise ErrorRetrievingCurrentUser(e)

    async def update_profile(self, user: User, user_id: str, user_data: UserUpdate):
        try:
            if user.user_id != user_id:
                self.logger.error("User attempted to update another user's profile, which is not allowed.")
                raise ErrorUpdateEmail(status_code=403)

            if user_data.user_email and user_data.user_email != user.user_email:
                self.logger.error("User attempted to update their email, which is not allowed.")
                raise ErrorUpdateEmail(status_code=400)

            return await self.user_service.update(user_id, user_data)

        except Exception as e:
            logging.error(f"Error updating User profile. {e}")
            raise ErrorUpdatingUserProfile(e)

    async def delete_profile(self, user, user_id: str):
        try:
            if user.user_id != user_id:
                self.logger.error("User attempted to delete another user's profile, which is not allowed.")
                raise ErrorDeleteAnotherProfile()

            return await self.user_service.delete(user_id)

        except Exception as e:
            logging.error(f"Error deleting User profile. {e}")
            raise ErrorDeletingUserProfile(e)
