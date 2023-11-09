import datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, FilePath, HttpUrl, ConfigDict


class CompanyBase(BaseModel):
    company_id: UUID = Field(json_schema_extra={"primary_key": True, "unique": True}, default_factory=uuid4, title="ID")
    company_name: Optional[str] = Field(None, title="Name")
    company_title: Optional[str] = Field(None, title="Title")
    company_description: Optional[str] = Field(None, title="Description")
    company_city: Optional[str] = Field(None, title="City")
    company_phone: Optional[str] = Field(None, title="Phone")
    company_links: Optional[HttpUrl] = Field(None, title="Link")
    company_avatar: Optional[FilePath] = Field(None, title="Avatar")
    company_is_visible: bool = Field(False, title="Visible")
    company_created_at: Optional[datetime.datetime] = Field(None, title="Created")
    company_updated_at: Optional[datetime.datetime] = Field(None, title="Updated")
    owner_id: Optional[UUID] = Field(default=None)

    def __repr__(self):

        return (
            f"<{self.__class__.__name__}("
            f"company_id={self.company_id}, "
            f"company_name={self.company_name}, "
            f"company_title={self.company_title}, "
            f"company_description={self.company_description}, "
            f"company_is_visible={self.company_is_visible}, "
            f")>"
        )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "company_name": "Company Name",
                "company_title": "Company Title",
                "company_description": "Company Description",
                "company_is_visible": "False",
            }
        }
    )


class CompanyUpdate(BaseModel):
    company_name: Optional[str] = None
    company_title: Optional[str] = None
    company_description: Optional[str] = None
    company_is_visible: Optional[bool] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "company_name": "",
                "company_title": "",
                "company_description": "",
                "company_is_visible": "",
            }
        }
    )


class CompanyInvitationCreate(BaseModel):
    sender_id: UUID
    recipient_id: UUID
    company_id: UUID
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "recipient_id": "",
                "company_id": "",
            }
        }
    )


class CompanyMemberResponse(BaseModel):
    user_id: UUID
    user_email: str
    user_firstname: str
    user_lastname: str


class CompanyAdmin(BaseModel):
    user_id: str
    company_id: str
    is_admin: bool
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "user_id": "",
                "company_id": "",
                "is_admin": "False",
            }
        }
    )
