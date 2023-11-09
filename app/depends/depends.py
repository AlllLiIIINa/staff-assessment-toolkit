from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db import get_db
from app.services.auth import AuthService
from app.services.companies import CompanyService
from app.services.invitations import InvitationService
from app.services.users import UserService


async def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session)


async def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(session)


async def get_company_service(session: AsyncSession = Depends(get_db)) -> CompanyService:
    return CompanyService(session)


async def get_invitation_service(session: AsyncSession = Depends(get_db)) -> InvitationService:
    return InvitationService(session)
