from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..models.user import UserInDB, UserCreate, UserUpdate, PasswordResetRequest, PasswordResetConfirm
from ..models.user_model import DBUser
from ..database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated, List
from uuid import UUID

router = APIRouter(prefix="/api/v1/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # 检查用户名是否已存在
    existing_user = await UserInDB.get(user.username, db)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 创建新用户
    user_in_db = UserInDB(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=UserInDB.get_password_hash(user.password),
        is_admin=user.is_admin
    )
    await user_in_db.save(db)
    return user_in_db

@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
):
    user = await UserInDB.authenticate(
        form_data.username, 
        form_data.password,
        db
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    return {"access_token": user.username, "token_type": "bearer"}

@router.get("/me")
async def read_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
):
    user = await UserInDB.get_current_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user

@router.put("/me")
async def update_current_user(
    user_update: UserUpdate,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
):
    current_user = await UserInDB.get_current_user(token, db)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    # 直接使用UserUpdate对象更新
    updated_user = await current_user.update(user_update, db)
    return updated_user

@router.delete("/me")
async def delete_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
):
    current_user = await UserInDB.get_current_user(token, db)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    await current_user.delete(db)
    return {"message": "User deleted successfully"}

# 管理员用户管理端点
@router.get("/", response_model=List[UserInDB])
async def list_users(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
):
    current_user = await UserInDB.get_current_user(token, db)
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required"
        )
    
    # 获取所有用户
    result = await db.execute(select(DBUser))
    db_users = result.scalars().all()
    
    # 转换为UserInDB对象列表并保留管理员状态
    users = []
    for db_user in db_users:
        user_dict = {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "hashed_password": db_user.hashed_password,
            "disabled": db_user.disabled,
            "is_admin": bool(db_user.is_admin)
        }
        user_in_db = UserInDB.model_validate(user_dict)
        users.append(user_in_db)
    
    # 过滤掉当前用户（管理员自己） - 统一转换为字符串比较
    current_user_id_str = str(current_user.id)
    filtered_users = [user for user in users if str(user.id) != current_user_id_str]
    
    print(f"Total users: {len(users)}, Filtered users count: {len(filtered_users)}")
    print(f"Current user id: {current_user.id}, Type: {type(current_user.id)}")
    print(f"User ids: {[str(user.id) for user in users]}")
    
    return filtered_users

@router.get("/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: UUID,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
):
    current_user = await UserInDB.get_current_user(token, db)
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required"
        )
    user = await UserInDB.get_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
):
    current_user = await UserInDB.get_current_user(token, db)
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required"
        )
    user = await UserInDB.get_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # 直接使用UserUpdate对象更新
    updated_user = await user.update(user_update, db)
    return updated_user

@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
):
    current_user = await UserInDB.get_current_user(token, db)
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required"
        )
    user = await UserInDB.get_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user.delete(db)
    return {"message": "User deleted successfully"}

@router.post("/password/reset")
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    token = await UserInDB.generate_password_reset_token(request.email, db)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found"
        )
    return {"message": "Password reset email sent"}

@router.post("/password/reset/confirm")
async def reset_password(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    success = await UserInDB.reset_password(request.token, request.new_password, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    return {"message": "Password updated successfully"}
