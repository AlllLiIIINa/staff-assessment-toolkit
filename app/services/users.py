import logging
import secrets
import string
import bcrypt
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.schemas.user import UserBase, UserUpdate
from app.utils.security import Hasher


class UserService:
    model = User

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, page: int = 1, items_per_page: int = 10):
        try:
            offset = (page - 1) * items_per_page
            query = select(self.model).offset(offset).limit(items_per_page)
            result = await self.session.execute(query)

            logging.info("Getting entity list processed successfully")
            return [UserBase(**user.__dict__) for user in result.scalars().all()]

        except Exception as e:

            logging.error(f"Error retrieving entity list: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving entity list: {e}")

    async def get_by_id(self, user_id: str):
        result = await self.session.execute(select(User).filter(User.user_id == user_id))

        if not result:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        try:
            logging.info("Getting user processed successfully")
            return result.scalars().first()

        except Exception as e:
            logging.error(f"Error retrieving user with ID {user_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving user with ID {user_id}: {e}")

    async def get_by_email(self, user_email: str):
        try:
            result = await self.session.execute(select(User).filter(User.user_email == user_email))

            if not result:
                logging.error(f"Error retrieving user with email {user_email}")
                return None

            logging.info("Getting user processed successfully")
            return result.scalars().first()

        except Exception as e:
            logging.error(f"Error retrieving user with email {user_email}: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving user with email {user_email}: {e} ")

    async def create(self, user_data: UserBase):
        try:
            if not user_data.user_hashed_password:
                password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(8))

            else:
                password = user_data.user_hashed_password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode(), salt).decode('utf-8')
            user_data.user_hashed_password = str(hashed_password)
            new_user = User(**user_data.model_dump())
            self.session.add(new_user)

            try:
                await self.session.commit()

            except Exception as e:
                logging.error(f"Error committing transaction: {str(e)}")
                await self.session.rollback()

            finally:
                await self.session.close()

            logging.info(f"User created: {new_user.user_id}")
            logging.info("Creating user processed successfully")
            return new_user

        except Exception as e:
            logging.error(f"Error creating user: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error creating user: {e}")

    async def update(self, user_id: str, user_data: UserUpdate):
        try:
            user = await self.get_by_id(user_id)

            if not user:
                logging.error(f"Error retrieving user with ID {user_id}")
                return None

            if user_data.user_hashed_password:
                user_data.user_hashed_password = await Hasher.get_password_hash(user_data.user_hashed_password)
                user.user_hashed_password = user_data.user_hashed_password

            logging.info(user_data)
            user_dict = user_data.model_dump(exclude_none=True)
            updated_user_dict = {key: value for key, value in user_dict.items() if value is not None}
            query_user = update(self.model).where(self.model.user_id == user_id).values(updated_user_dict).returning(self.model.user_id)
            await self.session.execute(query_user)
            await self.session.commit()

            logging.info(f"User update successful for user ID: {user_id}")
            return await self.get_by_id(user_id)

        except Exception as e:
            logging.error(f"Error during user update for user ID: {user_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error updating user: {e}")

    async def delete(self, user_id: str):
        user = await self.get_by_id(user_id)

        if user is None:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

        try:
            await self.session.delete(user)
            await self.session.commit()
            logging.info("Deleting user processed successfully")
            return user

        except Exception as e:
            logging.error(f"Error deleting user with ID {user_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error deleting user with ID {user_id}: {e}")
