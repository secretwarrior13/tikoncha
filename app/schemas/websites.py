from typing import Optional

from pydantic import validator

from app.enums.enums import GeneralType, Priorities
from app.schemas.base import BaseSchema


class WebsiteBase(BaseSchema):
    url: str
    name: str
    general_type: Optional[GeneralType] = None
    priority: Optional[Priorities] = None

    @validator("url")
    def validate_url(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty")
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v


class WebsiteCreate(WebsiteBase):
    """Identical to WebsiteBase – used for clarity in routes"""


class WebsiteResponse(WebsiteBase):
    id: int
    created_at: str
    updated_at: str


class PolicyBase(BaseSchema):
    title: str
    content: str
    version: str

    @validator("title", "content", "version")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v


class PolicyCreate(PolicyBase):
    """For POST /policies"""


class PolicyResponse(PolicyBase):
    id: int
    created_at: str
    updated_at: str
