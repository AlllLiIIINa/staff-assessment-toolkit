import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean, UUID
from app.db.db import Base


class User(Base):
    __tablename__: str = "users"
    __bind_key__ = "internship_db"

    user_id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid4)
    user_email = Column(String, unique=True, index=True, nullable=False)
    user_firstname = Column(String, nullable=False)
    user_lastname = Column(String, nullable=False)
    user_birthday = Column(DateTime, default=None)
    user_status = Column(Boolean, default=True)
    user_city = Column(String, default=None)
    user_phone = Column(String, default=None)
    user_links = Column(String, default=None)
    user_avatar = Column(String, default=None)
    user_hashed_password = Column(String, nullable=False)
    user_is_superuser = Column(Boolean, default=False, nullable=False)
    user_created_at = Column(DateTime, index=True, default=datetime.utcnow, nullable=False)
    user_updated_at = Column(DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"user_id={self.user_id}, "
            f"user_email={self.user_email}, "
            f"user_firstname={self.user_firstname}, "
            f"user_lastname={self.user_lastname}, "
            f")>"
        )
