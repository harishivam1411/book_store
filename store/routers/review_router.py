from fastapi import APIRouter

review_router = APIRouter(prefix='/books/{book_id}/reviews', tags=['Reviews'])

@review_router.get('/')
async def retrieve_reviews():
    pass

@review_router.post('/')
async def create_review():
    pass

@review_router.get('/{review_id}')
async def retrieve_review():
    pass

@review_router.put('/{review_id}')
async def update_review():
    pass