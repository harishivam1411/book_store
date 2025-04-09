from pydantic import BaseModel, Field
from datetime import datetime, timezone

class BaseSchema(BaseModel):
    id: str = Field(..., examples=["6683f946ec61bfa6a3c2d7c7"])
    name: str = Field(..., examples=["F. Scott Fitzgerald"])

class BookBaseSchema(BaseModel):
    id: str = Field(..., examples=["6683f946ec61bfa6a3c2d7c7"])
    title: str = Field(..., examples=["The Great Gatsby"])

class UserBaseSchema(BaseModel):
    id: str = Field(..., examples=["6683f946ec61bfa6a3c2d7c7"])
    username: str = Field(..., examples=["booklover99"])

class CreateSchema(BaseModel):
    id: str = Field(..., examples=["6683f946ec61bfa6a3c2d7c7"])
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CreateUpdateSchema(BaseModel):
    id: str = Field(..., examples=["6683f946ec61bfa6a3c2d7c7"])
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TokenRequest(BaseModel):
    id: str
    email: str

class TokenPayload(BaseModel):
    exp: int = None
    email: str = None
    id: str = None
    token_type: str = None

class TokenResponse(BaseModel):
    access_token: str = Field(..., examples=["eyJQGdtYWlsLmNvbSIsImlkIjoiNzBjMzhkYTEtNmEzYS00NDQ2LTg5MGMtNDYzOTM4YzA0NmFhIiwidG9rZW5fdHlwZSI6ImFjY2Vzc190b2tlbiJ9.IJI-K-BsqODkgjI8MN-NBxBKmIxQ6z_ZOLhmKWMouTc"])
    refresh_token: str = Field(..., examples=["eyJQGdtYWlsLmNvbSIsImlkIjoiNzBjMzhkYTEtNmEzYS00NDQ2LTg5MGMtNDYzOTM4YzA0NmFhIiwidG9rZW5fdHlwZSI6ImFjY2Vzc190b2tlbiJ9.IJI-K-BsqODkgjI8MN-NBxBKmIxQ6z_ZOLhmKWMouTc"])