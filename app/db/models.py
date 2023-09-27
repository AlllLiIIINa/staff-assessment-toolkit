import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean

from app.db.db import Base


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
    created_at = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, index=True, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"id={self.user_id}, "
            f"email={self.user_email}, "
            f"firstname={self.user_firstname}, "
            f"lastname={self.user_lastname}, "
            f")>"
        )
