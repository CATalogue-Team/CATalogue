import pytest
from uuid import UUID, uuid4
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from api.models.post import Post, Comment
from api.models.user_model import DBUser
from api.schemas.post import PostCreate, PostUpdate, CommentCreate
from api.auth import decode_access_token
from tests.api.conftest import auth_headers, admin_auth_headers, another_auth_headers

class TestPostAPI:
    """测试帖子API"""

    @pytest.mark.asyncio
    async def test_create_post(self, client: AsyncClient, test_user_data: dict, auth_headers):
        """测试创建帖子"""
        # 直接创建帖子（用户已在auth_headers固件中创建）
        post_data = PostCreate(
            title="测试帖子标题",
            content="测试帖子内容"
        ).model_dump()
        headers = auth_headers
        response = await client.post(
            "/api/v1/posts",
            json=post_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["title"] == post_data["title"]
        assert response.json()["content"] == post_data["content"]

    @pytest.mark.asyncio
    async def test_get_posts(self, client: AsyncClient, test_post, auth_headers):
        """测试获取帖子列表"""
        headers = auth_headers
        response = await client.get("/api/v1/posts", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) > 0
        assert response.json()[0]["id"] == str(test_post.id)

    @pytest.mark.asyncio
    async def test_get_post_by_id(self, client: AsyncClient, test_post, auth_headers):
        """测试获取单个帖子"""
        headers = auth_headers
        response = await client.get(f"/api/v1/posts/{str(test_post.id)}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == str(test_post.id)

    @pytest.mark.asyncio
    async def test_update_post(self, client: AsyncClient, test_post, auth_headers):
        """测试更新帖子"""
        update_data = PostUpdate(
            title="更新后的标题",
            content="更新后的内容"
        ).model_dump()
        headers = auth_headers
        response = await client.put(
            f"/api/v1/posts/{str(test_post.id)}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == update_data["title"]

    @pytest.mark.asyncio
    async def test_delete_post(self, client: AsyncClient, test_post, auth_headers):
        """测试删除帖子"""
        headers = auth_headers
        response = await client.delete(
            f"/api/v1/posts/{str(test_post.id)}",
            headers=headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_update_other_user_post(self, client: AsyncClient, db_session):
        """测试普通用户不能修改他人帖子"""
        from api.models.user_model import DBUser
        from api.models.post import Post
        from api.auth import create_access_token
        
        # 创建两个不同的用户
        user1 = DBUser(
            username=f"user1_{uuid4().hex[:8]}",
            email=f"user1_{uuid4().hex[:8]}@example.com",
            full_name="User 1",
            hashed_password="hashed_password1",
            is_admin=False
        )
        user2 = DBUser(
            username=f"user2_{uuid4().hex[:8]}",
            email=f"user2_{uuid4().hex[:8]}@example.com",
            full_name="User 2",
            hashed_password="hashed_password2",
            is_admin=False
        )
        db_session.add_all([user1, user2])
        await db_session.commit()
        
        # 创建帖子，作者是user1
        post = Post(
            title="测试帖子",
            content="测试内容",
            author_id=user1.id
        )
        db_session.add(post)
        await db_session.commit()
        
        # 为user2生成token
        token = create_access_token(data={"sub": user2.username})
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 尝试用user2修改user1的帖子
        update_data = PostUpdate(
            title="尝试修改他人帖子",
            content="不应该成功"
        ).model_dump()
        response = await client.put(
            f"/api/v1/posts/{str(post.id)}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_delete_other_user_post(self, client: AsyncClient, db_session):
        """测试普通用户不能删除他人帖子"""
        from api.models.user_model import DBUser
        from api.models.post import Post
        from api.auth import create_access_token
        
        # 创建两个不同的用户
        user1 = DBUser(
            username=f"user1_{uuid4().hex[:8]}",
            email=f"user1_{uuid4().hex[:8]}@example.com",
            full_name="User 1",
            hashed_password="hashed_password1",
            is_admin=False
        )
        user2 = DBUser(
            username=f"user2_{uuid4().hex[:8]}",
            email=f"user2_{uuid4().hex[:8]}@example.com",
            full_name="User 2",
            hashed_password="hashed_password2",
            is_admin=False
        )
        db_session.add_all([user1, user2])
        await db_session.commit()
        
        # 创建帖子，作者是user1
        post = Post(
            title="测试帖子",
            content="测试内容",
            author_id=user1.id
        )
        db_session.add(post)
        await db_session.commit()
        
        # 为user2生成token
        token = create_access_token(data={"sub": user2.username})
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 尝试用user2删除user1的帖子
        response = await client.delete(
            f"/api/v1/posts/{str(post.id)}",
            headers=headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_admin_can_manage_all_posts(self, client: AsyncClient, test_post, db_session):
        """测试管理员可以管理所有帖子"""
        from api.models.user_model import DBUser
        from api.auth import create_access_token
        
        # 直接创建管理员用户
        admin_user = DBUser(
            username=f"admin_{uuid4().hex[:8]}",
            email=f"admin_{uuid4().hex[:8]}@example.com",
            full_name="Admin User",
            hashed_password="hashed_adminpassword123",
            is_admin=True  # 确保设置为True
        )
        db_session.add(admin_user)
        await db_session.commit()
        await db_session.refresh(admin_user)
        
        # 为管理员用户生成token
        token = create_access_token(data={"sub": admin_user.username})
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 测试管理员更新帖子
        update_data = PostUpdate(
            title="管理员更新标题",
            content="管理员更新内容"
        ).model_dump()
        response = await client.put(
            f"/api/v1/posts/{str(test_post.id)}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK, \
            f"管理员更新帖子失败: {response.text}"

        # 测试管理员删除帖子
        response = await client.delete(
            f"/api/v1/posts/{str(test_post.id)}",
            headers=headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT, \
            f"管理员删除帖子失败: {response.text}"

class TestCommentAPI:
    """测试评论API"""

    @pytest.mark.asyncio
    async def test_create_comment(self, client: AsyncClient, test_post, auth_headers):
        """测试创建评论"""
        comment_data = CommentCreate(
            content="测试评论内容"
        ).model_dump()
        headers = auth_headers
        response = await client.post(
            f"/api/v1/posts/{str(test_post.id)}/comments",
            json=comment_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["content"] == comment_data["content"]

    @pytest.mark.asyncio
    async def test_get_comments(self, client: AsyncClient, test_comment):
        """测试获取评论列表"""
        response = await client.get(f"/api/v1/posts/{str(test_comment.post_id)}/comments")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) > 0
        assert response.json()[0]["id"] == str(test_comment.id)

    @pytest.mark.asyncio
    async def test_delete_comment(self, client: AsyncClient, test_comment, auth_headers):
        """测试删除评论"""
        headers = auth_headers
        response = await client.delete(
            f"/api/v1/comments/{str(test_comment.id)}",
            headers=headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_delete_other_user_comment(self, client: AsyncClient, db_session):
        """测试普通用户不能删除他人评论"""
        from api.models.user_model import DBUser
        from api.models.post import Post, Comment
        from api.auth import create_access_token
        
        # 创建两个不同的用户
        user1 = DBUser(
            username=f"user1_{uuid4().hex[:8]}",
            email=f"user1_{uuid4().hex[:8]}@example.com",
            full_name="User 1",
            hashed_password="hashed_password1",
            is_admin=False
        )
        user2 = DBUser(
            username=f"user2_{uuid4().hex[:8]}",
            email=f"user2_{uuid4().hex[:8]}@example.com",
            full_name="User 2",
            hashed_password="hashed_password2",
            is_admin=False
        )
        db_session.add_all([user1, user2])
        await db_session.commit()
        
        # 创建帖子和评论，作者都是user1
        post = Post(
            title="测试帖子",
            content="测试内容",
            author_id=user1.id
        )
        db_session.add(post)
        await db_session.commit()
        
        comment = Comment(
            content="测试评论",
            post_id=post.id,
            author_id=user1.id
        )
        db_session.add(comment)
        await db_session.commit()
        
        # 为user2生成token
        token = create_access_token(data={"sub": user2.username})
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 尝试用user2删除user1的评论
        response = await client.delete(
            f"/api/v1/comments/{str(comment.id)}",
            headers=headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_admin_can_delete_any_comment(self, client: AsyncClient, test_comment, db_session):
        """测试管理员可以删除任何评论"""
        from api.models.user_model import DBUser
        from api.auth import create_access_token
        
        # 直接创建管理员用户
        admin_user = DBUser(
            username=f"admin_{uuid4().hex[:8]}",
            email=f"admin_{uuid4().hex[:8]}@example.com",
            full_name="Admin User",
            hashed_password="hashed_adminpassword123",
            is_admin=True  # 确保设置为True
        )
        db_session.add(admin_user)
        await db_session.commit()
        await db_session.refresh(admin_user)
        
        # 为管理员用户生成token
        token = create_access_token(data={"sub": admin_user.username})
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = await client.delete(
            f"/api/v1/comments/{str(test_comment.id)}",
            headers=headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
