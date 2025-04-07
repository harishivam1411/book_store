from fastapi import APIRouter

category_router = APIRouter(prefix='/categories', tags=['Categories'])

@category_router.get('/')
async def retrieve_categories():
    pass

@category_router.post('/')
async def create_category():
    pass

@category_router.get('/{category_id}')
async def retrieve_category():
    pass

@category_router.put('/{category_id}')
async def update_category():
    pass