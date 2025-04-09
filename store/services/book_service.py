from fastapi import HTTPException
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from store.models.book.book_db import Book
from store.models.book.book_model import BookCreate, BookUpdate, BookResponse

class BookService:
    def __init__(self, db : AsyncIOMotorClient):
        self.db = db
        self.collection = db.book
        self.author = db.author
        self.category = db.category
        self.review = db.review

    async def retrieve_books(self) -> list[BookResponse]:
        result = self.collection.find()
        books = []
        async for book in result:
            book = self.__replace_id(book)
            book["author"] = book.get("author") or {"id": "6683f946ec61bfa6a3c2d7c7", "name": "Unknown Author"}
            book["categories"] = book.get("categories") or []
            books.append(BookResponse(**book))
        return books

    async def create_book(self, book: BookCreate) -> BookResponse:
        book_dict = book.model_dump()
        book = Book(**book_dict)
        result = await self.collection.insert_one(book.model_dump())
        return await self.retrieve_book(result.inserted_id)

    async def retrieve_book(self, inserted_id: str) -> BookResponse:
        book = await self.collection.find_one({'_id': ObjectId(inserted_id)})
        book = self.__replace_id(book)
        return BookResponse(**book)

    async def update_book(self, book_id: str, book: BookUpdate) -> BookResponse:
        is_book = await self.collection.find_one({'_id': ObjectId(book_id)})
        if not is_book:
            raise HTTPException(status_code=404, detail='Invalid book ID')
        book_dict = book.model_dump(exclude_unset=True)
        await self.collection.update_one({'_id': ObjectId(book_id)}, {'$set': book_dict})
        return await self.retrieve_book(book_id)

    @staticmethod
    def __replace_id(document):
        document['id'] = str(document.pop('_id'))
        return document
   
