from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorClient

from store.models.auth.auth_model import UserAuthCreate
from store.services.auth_service import AuthService

auth_router = APIRouter(prefix='/auth', tags=['Auth'])

@auth_router.post('/', status_code=201)
async def create_user(user: UserAuthCreate, db: AsyncIOMotorClient):
    service = AuthService(db)
    return service.create_user(user)