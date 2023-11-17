from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.db.models import User
from app.depends.depends import get_auth_service
from app.schemas.auth import SignIn, UserOut
from app.schemas.user import UserUpdate
from app.services.auth import AuthService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/signin/", response_model=SignIn)
async def user_signin(form_data: OAuth2PasswordRequestForm = Depends(),
                      auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.get_user_token(form_data)


@auth_router.get('/me', response_model=UserOut, operation_id="me")
async def get_me(user: User = Depends(AuthService.get_current_user)):
    return user


@auth_router.delete('/', operation_id="delete_profile")
async def delete_user_profile(user: User = Depends(AuthService.get_current_user),
                              auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.delete_profile(user, user.user_id)


@auth_router.put("/", operation_id="update_profile")
async def update_user_profile(user_data: UserUpdate,
                              current_user: User = Depends(AuthService.get_current_user),
                              auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.update_profile(current_user, current_user.user_id, user_data)
