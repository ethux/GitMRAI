from fastapi import APIRouter, Depends, HTTPException, Request, Form
from supabase import Client
from typing import List
from src.api.auth.db.models import UserCreate, UserResponse
from src.api.auth.users.crud import get_user, get_users, create_user, update_user, delete_user, login_user
from src.api.auth.db.database import get_db
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.post("/users/", response_model=UserResponse)
def create_user_endpoint(user: UserCreate, db: Client = Depends(get_db)):
    db_user = create_user(db=db, user=user)
    return UserResponse.from_orm(db_user)

@router.get("/users/{user_id}", response_model=UserResponse)
def read_user_endpoint(user_id: int, db: Client = Depends(get_db)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(db_user)

@router.get("/users/", response_model=List[UserResponse])
def read_users_endpoint(skip: int = 0, limit: int = 10, db: Client = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return [UserResponse.from_orm(user) for user in users]

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user_endpoint(user_id: int, user: UserCreate, db: Client = Depends(get_db)):
    db_user = update_user(db=db, user_id=user_id, user=user)
    return UserResponse.from_orm(db_user)

@router.delete("/users/{user_id}", response_model=UserResponse)
def delete_user_endpoint(user_id: int, db: Client = Depends(get_db)):
    db_user = delete_user(db=db, user_id=user_id)
    return UserResponse.from_orm(db_user)

@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def post_login(request: Request, username: str = Form(...), password: str = Form(...), db: Client = Depends(get_db)):
    user = login_user(db, username, password)
    if user:
        if not user.api_key:
            api_key = str(uuid.uuid4())
            logger.info(f"Generated API key for user {user.username}: {api_key}")
            update_user(db, user.id, UserCreate(username=username, password=password, api_key=api_key))
        else:
            api_key = user.api_key

        return templates.TemplateResponse("login_success.html", {"request": request, "api_key": api_key})
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

@router.get("/register", response_class=HTMLResponse)
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
def post_register(request: Request, username: str = Form(...), password: str = Form(...), db: Client = Depends(get_db)):
    user_create = UserCreate(username=username, password=password)
    db_user = create_user(db, user_create)
    return templates.TemplateResponse("register_success.html", {"request": request, "user": db_user})