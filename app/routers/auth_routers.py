from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db import get_db
from app.db.models import User
from app.services.auth import AuthService
from app.depends.depends import get_current_user
from app.schemas.auth import SignIn, UserOut

auth_router = APIRouter()


@auth_router.post("/user_signin/", response_model=SignIn)
async def user_signin(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_db)):
    auth_service = AuthService(session)
    return await auth_service.get_user_token(form_data)


@auth_router.get('/me', response_model=UserOut, operation_id="me")
async def get_me(user: User = Depends(get_current_user)):
    return user
