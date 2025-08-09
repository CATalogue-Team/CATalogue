from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Union
from uuid import UUID
import logging
from sqlalchemy import Column

from api.models.post import Post, Comment
from api.schemas.post import PostCreate, PostUpdate, CommentCreate, Post as PostSchema, Comment as CommentSchema
from api.models.user import DBUser

logger = logging.getLogger(__name__)

class PostService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _check_permission(self, resource_author_id: Union[UUID, str], user_id: Union[UUID, str]):
        """检查用户是否有操作权限"""
        try:
            user_uuid = UUID(str(user_id)) if user_id else None
            if not user_uuid:
                logger.warning("No user UUID provided")
                return False
        except ValueError:
            logger.warning(f"Invalid UUID format: {user_id}")
            return False
            
        try:
            # 直接从数据库获取用户信息
            stmt = select(DBUser).where(DBUser.id == user_uuid)
            result = await self.db.execute(stmt)
            db_user = result.scalar_one_or_none()
            
            if not db_user:
                logger.warning(f"User not found: {user_uuid}")
                return False
                
            # 显式转换为 Python 布尔值 - 确保正确处理默认值
            is_admin = db_user.is_admin if db_user.is_admin is not None else False
            logger.info(f"User {db_user.username} (ID: {db_user.id}) is_admin: {is_admin}")
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return False
            
        # 处理resource_author_id
        author_uuid = None
        if isinstance(resource_author_id, UUID):
            author_uuid = resource_author_id
        elif resource_author_id:
            try:
                author_uuid = UUID(str(resource_author_id))
            except ValueError:
                pass
                
        # 确保资源有作者
        if not author_uuid:
            logger.warning(f"Resource has no author")
            return False
            
        # 检查用户是否是管理员 - 管理员有所有权限
        if is_admin is True:
            logger.info(f"Admin access granted for user {user_uuid}")
            return True
            
        # 检查用户是否是资源所有者
        logger.info(f"Comparing author_uuid: {str(author_uuid)} with db_user.id: {str(db_user.id)}")
        if str(author_uuid) == str(db_user.id):  # 比较字符串形式的ID
            logger.info(f"Owner access granted for user {db_user.id}")
            return True
            
        logger.warning(f"Permission denied for user {user_uuid} on resource by {author_uuid}")
        logger.warning(f"User is_admin: {db_user.is_admin}")
        return False

    async def create_post(self, post_data: PostCreate, author_id: Union[UUID, str]) -> PostSchema:
        """创建新帖子"""
        author_uuid = UUID(author_id) if isinstance(author_id, str) else author_id
        post = Post(**post_data.model_dump(), author_id=author_uuid)
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        
        # 确保所有UUID字段被正确转换
        post_dict = {
            'id': str(post.id),
            'title': post.title,
            'content': post.content,
            'author_id': str(post.author_id),
            'created_at': post.created_at,
            'updated_at': post.updated_at,
            'likes': post.likes,
            'author': post.author
        }
        return PostSchema.model_validate(post_dict)

    async def get_posts(self) -> List[PostSchema]:
        """获取所有帖子"""
        result = await self.db.execute(select(Post))
        posts = result.unique().scalars().all()
        
        result = []
        for post in posts:
            post_dict = {
                'id': str(post.id),
                'title': post.title,
                'content': post.content,
                'author_id': str(post.author_id),
                'created_at': post.created_at,
                'updated_at': post.updated_at,
                'likes': post.likes,
                'author': post.author
            }
            result.append(PostSchema.model_validate(post_dict))
        return result

    async def get_post(self, post_id: Union[UUID, str]) -> Optional[PostSchema]:
        """获取单个帖子"""
        post_uuid = UUID(post_id) if isinstance(post_id, str) else post_id
        result = await self.db.execute(select(Post).where(Post.id == post_uuid))
        post = result.unique().scalar_one_or_none()
        if not post:
            return None
            
        post_dict = {
            'id': str(post.id),
            'title': post.title,
            'content': post.content,
            'author_id': str(post.author_id),
            'created_at': post.created_at,
            'updated_at': post.updated_at,
            'likes': post.likes,
            'author': post.author
        }
        return PostSchema.model_validate(post_dict)

    async def update_post(self, post_id: Union[UUID, str], post_data: PostUpdate, user_id: Union[UUID, str]) -> PostSchema:
        """更新帖子"""
        post_uuid = UUID(post_id) if isinstance(post_id, str) else post_id
        db_post = await self.db.get(Post, post_uuid)
        if not db_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="帖子不存在"
            )
            
        # 获取实际的 author_id UUID 值
        author_id = db_post.author_id
        if isinstance(author_id, Column):
            author_id = author_id.value
        has_permission = await self._check_permission(author_id, user_id)
        if has_permission is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限操作该资源"
            )
            
        for key, value in post_data.model_dump(exclude_unset=True).items():
            setattr(db_post, key, value)
            
        await self.db.commit()
        await self.db.refresh(db_post)
        return PostSchema.model_validate(db_post)

    async def delete_post(self, post_id: Union[UUID, str], user_id: Union[UUID, str]) -> None:
        """删除帖子"""
        post_uuid = UUID(post_id) if isinstance(post_id, str) else post_id
        db_post = await self.db.get(Post, post_uuid)
        if not db_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="帖子不存在"
            )
            
        # 获取实际的 author_id UUID 值
        author_id = db_post.author_id
        if isinstance(author_id, Column):
            author_id = author_id.value
        has_permission = await self._check_permission(author_id, user_id)
        if has_permission is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限操作该资源"
            )
            
        await self.db.delete(db_post)
        await self.db.commit()

    async def create_comment(self, post_id: Union[UUID, str], comment_data: CommentCreate, author_id: Union[UUID, str]) -> CommentSchema:
        """创建评论"""
        post_uuid = UUID(post_id) if isinstance(post_id, str) else post_id
        
        # 检查帖子是否存在
        post = await self.db.get(Post, post_uuid)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="帖子不存在"
            )
            
        author_uuid = UUID(author_id) if isinstance(author_id, str) else author_id
        comment = Comment(**comment_data.model_dump(), post_id=post_uuid, author_id=author_uuid)
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        
        # 确保所有UUID字段被正确转换
        comment_dict = {
            'id': str(comment.id),
            'content': comment.content,
            'author_id': str(comment.author_id),
            'post_id': str(comment.post_id),
            'created_at': comment.created_at,
            'author': comment.author
        }
        return CommentSchema.model_validate(comment_dict)

    async def get_comments(self, post_id: Union[UUID, str]) -> List[CommentSchema]:
        """获取帖子评论"""
        post_uuid = UUID(post_id) if isinstance(post_id, str) else post_id
        result = await self.db.execute(select(Comment).where(Comment.post_id == post_uuid))
        comments = result.unique().scalars().all()
        
        result = []
        for comment in comments:
            comment_dict = {
                'id': str(comment.id),
                'content': comment.content,
                'author_id': str(comment.author_id),
                'post_id': str(comment.post_id),
                'created_at': comment.created_at,
                'author': comment.author
            }
            result.append(CommentSchema.model_validate(comment_dict))
        return result

    async def delete_comment(self, comment_id: Union[UUID, str], user_id: Union[UUID, str]) -> None:
        """删除评论"""
        comment_uuid = UUID(comment_id) if isinstance(comment_id, str) else comment_id
        comment = await self.db.get(Comment, comment_uuid)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )
            
        # 获取实际的 author_id UUID 值
        author_id = comment.author_id
        if isinstance(author_id, Column):
            author_id = author_id.value
        has_permission = await self._check_permission(author_id, user_id)
        if has_permission is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限操作该资源"
            )
            
        await self.db.delete(comment)
        await self.db.commit()
