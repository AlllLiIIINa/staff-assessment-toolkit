from typing import Optional
from pydantic import EmailStr, Field, ConfigDict, BaseModel
from app.schemas.user import UserBase, router


class SignIn(BaseModel):
    user_email: Optional[EmailStr] = Field(None, title="Email address")
    user_hashed_password: Optional[str] = Field(None, title="Password", min_length=6)
    user_firstname: Optional[str] = Field(None, title="First name")
    user_lastname: Optional[str] = Field(None, title="Last name")


class SignUp(BaseModel):
    user_firstname: str = Field(None, title="First name")
    user_lastname: str = Field(None, title="Last name")
    user_email: EmailStr = Field(None, title="Email address")
    user_hashed_password: str = Field(None, title="Password", min_length=6)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "user_email": "user@gmail.com",
                "user_hashed_password": "PassWord123",
                "user_firstname": "David",
                "user_lastname": "White",
            }
        }
    )


@router.get("/user_signup/")
async def user_signup(user: SignUp) -> SignUp:
    return user


@router.get("/user_signin/{user_id}/")
async def user_signup(user: UserBase) -> UserBase:
    return user
