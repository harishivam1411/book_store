from fastapi import APIRouter

author_router = APIRouter(prefix='/authors', tags=['Authors'])

@author_router.get('/')
async def retrieve_authors():
    pass

@author_router.post('/')
async def create_author():
    pass

@author_router.get('/{author_id}')
async def retrieve_author():
    pass

@author_router.put('/{author_id}')
async def update_author():
    pass