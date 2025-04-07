from fastapi import APIRouter

user_router = APIRouter(prefix='/users', tags=['Users'])

@user_router.get('/')
async def retrieve_users():
    pass

@user_router.post('/')
async def create_user():
    pass

@user_router.get('/{user_id}')
async def retrieve_user():
    pass

@user_router.put('/{user_id}')
async def update_user():
    pass