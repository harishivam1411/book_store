from pydantic import BaseModel, Field

from store.models.base.base_model import CreateSchema

class UserAuthCreate(BaseModel):
    username: str = Field(..., examples=["booklover99"])
    password: str = Field(..., examples=["securePassword123"])

class UserAuthResponse(CreateSchema):
    username: str = Field(..., examples=["booklover99"])
    password: str = Field(..., examples=["securePassword123"])