from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict, HttpUrl, FilePath


class SignIn(BaseModel):
    access_token: str
    token_type: str


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


class UserOut(BaseModel):
    user_email: Optional[EmailStr] = None
    user_firstname: Optional[str] = None
    user_lastname: Optional[str] = None
    user_birthday: Optional[str] = None
    user_city: Optional[str] = None
    user_phone: Optional[str] = None
    user_links: Optional[HttpUrl] = None
    user_avatar: Optional[FilePath] = None


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_firstname: Optional[str] = None
    user_lastname: Optional[str] = None
    user_birthday: Optional[str] = None
    user_city: Optional[str] = None
    user_phone: Optional[str] = None
    user_links: Optional[str] = None
    user_avatar: Optional[str] = None
