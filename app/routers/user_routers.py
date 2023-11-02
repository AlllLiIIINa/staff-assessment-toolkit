from http import HTTPStatus
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserUpdate, UserBase
from app.services.users import UserService
from ..db.db import get_db

user_router = APIRouter(tags=["users"])


@user_router.get("/")
async def user_list(
        page: int = Query(default=1, description="Page number", ge=1),
        users_per_page: int = Query(default=10, description="Items per page", le=100),
        session: AsyncSession = Depends(get_db)):
    user_repo = UserService(session)
    return await user_repo.get_all(page, users_per_page)


@user_router.post("/user_create", status_code=HTTPStatus.CREATED, operation_id="user_create")
async def user_create(user_data: UserBase, session: AsyncSession = Depends(get_db)):
    user_repo = UserService(session)
    return await user_repo.create(user_data)


@user_router.get("/{user_id}", operation_id="user_get_by_id")
async def user_get_by_id(user_id: str, session: AsyncSession = Depends(get_db)):
    user_repo = UserService(session)
    return await user_repo.get_by_id(user_id)


@user_router.get("/{user_email}", operation_id="user_get_by_email")
async def user_get_by_email(user_email: str, session: AsyncSession = Depends(get_db)):
    user_repo = UserService(session)
    return await user_repo.get_by_email(user_email)


@user_router.put("update/{user_id}", operation_id="user_update")
async def user_update(user_id: str, user_data: UserUpdate, session: AsyncSession = Depends(get_db)):
    user_repo = UserService(session)
    return await user_repo.update(user_id, user_data)


@user_router.put("delete/{user_id}", status_code=HTTPStatus.NO_CONTENT, operation_id="user_delete")
async def user_delete(user_id: str, session: AsyncSession = Depends(get_db)):
    user_repo = UserService(session)
    return await user_repo.delete(user_id)
