from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated
from ..models.user import UserCreate, UserInDB, Token
from ..security import (
    get_password_hash,
    create_access_token,
    get_current_user,
    verify_password
)
from ..config import settings
from ..database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/register", response_model=UserInDB)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # 检查用户名是否已存在
    existing_user = await UserInDB.get(user.username, db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = UserInDB(
        **user.dict(exclude={"password"}),
        hashed_password=hashed_password
    )
    await db_user.save(db)
    return db_user

@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
):
    user = await UserInDB.get(form_data.username, db)
    if not user or not verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserInDB)
async def read_users_me(
    current_user: Annotated[UserInDB, Depends(get_current_user)]
):
    return current_user
