from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db import get_db
from app.services.auth import AuthService
from app.services.companies import CompanyService
from app.services.invitations import InvitationService
from app.services.notifications import NotificationService
from app.services.questions import QuestionService
from app.services.quizzes import QuizService
from app.services.results import ResultService
from app.services.users import UserService


async def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session)


async def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(session)


async def get_company_service(session: AsyncSession = Depends(get_db)) -> CompanyService:
    return CompanyService(session)


async def get_invitation_service(session: AsyncSession = Depends(get_db)) -> InvitationService:
    return InvitationService(session)


async def get_quiz_service(session: AsyncSession = Depends(get_db)) -> QuizService:
    return QuizService(session)


async def get_question_service(session: AsyncSession = Depends(get_db)) -> QuestionService:
    return QuestionService(session)


async def get_result_service(session: AsyncSession = Depends(get_db)) -> ResultService:
    return ResultService(session)


async def get_notification_service(session: AsyncSession = Depends(get_db)) -> NotificationService:
    return NotificationService(session)
