import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Boolean, select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.db.db import Base


class User(Base):
    __tablename__: str = "users"
    __bind_key__ = "internship_db"

    user_id = Column(String, primary_key=True, index=True, default=uuid.uuid4())
    user_email = Column(String, unique=True, index=True, nullable=False)
    user_firstname = Column(String, nullable=False)
    user_lastname = Column(String, nullable=False)
    user_birthday = Column(DateTime)
    user_status = Column(Boolean, default=True)
    user_city = Column(String)
    user_phone = Column(String)
    user_links = Column(String)
    user_avatar = Column(String)
    user_hashed_password = Column(String, nullable=False)
    user_is_superuser = Column(Boolean, default=False, nullable=False)
    user_created_at = Column(DateTime, index=True, default=datetime.utcnow, nullable=False)
    user_updated_at = Column(DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("/
            f"user_id={self.user_id}, "
            f"user_email={self.user_email}, "
            f"user_firstname={self.user_firstname}, "
            f"user_lastname={self.user_lastname}, "
            f")>"
        )


class CRUD:

    async def get_all(async_session: async_sessionmaker[AsyncSession]):
        async with async_session() as session:
            statement = select(User).order_by(User.user_id)

            result = await session.execute(statement)

            return result.scalars()

    async def sign_up(async_session: async_sessionmaker[AsyncSession], user: User):
        async with async_session() as session:
            session.add(user)
            await session.commit()

        return user

    async def sign_in(async_session: async_sessionmaker[AsyncSession], user_id: str):
        async with async_session() as session:
            statement = select(User).filter(User.user_id == user_id)

            result = await session.execute(statement)

            return result.scalars().one()

    async def update(async_session: async_sessionmaker[AsyncSession], user_id, data):
        async with async_session() as session:
            statement = select(User).filter(User.user_id == user_id)
            result = await session.execute(statement)
            user = result.scalars().one()

            user.user_firstname = data['firstname']
            user.user_lastname = data['lastname']

            await session.commit()

            return user

    @staticmethod
    async def delete(async_session: async_sessionmaker[AsyncSession], user: User):
        async with async_session() as session:
            await session.delete(user)
            await session.commit()

        return {}

    # async def set_password_async(self, password):
    #     salt = await asyncio.to_thread(bcrypt.gensalt)
    #     hashed_password = await asyncio.to_thread(bcrypt.hashpw, password.encode('utf-8'), salt)
    #     self.hashed_password = hashed_password
    #
    # async def check_password_async(self, password):
    #     return await asyncio.to_thread(
    #         bcrypt.checkpw,
    #         password.encode('utf-8'),
    #         self.password_hash.encode('utf-8')
    #     )
