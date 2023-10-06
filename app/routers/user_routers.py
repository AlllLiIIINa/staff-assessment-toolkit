import logging
from http import HTTPStatus
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from .health import router
from app.schemas.user import UserUpdate, UserBase
from app.services.auth import SignUp, SignIn
from app.services.users import UserService
from ..db.db import get_db


@router.get("/users/")
async def user_list(
        page: int = Query(default=1, description="Page number", ge=1),
        users_per_page: int = Query(default=10, description="Items per page", le=100),
        session: AsyncSession = Depends(get_db)):
    user_repo = UserService(session)
    return await user_repo.get_all(page, users_per_page)


@router.post("/user_create", status_code=HTTPStatus.CREATED, operation_id="user_signup")
async def user_create(user_data: SignUp, session: AsyncSession = Depends(get_db)):
    user_repo = UserService(session)
    user = await user_repo.create(user_data)
    return user


@router.get("/user_get_by_id/{user_id}", response_model=SignIn, operation_id="user_signin")
async def user_get_by_id(user_id: str, session: AsyncSession = Depends(get_db)):
    user_repo = UserService(session)
    user = await user_repo.get_by_id(user_id)
    return user


@router.put("/user_update/{user_id}", response_model=UserBase, operation_id="user_update")
async def user_update(user_id: str, user_data: UserUpdate, session: AsyncSession = Depends(get_db)):
    user_repo = UserService(session)
    user = await user_repo.update(user_id, user_data)
    logging.info("Getting user processed successfully")
    return user


@router.put("/user_delete/{user_id}", status_code=HTTPStatus.NO_CONTENT, operation_id="user_delete")
async def user_delete(user_id: str, session: AsyncSession = Depends(get_db)):
    user_repo = UserService(session)
    user = await user_repo.delete(user_id)
    return user
