`import pytest
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
        from app.models import Cat
        result = service.create(Cat, name='test')
        assert result is not None
        assert hasattr(result, 'id')

    def test_get_by_id(self, service):
        """测试根据ID获取"""
        from app.models import Cat
        obj = service.create(Cat, name='test')
        result = service.get(Cat, obj.id)
        assert result.id == obj.id

    def test_update(self, service):
        """测试更新方法"""
        from app.models import Cat
        obj = service.create(Cat, name='test')
        updated = service.update(Cat, obj.id, name='updated')
        assert updated.name == 'updated'

    def test_delete(self, service):
        """测试删除方法"""
        from app.models import Cat
        obj = service.create(Cat, name='test')
        service.delete(Cat, obj.id)
        assert service.get(Cat, obj.id) is None

    def test_list_all(self, service):
        """测试获取所有记录"""
        from app.models import Cat
        service.create(Cat, name='test1')
        service.create(Cat, name='test2')
        results = service.get_all(Cat)
        assert len(results) >= 2
