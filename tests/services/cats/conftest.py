import pytest
from unittest.mock import MagicMock
from app.services import CatService
from app.extensions import db as _db
from tests.shared.factories.cat import CatFactory

@pytest.fixture
def cat_service(app):
    """CatService测试fixture"""
    mock_db = MagicMock()
    mock_db.session = _db.session
    return CatService(mock_db)

@pytest.fixture
def test_cat_data():
    """测试猫咪数据"""
    return {
        'name': '测试猫咪',
        'breed': '测试品种',
        'age': 2,
        'description': '测试描述'
    }
