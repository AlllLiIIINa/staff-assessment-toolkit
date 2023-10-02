import datetime
from typing import Optional
from typing import List
from pydantic import BaseModel, Field, EmailStr, FilePath, HttpUrl


class UserBase(BaseModel):
    user_id: int
    user_email: EmailStr = Field(None, title="Email address")
    user_firstname: str = Field(None, title="First name")
    user_lastname: str = Field(None, title="Last name")
    user_status: bool = Field(None, title="Status")
    user_city: str = Field(None, title="City")
    user_phone: str = Field(None, title="Phone")
    user_links: HttpUrl = Field(None, title="Link")
    user_avatar: FilePath = Field(None, title="Avatar")
    user_hashed_password: str = Field(None, title="Password", min_length=6)
    is_superuser: bool = Field(False, title="Superuser")
    created_at: Optional[datetime.date] = Field(None, title="Created")
    updated_at: Optional[datetime.date] = Field(None, title="Updated")


class UserUpdate(BaseModel):
    hashed_password: str = Field(None, title="Password", min_length=6)


class UsersList(BaseModel):
    users: List[BaseModel]

    class Config:
        title = "Users List"


class UserDetail(BaseModel):
    pass
