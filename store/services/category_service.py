from bson import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from store.models.category.category_db import Category
from store.models.category.category_model import CategoryCreate, CategoryResponse, CategoryUpdate


class CategoryService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.collection = db.category

    async def create_category(self, category: CategoryCreate) -> CategoryResponse:
        category_dict = category.model_dump()
        category = Category(**category_dict)
        print(category)
        result = await self.collection.insert_one(category.model_dump())
        return await self.retrieve_category(result.inserted_id)
    
    async def retrieve_category(self, inserted_id: str) -> CategoryResponse:
        category = await self.collection.find_one({'_id': ObjectId(inserted_id)})
        category = self.__replace_id(category)
        return CategoryResponse(**category)

    async def retrieve_categories(self) -> list[CategoryResponse]:
        result = self.collection.find()
        categories = []
        async for category in result:
            category = self.__replace_id(category)
            categories.append(CategoryResponse(**category))
        return categories
    
    async def update_category(self, category_id: str, category: CategoryUpdate) -> CategoryResponse:
        is_category = await self.collection.find_one({'_id': ObjectId(category_id)})
        if not is_category:
            raise HTTPException(status_code=404, detail='Invalid Category ID')
        category_dict = category.model_dump(exclude_unset=True)
        await self.collection.update_one({'_id': ObjectId(category_id)}, {'$set': category_dict})
        return await self.retrieve_category(category_id)

    @staticmethod
    def __replace_id(document):
        document['id'] = str(document.pop('_id'))
        return document