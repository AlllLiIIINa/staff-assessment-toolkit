import datetime
from uuid import UUID, uuid4
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field, EmailStr, FilePath, HttpUrl, ConfigDict, field_validator


class UserBase(BaseModel):
    user_id: UUID = Field(json_schema_extra={"primary_key": True, "unique": True}, default_factory=uuid4, title="ID")
    user_email: EmailStr = Field(None, title="Email address")
    user_firstname: Optional[str] = Field(None, title="First name")
    user_lastname: Optional[str] = Field(None, title="Last name")
    user_birthday: Optional[datetime.date] = Field(None, title="Birthday")
    user_status: Optional[bool] = Field(None, title="Status")
    user_city: Optional[str] = Field(None, title="City")
    user_phone: Optional[str] = Field(None, title="Phone")
    user_links: Optional[HttpUrl] = Field(None, title="Link")
    user_avatar: Optional[FilePath] = Field(None, title="Avatar")
    user_hashed_password: Optional[str] = Field(None, title="Password", min_length=6)
    user_is_superuser: bool = Field(False, title="Superuser")
    user_created_at: Optional[datetime.datetime] = Field(None, title="Created")
    user_updated_at: Optional[datetime.datetime] = Field(None, title="Updated")

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"user_id={self.user_id}, "
            f"user_email={self.user_email}, "
            f"user_firstname={self.user_firstname}, "
            f"user_lastname={self.user_lastname}, "
            f")>"
        )

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


class UserUpdate(BaseModel):
    user_email: Optional[str] = None
    user_firstname: Optional[str] = None
    user_lastname: Optional[str] = None
    user_hashed_password: Optional[str] = None
    user_birthday: Optional[datetime.date] = None
    user_city: Optional[str] = None
    user_phone: Optional[str] = None
    user_links: Optional[HttpUrl] = None
    user_avatar: Optional[FilePath] = None

    @field_validator("*", mode='before')
    def update_only_allowed_fields(cls, values, field):
        allowed_fields = {'user_firstname', 'user_lastname', 'user_hashed_password'}
        field = field.field_name
        if field not in allowed_fields:
            raise HTTPException(status_code=400, detail=f"User is not allowed to update the field: {field}")
        return values

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "user_hashed_password": "",
                "user_firstname": "",
                "user_lastname": "",
            }
        }
    )
