from pydantic import BaseModel, Field
from datetime import datetime, timezone

class Category(BaseModel):
    name: str = Field(...)
    description: str = Field(None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    