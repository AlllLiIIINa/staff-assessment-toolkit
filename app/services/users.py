import logging
import bcrypt
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.schemas.user import UserBase, UserUpdate


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
        try:
            result = await self.session.execute(select(User).filter(User.user_id == user_id))

            if not result:
                logging.error(f"Error retrieving user with ID {user_id}")
                return None

            logging.info("Getting user processed successfu lly")
            return result.scalars().first()

        except Exception as e:
            logging.error(f"Error retrieving user with ID {user_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving user with ID {user_id}: {e} ")

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
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(user_data.user_hashed_password.encode(), salt).decode('utf-8')
            user_data.user_hashed_password = str(hashed_password)
            new_user = User(**user_data.model_dump())
            self.session.add(new_user)
            await self.session.commit()

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

            logging.info(user_data)
            user_dict = user_data.model_dump()
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
        try:
            user = await self.get_by_id(user_id)
            await self.session.delete(user)
            await self.session.commit()

            logging.info("Deleting user processed successfully")
            return await self.get_by_id(user_id)

        except Exception as e:
            logging.error(f"Error deleting user with ID {user_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error deleting user with ID {user_id}: {e}")
