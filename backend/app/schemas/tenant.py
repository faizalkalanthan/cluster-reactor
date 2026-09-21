from pydantic import BaseModel, ConfigDict, Field


class TenantCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    slug: str = Field(..., min_length=2, max_length=60)
    domain: str | None = None
    is_active: bool = True


class TenantUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    slug: str | None = Field(default=None, min_length=2, max_length=60)
    domain: str | None = None
    is_active: bool | None = None


class TenantRead(BaseModel):
    id: int
    name: str
    slug: str
    domain: str | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
