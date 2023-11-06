from http import HTTPStatus
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.companies import CompanyService
from ..db.db import get_db
from ..db.models import User
from ..depends.depends import get_current_user
from ..schemas.company import CompanyUpdate, CompanyBase, CompanyInvitationCreate
from ..services.invitations import InvitationService

company_router = APIRouter(prefix="/companies", tags=["companies"])


@company_router.get("/", operation_id="companies", )
async def company_list(
        page: int = Query(default=1, description="Page number", ge=1),
        companies_per_page: int = Query(default=10, description="Items per page", le=100),
        session: AsyncSession = Depends(get_db)):
    company_repo = CompanyService(session)
    return await company_repo.get_all(page, companies_per_page)


@company_router.post("/", status_code=HTTPStatus.CREATED, operation_id="company_create")
async def company_create(company_data: CompanyBase, user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_db)):
    company_repo = CompanyService(session)
    return await company_repo.create(company_data, user.user_id)


@company_router.get("/{company_id}", operation_id="company_get_by_id")
async def company_get_by_id(company_id: str, user: User = Depends(get_current_user),
                            session: AsyncSession = Depends(get_db)):
    company_repo = CompanyService(session)
    return await company_repo.get_by_id(company_id, user.user_id)


@company_router.put("/{company_id}", operation_id="company_update")
async def company_update(company_id: str, company_data: CompanyUpdate, user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_db)):
    company_repo = CompanyService(session)
    return await company_repo.update(company_id, company_data, user.user_id)


@company_router.delete("/{company_id}", status_code=HTTPStatus.NO_CONTENT, operation_id="company_delete")
async def company_delete(company_id: str, user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_db)):
    company_repo = CompanyService(session)
    return await company_repo.delete(company_id, user.user_id)


@company_router.get("/{company_id}/members", operation_id="get_company_members")
async def get_company_members(company_id: str, page: int = Query(default=1, description="Page number", ge=1),
                              members_per_page: int = Query(default=10, description="Items per page", le=100),
                              session: AsyncSession = Depends(get_db)):
    company_repo = CompanyService(session)
    return await company_repo.get_company_members(company_id, page, members_per_page)


@company_router.post("/{company_id}/{member_id}", operation_id="remove_member")
async def remove_member(company_id: str, member_id: str, user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_db)):
    company_repo = CompanyService(session)
    return await company_repo.remove_member(company_id, user.user_id, member_id)


@company_router.post("/{company_id}/leave", operation_id="leave_company")
async def leave_company(company_id: str, user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_db)):
    company_repo = CompanyService(session)
    return await company_repo.leave_company(company_id, user.user_id)


@company_router.post("/invitation", operation_id="create_invitation")
async def create_invitation(invitation_data: CompanyInvitationCreate, user: User = Depends(get_current_user),
                            session: AsyncSession = Depends(get_db)):
    invitation_repo = InvitationService(session)
    return await invitation_repo.create(user.user_id, invitation_data)


@company_router.get("/user_requests/", operation_id="get_user_requests")
async def user_requests(user: User = Depends(get_current_user),
                            page: int = Query(default=1, description="Page number", ge=1),
                            invitation_per_page: int = Query(default=10, description="Items per page", le=100),
                            session: AsyncSession = Depends(get_db)):
    invitation_repo = InvitationService(session)
    return await invitation_repo.user_requests(user.user_id, page, invitation_per_page)


@company_router.get("/user_invitations/", operation_id="get_user_invitations")
async def user_invitations(user: User = Depends(get_current_user),
                                  page: int = Query(default=1, description="Page number", ge=1),
                                  invitation_per_page: int = Query(default=10, description="Items per page", le=100),
                                  session: AsyncSession = Depends(get_db)):
    invitation_repo = InvitationService(session)
    return await invitation_repo.user_invitations(user.user_id, page, invitation_per_page)


@company_router.post("/{invitation_id}", operation_id="manage_invitation")
async def manage_invitation(invitation_id: str, action: str, user: User = Depends(get_current_user),
                            session: AsyncSession = Depends(get_db)):
    invitation_repo = InvitationService(session)
    return await invitation_repo.handle(user.user_id, invitation_id, action)


@company_router.get("/invited_users/{company_id}", operation_id="get_invited_users")
async def invited_users(company_id: str, user: User = Depends(get_current_user),
                            page: int = Query(default=1, description="Page number", ge=1),
                            invitation_per_page: int = Query(default=10, description="Items per page", le=100),
                            session: AsyncSession = Depends(get_db)):
    invitation_repo = InvitationService(session)
    return await invitation_repo.invited_users(company_id, user.user_id, page, invitation_per_page)


@company_router.get("/membership_requests/{company_id}", operation_id="get_membership_requests")
async def membership_requests(company_id: str, user: User = Depends(get_current_user),
                                  page: int = Query(default=1, description="Page number", ge=1),
                                  invitation_per_page: int = Query(default=10, description="Items per page", le=100),
                                  session: AsyncSession = Depends(get_db)):
    invitation_repo = InvitationService(session)
    return await invitation_repo.membership_requests(company_id, user.user_id, page, invitation_per_page)
