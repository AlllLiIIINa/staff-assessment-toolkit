import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String, Boolean, UUID, ForeignKey, Integer, ARRAY
from sqlalchemy.orm import relationship
from app.db.db import Base


class CompanyMembers(Base):
    __tablename__: str = "company_members"

    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True)
    is_admin = Column(Boolean, default=False, nullable=False)


class CompanyInvitations(Base):
    __tablename__: str = "company_invitations"

    invitation_id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    recipient_id = Column(UUID(as_uuid=True), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id"), nullable=False)
    invitation_created_at = Column(DateTime, index=True, default=datetime.utcnow, nullable=False)
    invitation_updated_at = Column(DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow,
                                   nullable=False)


class User(Base):
    __tablename__: str = "users"

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
    results = relationship("Result", back_populates="result_user")

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
    quiz = relationship("Quiz", back_populates="company")
    results = relationship("Result", back_populates="result_company")

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


class Quiz(Base):
    __tablename__: str = "quizzes"

    quiz_id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid4)
    quiz_name = Column(String, default=None)
    quiz_title = Column(String, default=None)
    quiz_description = Column(String, default=None)
    quiz_frequency = Column(DateTime, default=None)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.company_id'))
    company = relationship("Company", back_populates="quiz")
    question = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    quiz_created_by = Column(UUID(as_uuid=True), default=uuid.uuid4)
    quiz_updated_by = Column(UUID(as_uuid=True), default=None)
    quiz_created_at = Column(DateTime, index=True, default=datetime.utcnow, nullable=False)
    quiz_updated_at = Column(DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    results = relationship("Result", back_populates="result_quiz")

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"quiz_id={self.quiz_id}, "
            f"quiz_name={self.quiz_name}, "
            f"quiz_title={self.quiz_title}, "
            f"quiz_description={self.quiz_description}, "
            f"quiz_frequency={self.quiz_frequency}, "
            f")>"
        )


class Question(Base):
    __tablename__: str = "questions"

    question_id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid4)
    question_text = Column(String, default=None)
    question_answers = Column(ARRAY(String), default=None)
    question_correct_answer = Column(ARRAY(String), default=None)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey('quizzes.quiz_id'))
    quiz = relationship("Quiz", back_populates="question")
    question_company_id = Column(UUID(as_uuid=True), ForeignKey('companies.company_id'))
    question_created_by = Column(UUID(as_uuid=True), default=uuid.uuid4)
    question_updated_by = Column(UUID(as_uuid=True), default=None)
    question_created_at = Column(DateTime, index=True, default=datetime.utcnow, nullable=False)
    question_updated_at = Column(DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"question_id={self.question_id}, "
            f"question_text={self.question_text}, "
            f"question_answers={self.question_answers}, "
            f"question_correct_answer={self.question_correct_answer}, "
            f")>"
        )


class Result(Base):
    __tablename__: str = "results"

    result_id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid4)
    result_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), default=uuid.uuid4)
    result_user = relationship("User", back_populates="results")
    result_company_id = Column(UUID(as_uuid=True), ForeignKey('companies.company_id'), default=uuid.uuid4)
    result_company = relationship("Company", back_populates="results")
    result_quiz_id = Column(UUID(as_uuid=True), ForeignKey('quizzes.quiz_id'), default=uuid.uuid4)
    result_quiz = relationship("Quiz", back_populates="results")
    result_created_at = Column(DateTime, index=True, default=datetime.utcnow, nullable=False)
    result_right_count = Column(Integer, default=0)
    result_total_count = Column(Integer, default=0)
