from fastapi import APIRouter, HTTPException, Depends, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.utils.security import hash_password, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    return {"user": current_user}

