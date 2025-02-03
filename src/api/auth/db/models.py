from pydantic import BaseModel, validator
from passlib.context import CryptContext
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    api_key: str = None

    @validator('password', pre=True, always=True)
    def hash_password(cls, v):
        return pwd_context.hash(v)

    @validator('api_key', pre=True, always=True)
    def generate_api_key(cls, v):
        if v is None:
            return secrets.token_urlsafe(32)
        return v

class User(UserBase):
    id: int
    password_hash: str
    api_key: str

    @classmethod
    def from_orm(cls, user_db):
        return cls(
            id=user_db['id'],
            username=user_db['username'],
            password_hash=user_db['password_hash'],
            api_key=user_db['api_key']
        )

class UserResponse(UserBase):
    id: int
    api_key: str

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, user_db):
        return cls(
            id=user_db['id'],
            username=user_db['username'],
            api_key=user_db['api_key']
        )

class UserLogin(BaseModel):
    username: str
    password: str