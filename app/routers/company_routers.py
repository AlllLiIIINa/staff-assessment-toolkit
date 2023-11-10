from http import HTTPStatus
from fastapi import APIRouter, Depends, Query
from app.db.models import User
from app.depends.depends import get_company_service, get_invitation_service
from app.schemas.company import CompanyUpdate, CompanyBase, CompanyInvitationCreate, CompanyAdmin
from app.services.auth import AuthService
from app.services.companies import CompanyService
from app.services.invitations import InvitationService

company_router = APIRouter(prefix="/companies", tags=["companies"])


@company_router.get("/", operation_id="companies", )
async def company_list(page: int = Query(default=1, description="Page number", ge=1),
                       companies_per_page: int = Query(default=10, description="Items per page", le=100),
                       company_repo: CompanyService = Depends(get_company_service)):
    return await company_repo.get_all(page, companies_per_page)


@company_router.post("/", status_code=HTTPStatus.CREATED, operation_id="company_create")
async def company_create(company_data: CompanyBase, user: User = Depends(AuthService.get_current_user),
                         company_service: CompanyService = Depends(get_company_service)):
    return await company_service.create(company_data, user.user_id)


@company_router.get("/{company_id}", operation_id="company_get_by_id")
async def company_get_by_id(company_id: str, user: User = Depends(AuthService.get_current_user),
                            company_service: CompanyService = Depends(get_company_service)):
    return await company_service.get_by_id(company_id, user.user_id)


@company_router.put("/{company_id}", operation_id="company_update")
async def company_update(company_id: str, company_data: CompanyUpdate, user: User = Depends(AuthService.get_current_user),
                         company_service: CompanyService = Depends(get_company_service)):
    return await company_service.update(company_id, company_data, user.user_id)


@company_router.delete("/{company_id}", status_code=HTTPStatus.NO_CONTENT, operation_id="company_delete")
async def company_delete(company_id: str, user: User = Depends(AuthService.get_current_user),
                         company_service: CompanyService = Depends(get_company_service)):
    return await company_service.delete(company_id, user.user_id)


@company_router.get("/{company_id}/members", operation_id="get_company_members")
async def get_company_members(company_id: str, page: int = Query(default=1, description="Page number", ge=1),
                              members_per_page: int = Query(default=10, description="Items per page", le=100),
                              company_service: CompanyService = Depends(get_company_service)):
    return await company_service.get_company_members(company_id, page, members_per_page)


@company_router.delete("/{company_id}/{member_id}", operation_id="remove_member")
async def remove_member(company_id: str, member_id: str, user: User = Depends(AuthService.get_current_user),
                        company_service: CompanyService = Depends(get_company_service)):
    return await company_service.remove_member(company_id, user.user_id, member_id)


@company_router.post("/{company_id}/leave", operation_id="leave_company")
async def leave_company(company_id: str, user: User = Depends(AuthService.get_current_user),
                        company_service: CompanyService = Depends(get_company_service)):
    return await company_service.leave_company(company_id, user.user_id)


@company_router.post("/invitation", operation_id="create_invitation")
async def create_invitation(invitation_data: CompanyInvitationCreate, user: User = Depends(AuthService.get_current_user),
                            invitation_service: InvitationService = Depends(get_invitation_service)):
    return await invitation_service.create(user.user_id, invitation_data)


@company_router.get("/user_requests/", operation_id="get_user_requests")
async def user_requests(user: User = Depends(AuthService.get_current_user),
                        page: int = Query(default=1, description="Page number", ge=1),
                        invitation_per_page: int = Query(default=10, description="Items per page", le=100),
                        invitation_service: InvitationService = Depends(get_invitation_service)):
    return await invitation_service.user_requests(user.user_id, page, invitation_per_page)


@company_router.get("/{company_id}/invitations", operation_id="get_user_invitations")
async def user_invitations(user: User = Depends(AuthService.get_current_user),
                           page: int = Query(default=1, description="Page number", ge=1),
                           invitation_per_page: int = Query(default=10, description="Items per page", le=100),
                           invitation_service: InvitationService = Depends(get_invitation_service)):
    return await invitation_service.user_invitations(user.user_id, page, invitation_per_page)


@company_router.post("/{invitation_id}", operation_id="manage_invitation")
async def manage_invitation(invitation_id: str, action: str, user: User = Depends(AuthService.get_current_user),
                            invitation_service: InvitationService = Depends(get_invitation_service)):
    return await invitation_service.handle(user.user_id, invitation_id, action)


@company_router.get("{company_id}/invited", operation_id="get_invited_users")
async def invited_users(company_id: str, user: User = Depends(AuthService.get_current_user),
                        page: int = Query(default=1, description="Page number", ge=1),
                        invitation_per_page: int = Query(default=10, description="Items per page", le=100),
                        invitation_service: InvitationService = Depends(get_invitation_service)):
    return await invitation_service.invited_users(company_id, user.user_id, page, invitation_per_page)


@company_router.get("/{company_id}/requests", operation_id="get_membership_requests")
async def membership_requests(company_id: str, user: User = Depends(AuthService.get_current_user),
                              page: int = Query(default=1, description="Page number", ge=1),
                              invitation_per_page: int = Query(default=10, description="Items per page", le=100),
                              invitation_service: InvitationService = Depends(get_invitation_service)):
    return await invitation_service.membership_requests(company_id, user.user_id, page, invitation_per_page)


@company_router.get("/{user_id}/", operation_id="get_user_companies")
async def get_user_companies(user_id: str, company_service: CompanyService = Depends(get_company_service)):
    return await company_service.get_user_companies(user_id)


@company_router.get("/{company_id}/admins", operation_id="get_admins")
async def get_admins(company_id: str,
                     page: int = Query(default=1, description="Page number", ge=1),
                     admin_per_page: int = Query(default=10, description="Items per page", le=100),
                     company_service: CompanyService = Depends(get_company_service)):
    return await company_service.get_admins(company_id, page, admin_per_page)


@company_router.put("/{company_id}/role", operation_id="set_admin_status")
async def set_admin_status(admin_data: CompanyAdmin, user: User = Depends(AuthService.get_current_user),
                           company_service: CompanyService = Depends(get_company_service)):
    return await company_service.set_admin_status(admin_data, user.user_id)
