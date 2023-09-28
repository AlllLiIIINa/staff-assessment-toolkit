import datetime
from typing import Optional
from typing import List
from pydantic import Field
from pydantic import EmailStr
from pydantic import FilePath
from pydantic import HttpUrl
from fastapi_users import schemas


class UserBase(schemas.BaseUser):
    user_id: int
    user_email: EmailStr = Field(None, title="Email address")
    user_firstname: str = Field(None, title="First name")
    user_lastname: str = Field(None, title="Last name")
    user_status: bool = Field(None, title="Status")
    user_city: str = Field(None, title="City")
    user_phone: str = Field(None, title="Phone")
    user_links: HttpUrl = Field(None, title="Link")
    user_avatar: FilePath = Field(None, title="Avatar")
    hashed_password: str = Field(None, title="Password", min_length=6)
    is_superuser: bool = Field(False, title="Superuser")
    created_at: Optional[datetime.date] = Field(None, title="Created")
    updated_at: Optional[datetime.date] = Field(None, title="Updated")

    class Config:
        orm_mode = True


class UserUpdate(UserBase):
    hashed_password: str = Field(None, title="Password", min_length=6)


class SignIn(schemas.BaseUser):
    email: EmailStr = Field(None, title="Email address")
    hashed_password: str = Field(None, title="Password", min_length=6)


class SignUp(schemas.BaseUser):
    user_firstname: str = Field(None, title="First name")
    user_lastname: str = Field(None, title="Last name")
    email: EmailStr = Field(None, title="Email address")
    hashed_password: str = Field(None, title="Password", min_length=6)


class UsersList(schemas.BaseUser):
    users: List[UserBase]

    class Config:
        title = "Users List"


class UserDetail(schemas.BaseUser):
    pass
