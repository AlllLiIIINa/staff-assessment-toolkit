import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean, UUID, ForeignKey
from sqlalchemy.orm import relationship
from app.db.db import Base


class CompanyMembers(Base):
    __tablename__ = "company_members"

    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True)
    is_admin = Column(Boolean, default=False, nullable=False)


class CompanyInvitations(Base):
    __tablename__ = "company_invitations"

    invitation_id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    recipient_id = Column(UUID(as_uuid=True), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id"), nullable=False)
    invitation_created_at = Column(DateTime, index=True, default=datetime.utcnow, nullable=False)
    invitation_updated_at = Column(DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow,
                                   nullable=False)


class User(Base):
    __tablename__: str = "users"
    __bind_key__ = "internship_db"

    user_id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid4)
    user_email = Column(String, unique=True, index=True, nullable=False)
    user_firstname = Column(String, default=None)
    user_lastname = Column(String, default=None)
    user_birthday = Column(DateTime, default=None)
    user_status = Column(Boolean, default=True)
    user_city = Column(String, default=None)
    user_phone = Column(String, default=None)
    user_links = Column(String, default=None)
    user_avatar = Column(String, default=None)
    user_hashed_password = Column(String, default=None)
    user_is_superuser = Column(Boolean, default=False, nullable=False)
    user_created_at = Column(DateTime, index=True, default=datetime.utcnow, nullable=False)
    user_updated_at = Column(DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    companies = relationship("Company", back_populates="owner")
    member = relationship("Company", secondary="company_members", back_populates="members")
    sent_invitations = relationship("Company", secondary="company_invitations", back_populates="invitations")

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"user_id={self.user_id}, "
            f"user_email={self.user_email}, "
            f"user_firstname={self.user_firstname}, "
            f"user_lastname={self.user_lastname}, "
            f")>"
        )


class Company(Base):
    __tablename__: str = "companies"
    __bind_key__ = "internship_db"

    company_id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid4)
    company_name = Column(String, default=None, unique=True)
    company_title = Column(String, default=None)
    company_description = Column(String, default=None)
    company_city = Column(String, default=None)
    company_phone = Column(String, default=None)
    company_links = Column(String, default=None)
    company_avatar = Column(String, default=None)
    company_is_visible = Column(Boolean, default=False, nullable=False)
    company_created_at = Column(DateTime, index=True, default=datetime.utcnow, nullable=False)
    company_updated_at = Column(DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    owner = relationship("User", back_populates="companies")
    members = relationship("User", secondary="company_members", back_populates="member")
    invitations = relationship("User", secondary="company_invitations", back_populates="sent_invitations")

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"company_id={self.company_id}, "
            f"company_name={self.company_name}, "
            f"company_title={self.company_title}, "
            f"company_description={self.company_description}, "
            f"company_is_visible={self.company_is_visible}, "
            f")>"
        )
