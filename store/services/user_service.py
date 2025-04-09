from fastapi import HTTPException
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from store.models.user.user_db import User
from store.models.user.user_model import UserCreate, UserUpdate, UserResponse

class UserService:
    def __init__(self, db : AsyncIOMotorClient):
        self.db = db
        self.collection = db.user

    async def retrieve_users(self) -> list[UserResponse]:
        result = self.collection.find()
        users = []
        async for user in result:
            user = self.__replace_id(user)
            user["recent_reviews"] = user.get("recent_reviews") or []
            users.append(UserResponse(**user))
        return users

    async def create_user(self, user: UserCreate) -> UserResponse:
        user_dict = user.model_dump()
        user = User(**user_dict)
        result = await self.collection.insert_one(user.model_dump())
        return await self.retrieve_user(result.inserted_id)

    async def retrieve_user(self, inserted_id: str) -> UserResponse:
        user = await self.collection.find_one({'_id': ObjectId(inserted_id)})
        user = self.__replace_id(user)
        return UserResponse(**user)

    async def update_user(self, user_id: str, user: UserUpdate) -> UserResponse:
        is_user = await self.collection.find_one({'_id': ObjectId(user_id)})
        if not is_user:
            raise HTTPException(status_code=404, detail='Invalid user ID')
        user_dict = user.model_dump(exclude_unset=True)
        await self.collection.update_one({'_id': ObjectId(user_id)}, {'$set': user_dict})
        return await self.retrieve_user(user_id)

    @staticmethod
    def __replace_id(document):
        document['id'] = str(document.pop('_id'))
        return document