from http import HTTPStatus
from fastapi import APIRouter, Depends, Query
from app.depends.depends import get_user_service
from app.schemas.user import UserUpdate, UserBase
from app.services.users import UserService

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get("/")
async def user_list(page: int = Query(default=1, description="Page number", ge=1),
                    users_per_page: int = Query(default=10, description="Items per page", le=100),
                    user_service: UserService = Depends(get_user_service)):
    return await user_service.get_all(page, users_per_page)


@user_router.post("/", status_code=HTTPStatus.CREATED, operation_id="user_create")
async def user_create(user_data: UserBase, user_service: UserService = Depends(get_user_service)):
    return await user_service.create(user_data)


@user_router.get("/id/{user_id}", operation_id="user_get_by_id")
async def user_get_by_id(user_id: str, user_service: UserService = Depends(get_user_service)):
    return await user_service.get_by_id(user_id)


@user_router.get("/email/{user_email}", operation_id="user_get_by_email")
async def user_get_by_email(user_email: str, user_service: UserService = Depends(get_user_service)):
    return await user_service.get_by_email(user_email)


@user_router.put("/{user_id}", operation_id="user_update")
async def user_update(user_id: str, user_data: UserUpdate, user_service: UserService = Depends(get_user_service)):
    return await user_service.update(user_id, user_data)


@user_router.delete("/{user_id}", status_code=HTTPStatus.NO_CONTENT, operation_id="user_delete")
async def user_delete(user_id: str, user_service: UserService = Depends(get_user_service)):
    return await user_service.delete(user_id)
