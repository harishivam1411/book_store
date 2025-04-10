from fastapi import HTTPException
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from store.models.review.review_db import Review
from store.models.review.review_model import ReviewCreate, ReviewUpdate, ReviewCreateResponse, ReviewUpdateResponse, ReviewResponse, ReviewsResponse

class ReviewService:
    def __init__(self, db : AsyncIOMotorClient):
        self.db = db
        self.collection = db.review
        self.book_collection = db.book
        self.author_collection = db.author
        self.user_collection = db.user
        self.category_collection = db.category

    async def retrieve_reviews(self, book_id: str) -> list[ReviewsResponse]:

        # Verify book exists
        book = await self.book_collection.find_one({'_id': ObjectId(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
        
        result = self.collection.find()
        reviews = []
        async for review in result:
            review = self.__replace_id(review)
            
            # Get user details
            if user_id := review.get("user_id"):
                user = await self.user_collection.find_one({"_id": ObjectId(user_id)})
                if user:
                    user = self.__replace_id(user)
                    review["user"] = {"id": user["id"], "username": user["username"]}
                else:
                    review["user"] = {"id": user_id, "username": "Unknown user"}
            else:
                review["user"] = {"id": "", "username": "Unknown user"}
            
            reviews.append(ReviewResponse(**review))
        return reviews

    async def create_review(self, book_id: str, review: ReviewCreate) -> ReviewCreateResponse:
        # Verify book exists
        book = await self.book_collection.find_one({'_id': ObjectId(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
        
        # Get current user ID (in a real app, would come from auth token)
        # For now we'll use a placeholder
        current_user_id = "current_user_id"  # Replace with actual user ID from auth
        
        review_dict = review.model_dump()
        review_dict["book_id"] = book_id
        review_dict["user_id"] = current_user_id
        
        # Create the review
        review_model = Review(**review_dict)
        result = await self.collection.insert_one(review_model.model_dump())
        
        # Update book average rating
        await self.__update_book_avg_rating(book_id)
        
        # Add review to user's recent reviews
        await self.__add_to_user_reviews(current_user_id, result.inserted_id, book_id)
        
        return await self.retrieve_review(book_id, str(result.inserted_id))

    async def retrieve_review(self, book_id: str, review_id: str) -> ReviewResponse:
        try:
            review = await self.collection.find_one({'_id': ObjectId(review_id), 'book_id': book_id})
            if not review:
                raise HTTPException(status_code=404, detail=f"Review with ID {review_id} not found for book {book_id}")
                
            review = self.__replace_id(review)
            
            # Get user details
            if user_id := review.get("user_id"):
                user = await self.user_collection.find_one({"_id": ObjectId(user_id)})
                if user:
                    user = self.__replace_id(user)
                    review["user"] = {
                        "id": user["id"], 
                        "username": user["username"],
                        "first_name": user.get("first_name", ""),
                        "last_name": user.get("last_name", "")
                    }
                else:
                    review["user"] = {"id": user_id, "username": "Unknown user"}
            else:
                review["user"] = {"id": "", "username": "Unknown user"}
            
            return ReviewResponse(**review)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=404, detail=f"Review with ID {review_id} not found for book {book_id}")

    async def update_review(self, book_id: str, review_id: str, review: ReviewUpdate) -> ReviewUpdateResponse:
        # Verify review exists and belongs to the book
        existing_review = await self.collection.find_one({
            '_id': ObjectId(review_id),
            'book_id': book_id
        })
        if not existing_review:
            raise HTTPException(status_code=404, detail=f"Review with ID {review_id} not found for book {book_id}")
        
        # Verify current user owns the review
        # For now we'll use a placeholder
        current_user_id = "current_user_id"  # Replace with actual user ID from auth
        if str(existing_review.get("user_id")) != current_user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to update this review")
        
        update_data = review.model_dump(exclude_unset=True)
        
        # Update the 'updated_at' timestamp
        from datetime import datetime, timezone
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        await self.collection.update_one({'_id': ObjectId(review_id)}, {'$set': update_data})
        
        # Update book average rating
        await self.__update_book_avg_rating(book_id)
        
        return await self.retrieve_review(book_id, review_id)
    
    async def __update_book_avg_rating(self, book_id: str):
        """Update the average rating for a book based on all reviews"""
        try:
            pipeline = [
                {"$match": {"book_id": book_id}},
                {"$group": {"_id": None, "avgRating": {"$avg": "$rating"}}}
            ]
            result = await self.collection.aggregate(pipeline).to_list(length=1)
            
            if result and len(result) > 0:
                avg_rating = round(result[0]["avgRating"], 1)
                await self.book_collection.update_one(
                    {'_id': ObjectId(book_id)},
                    {'$set': {'average_rating': avg_rating}}
                )
        except:
            pass

    async def __add_to_user_reviews(self, user_id: str, review_id: str, book_id: str):
        """Add the review to the user's recent reviews list"""
        try:
            # Get book details
            book = await self.book_collection.find_one({'_id': ObjectId(book_id)})
            if not book:
                return
                
            book = self.__replace_id(book)
            
            # Get review details
            review = await self.collection.find_one({'_id': ObjectId(review_id)})
            if not review:
                return
                
            review = self.__replace_id(review)

            # Get user details
            user = await self.user_collection.find_one({'_id': ObjectId(user_id)})
            if not user:
                return
                
            user = self.__replace_id(user)
        except:
            pass

    @staticmethod
    def __replace_id(document):
        document['id'] = str(document.pop('_id'))
        return document