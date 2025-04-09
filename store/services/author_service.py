from fastapi import HTTPException
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from store.models.author.author_db import Author
from store.models.author.author_model import AuthorCreate, AuthorUpdate, AuthorResponse

class AuthorService:
    def __init__(self, db : AsyncIOMotorClient):
        self.db = db
        self.collection = db.author
        self.book_collection = db.book

    async def retrieve_authors(self) -> list[AuthorResponse]:
        result = self.collection.find()
        authors = []
        async for author in result:
            author = self.__replace_id(author)
            author["books"] = author.get("books") or []
            authors.append(AuthorResponse(**author))
        return authors

    async def create_author(self, author: AuthorCreate) -> AuthorResponse:
        author_dict = author.model_dump()
        author = Author(**author_dict)
        result = await self.collection.insert_one(author.model_dump())
        return await self.retrieve_author(result.inserted_id)

    async def retrieve_author(self, inserted_id: str) -> AuthorResponse:
        author = await self.collection.find_one({'_id': ObjectId(inserted_id)})
        author = self.__replace_id(author)
        return AuthorResponse(**author)

    async def update_author(self, author_id: str, author: AuthorUpdate) -> AuthorResponse:
        is_author = await self.collection.find_one({'_id': ObjectId(author_id)})
        if not is_author:
            raise HTTPException(status_code=404, detail='Invalid author ID')
        author_dict = author.model_dump(exclude_unset=True)
        await self.collection.update_one({'_id': ObjectId(author_id)}, {'$set': author_dict})
        return await self.retrieve_author(author_id)

    @staticmethod
    def __replace_id(document):
        document['id'] = str(document.pop('_id'))
        return document