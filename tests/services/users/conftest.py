import pytest
from unittest.mock import MagicMock
from app.services import UserService
from app.extensions import db as _db
from tests.core.factories import UserFactory

@pytest.fixture
def user_service(app):
    """UserService测试fixture"""
    mock_db = MagicMock()
    mock_db.session = _db.session
    return UserService(mock_db)

@pytest.fixture
def test_user_data():
    """测试用户数据"""
    return {
        'username': 'testuser',
        'password': 'testpassword',
        'email': 'test@example.com'
    }
