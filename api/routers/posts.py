from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from api.database import get_db
from api.schemas.post import Post, Comment, CommentCreate
from api.models.user_model import DBUser as User
from api.schemas.post import PostCreate, PostUpdate
from api.services.post_service import PostService
from api.auth import get_current_user

router = APIRouter(prefix="/api/v1")

@router.post("/posts", response_model=Post, status_code=status.HTTP_201_CREATED, tags=["社区帖子"])
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await PostService(db).create_post(post, str(current_user.id))

@router.get("/posts", response_model=List[Post], tags=["社区帖子"])
async def get_posts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await PostService(db).get_posts()

@router.get("/posts/{post_id}", response_model=Post, tags=["社区帖子"])
async def get_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = await PostService(db).get_post(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")
    return post

@router.put("/posts/{post_id}", response_model=Post, tags=["社区帖子"])
async def update_post(
    post_id: UUID,
    post: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_post = await PostService(db).update_post(post_id, post, str(current_user.id))
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN if updated_post is None else status.HTTP_404_NOT_FOUND,
            detail="没有权限操作该资源" if updated_post is None else "帖子不存在"
        )
    return updated_post

@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["社区帖子"])
async def delete_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await PostService(db).delete_post(post_id, str(current_user.id))

@router.post("/posts/{post_id}/comments", response_model=Comment, status_code=status.HTTP_201_CREATED, tags=["社区帖子"])
async def create_comment(
    post_id: UUID,
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await PostService(db).create_comment(post_id, comment, str(current_user.id))

@router.get("/posts/{post_id}/comments", response_model=List[Comment], tags=["社区帖子"])
async def get_comments(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await PostService(db).get_comments(post_id)

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["社区帖子"])
async def delete_comment(
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await PostService(db).delete_comment(comment_id, str(current_user.id))
