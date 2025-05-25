import pytest
from app.services.base_service import BaseService
from app.models import db

class TestBaseService:
    @pytest.fixture
    def service(self, app):
        from unittest.mock import MagicMock
        mock_db = MagicMock()
        mock_db.session = db.session
        with app.app_context():
            yield BaseService(mock_db)

    def test_create(self, service):
        """测试创建方法"""
        result = service.create({'name': 'test'})
        assert result is not None
        assert hasattr(result, 'id')

    def test_get_by_id(self, service):
        """测试根据ID获取"""
        obj = service.create({'name': 'test'})
        result = service.get_by_id(obj.id)
        assert result.id == obj.id

    def test_update(self, service):
        """测试更新方法"""
        obj = service.create({'name': 'test'})
        updated = service.update(obj.id, {'name': 'updated'})
        assert updated.name == 'updated'

    def test_delete(self, service):
        """测试删除方法"""
        obj = service.create({'name': 'test'})
        service.delete(obj.id)
        assert service.get_by_id(obj.id) is None

    def test_list_all(self, service):
        """测试获取所有记录"""
        service.create({'name': 'test1'})
        service.create({'name': 'test2'})
        results = service.list_all()
        assert len(results) >= 2
