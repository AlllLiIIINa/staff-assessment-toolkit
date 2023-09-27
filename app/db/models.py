from datetime import datetime
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy import delete as sqlalchemy_delete

from app.db.db import db
from app.db.db import Base

from uuid import uuid4


class User(Base):
    __tablename__: str = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, unique=True, index=True)
    user_firstname = Column(String)
    user_lastname = Column(String)
    birthday = Column(DateTime)
    user_status = Column(Boolean, default=True)
    user_city = Column(String)
    user_phone = Column(String)
    user_links = Column(String)
    user_avatar = Column(String)
    hashed_password = Column(String)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    updated_at = Column(DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"user_id={self.user_id}, "
            f"user_email={self.user_email}, "
            f"user_firstname={self.user_firstname}, "
            f"user_lastname={self.user_lastname}, "
            f")>"
        )

    @classmethod
    async def create(cls, **kwargs):
        user = cls(id=str(uuid4()), **kwargs)
        db.add(user)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        return user

    @classmethod
    async def get(cls, user_id):
        query = select(cls).where(cls.user_id == user_id)
        users = await db.execute(query)
        (user,) = users.first()
        return user

    @classmethod
    async def get_all(cls):
        query = select(cls)
        users = await db.execute(query)
        users = users.scalars().all()
        return users

    @classmethod
    async def update(cls, user_id, **kwargs):
        query = (
            sqlalchemy_update(cls)
            .where(cls.user_id == user_id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(query)

        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

    @classmethod
    async def delete(cls, user_id):
        query = sqlalchemy_delete(cls).where(cls.user_id == user_id)
        await db.execute(query)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        return True
