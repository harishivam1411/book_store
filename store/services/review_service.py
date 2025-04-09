from fastapi import HTTPException
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from store.models.review.review_db import Review
from store.models.review.review_model import ReviewCreate, ReviewUpdate, ReviewResponse

class ReviewService:
    def __init__(self, db : AsyncIOMotorClient):
        self.db = db
        self.collection = db.review
        self.user_collection = db.user
        self.book_collection = db.book

    async def retrieve_reviews(self, book_id: str) -> list[ReviewResponse]:
        result = self.collection.find()
        reviews = []
        async for review in result:
            review = self.__replace_id(review)
            review["user"] = review.get("user") or {"id": "6683f946ec61bfa6a3c2d7c7", "username": "Unknown user", "first_name": "Jane", "last_name": "Smith-Johnson"}
            reviews.append(ReviewResponse(**review))
        return reviews

    async def create_review(self, book_id: str, review: ReviewCreate) -> ReviewResponse:
        review_dict = review.model_dump()
        review_dict["book_id"] = book_id
        review = Review(**review_dict)
        result = await self.collection.insert_one(review.model_dump())
        return await self.retrieve_review(book_id, result.inserted_id)

    async def retrieve_review(self, book_id: str, inserted_id: str) -> ReviewResponse:
        review = await self.collection.find_one({'_id': ObjectId(inserted_id)})
        review = self.__replace_id(review)
        return ReviewResponse(**review)

    async def update_review(self, book_id: str, review_id: str, review: ReviewUpdate) -> ReviewResponse:
        is_review = await self.collection.find_one({'_id': ObjectId(review_id)})
        if not is_review:
            raise HTTPException(status_code=404, detail='Invalid review ID')
        review_dict = review.model_dump(exclude_unset=True)
        await self.collection.update_one({'_id': ObjectId(review_id)}, {'$set': review_dict})
        return await self.retrieve_review(book_id, review_id)

    @staticmethod
    def __replace_id(document):
        document['id'] = str(document.pop('_id'))
        return document