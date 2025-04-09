from fastapi import HTTPException
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from store.models.auth.auth_db import UserAuth

class AuthService:
    def __init__(self, db : AsyncIOMotorClient):
        self.db = db
        self.collection = db.auth