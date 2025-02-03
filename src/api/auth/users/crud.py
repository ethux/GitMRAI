from supabase import Client
from src.api.auth.db.models import UserCreate, UserResponse
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Client, user: UserCreate):
    data = user.dict()
    data['password_hash'] = data['password']
    response = db.table('users').insert(data).execute()
    return response.data[0]

def login_user(db: Client, username: str, password: str):
    response = db.table('users').select("*").eq("username", username).execute()
    user = response.data[0] if response.data else None
    if user and pwd_context.verify(password, user['password_hash']):
        return UserResponse.from_orm(user)
    return None

def get_user(db: Client, user_id: int):
    response = db.table('users').select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None

def get_users(db: Client, skip: int = 0, limit: int = 10):
    response = db.table('users').select("*").range(skip, skip + limit - 1).execute()
    return response.data

def update_user(db: Client, user_id: int, user: UserCreate):
    data = user.dict()
    data['password_hash'] = data['password']
    response = db.table('users').update(data).eq("id", user_id).execute()
    return response.data[0]

def delete_user(db: Client, user_id: int):
    response = db.table('users').delete().eq("id", user_id).execute()
    return response.data[0]