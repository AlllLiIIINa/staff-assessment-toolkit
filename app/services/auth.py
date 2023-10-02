from pydantic import EmailStr, Field, ConfigDict

from app.schemas.user import UserBase


class SignIn(UserBase):
    email: EmailStr = Field(None, title="Email address")
    hashed_password: str = Field(None, title="Password", min_length=6)


class SignUp(UserBase):
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
