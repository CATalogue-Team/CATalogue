import pytest
from api.models.user import UserInDB
from datetime import datetime
from uuid import uuid4

class TestUserModel:
    def test_user_creation(self):
        """测试用户模型创建"""
        user = UserInDB(
            id=uuid4(),
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpass",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.disabled is False

    def test_orm_mode(self):
        """测试ORM模式兼容性"""
        user_dict = {
            "id": str(uuid4()),
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": "hashedpass",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        user = UserInDB.parse_obj(user_dict)
        assert user.username == "testuser"
