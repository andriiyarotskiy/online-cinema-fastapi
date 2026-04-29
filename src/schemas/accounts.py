from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator

from database import accounts_validators
from database.models.accounts import UserGroupEnum


class BaseEmailPasswordSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {"email": "moderator@mail.com", "password": "StrongPassword123!"}
        },
    )

    email: EmailStr = Field(..., description="User email address.")
    password: str = Field(
        ...,
        min_length=8,
        description="User password. Must satisfy password strength rules.",
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        return value.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        return accounts_validators.validate_password_strength(value)


class UserRegistrationRequestSchema(BaseEmailPasswordSchema):
    pass


class PasswordResetRequestSchema(BaseModel):
    email: EmailStr = Field(..., description="Email used for account registration.")


class PasswordResetCompleteRequestSchema(BaseEmailPasswordSchema):
    token: str = Field(..., description="Password reset token from email.")


class UserLoginRequestSchema(BaseEmailPasswordSchema):
    pass


class UserLoginResponseSchema(BaseModel):
    access_token: str = Field(..., description="Short-lived JWT access token.")
    refresh_token: str = Field(..., description="Long-lived JWT refresh token.")
    token_type: str = Field(default="bearer", description="Authorization token type.")


class UserRegistrationResponseSchema(BaseModel):
    id: int = Field(..., description="Created user ID.")
    email: EmailStr = Field(..., description="Registered email address.")

    model_config = {"from_attributes": True}


class UserActivationRequestSchema(BaseModel):
    email: EmailStr = Field(..., description="Registered user email.")
    token: str = Field(..., description="Activation token from verification email.")


class MessageResponseSchema(BaseModel):
    message: str = Field(..., description="Operation result message.")


class TokenRefreshRequestSchema(BaseModel):
    refresh_token: str = Field(..., description="Valid JWT refresh token.")


class TokenRefreshResponseSchema(BaseModel):
    access_token: str = Field(..., description="New JWT access token.")
    token_type: str = Field(default="bearer", description="Authorization token type.")


class UserRoleUpdateRequestSchema(BaseModel):
    group: UserGroupEnum = Field(..., description="Target user role.")
