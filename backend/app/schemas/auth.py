from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6)
    tenant_slug: str | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise ValueError("email is required")
        return value.lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
