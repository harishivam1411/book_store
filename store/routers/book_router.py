from fastapi import APIRouter

book_router = APIRouter(prefix='/books', tags=['Books'])

@book_router.get('/')
async def retrieve_books():
    pass

@book_router.post('/')
async def create_book():
    pass

@book_router.get('/{book_id}')
async def retrieve_book():
    pass

@book_router.put('/{book_id}')
async def update_book():
    pass


