from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from store.models.auth.auth_db import UserAuth
from store.models.base.base_model import TokenRequest, TokenResponse
from store.utils.util import get_hashed_password, verify_password, create_access_token, create_refresh_token

class AuthService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.collection = db.auth
        self.user_collection = db.user

    async def create_user(self, user_auth):
        # Check if username already exists
        existing_user = await self.user_collection.find_one({"username": user_auth.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Create user auth entry
        hashed_password = get_hashed_password(user_auth.password)
        user_auth_dict = user_auth.model_dump()
        user_auth_dict["password"] = hashed_password
        user_auth_obj = UserAuth(**user_auth_dict)
        
        # Insert into auth collection
        result = await self.collection.insert_one(user_auth_obj.model_dump())
        
        inserted_id = str(result.inserted_id)
        return {"id": inserted_id, **user_auth_dict}

    async def login(self, user_auth):
        user = await self.user_collection.find_one({"username": user_auth.username})
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        if not verify_password(user_auth.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Create token
        token_request = TokenRequest(id=str(user["_id"]), email=user.get("email", ""))
        access_token = create_access_token(token_request)
        refresh_token = create_refresh_token(token_request)
        
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    
    async def refresh_token(self, refresh_token: str):
        """
        Generate a new access token using a valid refresh token
        """
        validation_result = validate_token(refresh_token, is_refresh=True)
        if not validation_result.get("valid"):
            raise HTTPException(status_code=401, detail=validation_result.get("error", "Invalid refresh token"))
            
        # Get payload data
        payload = validation_result["payload"]
        username = payload.get("username")
        
        # Verify the user exists
        user = await self.user_collection.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create new access token
        token_request = TokenRequest(id=str(user["_id"]), username=user["username"])
        access_token = create_access_token(token_request)
        
        return {"access_token": access_token, "token_type": "bearer"}