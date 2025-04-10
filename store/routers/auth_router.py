from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorClient

from store.database import get_database
from store.models.auth.auth_model import UserAuthCreate
from store.models.base.base_model import TokenResponse
from store.services.auth_service import AuthService
from store.utils.util import validate_token

auth_router = APIRouter(prefix='/auth', tags=['Auth'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

@auth_router.post('/', status_code=201)
async def create_user(user: UserAuthCreate, db: AsyncIOMotorClient = Depends(get_database)):
    service = AuthService(db)
    return await service.create_user(user)

@auth_router.post('/token', response_model=TokenResponse)
async def login(user: UserAuthCreate, db: AsyncIOMotorClient = Depends(get_database)):
    service = AuthService(db)
    return await service.login(user)

@auth_router.post('/refresh', response_model=dict)
async def refresh_token(refresh_token: str, db: AsyncIOMotorClient = Depends(get_database)):
    service = AuthService(db)
    return await service.refresh_token(refresh_token)

@auth_router.post('/validate', response_model=dict)
async def validate_access_token(token: str = Depends(oauth2_scheme)):
    """Validate an access token and return payload if valid"""
    result = validate_token(token)
    if not result.get("valid"):
        raise HTTPException(status_code=401, detail=result.get("error", "Invalid token"))
    return {"valid": True, "payload": result["payload"]}