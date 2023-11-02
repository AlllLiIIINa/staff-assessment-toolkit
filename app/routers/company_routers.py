from http import HTTPStatus
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.companies import CompanyService
from ..db.db import get_db
from ..db.models import User
from ..depends.depends import get_current_user
from ..schemas.company import CompanyUpdate, CompanyBase

company_router = APIRouter(tags=["companies"])


@company_router.get("/", operation_id="companies",)
async def company_list(
        page: int = Query(default=1, description="Page number", ge=1),
        companies_per_page: int = Query(default=10, description="Items per page", le=100),
        session: AsyncSession = Depends(get_db)):
    company_repo = CompanyService(session)
    return await company_repo.get_all(page, companies_per_page)


@company_router.post("/company_create", status_code=HTTPStatus.CREATED, operation_id="company_create")
async def company_create(company_data: CompanyBase, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)):
    company_repo = CompanyService(session)
    return await company_repo.create(company_data, user.user_id)


@company_router.get("/{company_id}", operation_id="company_get_by_id")
async def company_get_by_id(company_id: str, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)):
    company_repo = CompanyService(session)
    return await company_repo.get_by_id(company_id, user.user_id)


@company_router.put("update/{company_id}", operation_id="company_update")
async def company_update(company_id: str, company_data: CompanyUpdate, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)):
    company_repo = CompanyService(session)
    return await company_repo.update(company_id, company_data, user.user_id)


@company_router.put("delete/{company_id}", status_code=HTTPStatus.NO_CONTENT, operation_id="company_delete")
async def company_delete(company_id: str, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)):
    company_repo = CompanyService(session)
    return await company_repo.delete(company_id, user.user_id)
