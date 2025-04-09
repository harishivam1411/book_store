import os
from jose import jwt
from fastapi.security import HTTPBasic
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta

from store.models.base.base_model import TokenRequest, TokenPayload

security = HTTPBasic()

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)

def create_access_token(subject: TokenRequest) -> str:
    expires_delta = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expires_delta, "email": subject.email, "id": subject.id, "token_type": "access_token"}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: TokenRequest) -> str:
    expires_delta = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expires_delta, "email": subject.email, "id": subject.id, "token_type": "refresh_token"}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt

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