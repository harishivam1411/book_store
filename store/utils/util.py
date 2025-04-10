import os
from jose import jwt
from dotenv import load_dotenv
from fastapi.security import HTTPBasic
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta

from store.models.base.base_model import TokenRequest, TokenPayload

load_dotenv()
security = HTTPBasic()

ACCESS_TOKEN_EXPIRE_MINUTES = 10
REFRESH_TOKEN_EXPIRE_MINUTES = 60 
ALGORITHM = os.environ['ALGORITHM']
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)

def create_access_token(subject: TokenRequest) -> str:
    expires_delta = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expires_delta, "username": subject.username, "id": subject.id, "token_type": "access_token"}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: TokenRequest) -> str:
    expires_delta = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expires_delta, "username": subject.username, "id": subject.id, "token_type": "refresh_token"}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def refresh_access_token(refresh_token: str) -> dict:
    """
    Generate a new access token using a valid refresh token
    """
    try:
        payload = decode_jwt(refresh_token, is_refresh=True)
        if not payload:
            return {"error": "Invalid or expired refresh token"}
            
        token_payload = TokenPayload(**payload)
        if token_payload.token_type != "refresh_token":
            return {"error": "Invalid token type"}
            
        token_request = TokenRequest(id=token_payload.id, username=token_payload.username)
        access_token = create_access_token(token_request)
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        return {"error": str(e)}

def validate_token(token: str, is_refresh: bool = False) -> dict:
    """
    Validate a token and return its payload if valid
    """
    try:
        payload = decode_jwt(token, is_refresh)
        if not payload:
            return {"valid": False, "error": "Invalid or expired token"}
            
        token_payload = TokenPayload(**payload)
        expected_type = "refresh_token" if is_refresh else "access_token"
        
        if token_payload.token_type != expected_type:
            return {"valid": False, "error": "Invalid token type"}
            
        return {"valid": True, "payload": token_payload.model_dump()}
    except Exception as e:
        return {"valid": False, "error": str(e)}

def decode_jwt(token: str, is_refresh: bool) -> dict:
    try:
        if is_refresh:
            key = JWT_REFRESH_SECRET_KEY
        else:
            key = JWT_SECRET_KEY
        decoded_token = jwt.decode(token, key, algorithms=[ALGORITHM])
        token_payload = TokenPayload(**decoded_token)
        return decoded_token if datetime.fromtimestamp(token_payload.exp) >= datetime.now(timezone.utc) else None
    except Exception as e:
        print(e)
        return {}