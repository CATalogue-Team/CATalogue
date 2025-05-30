import pytest
from app.services.cat_service import CatService
from app.models import Cat, db

class TestCatService:
    @pytest.fixture
    def service(self, app):
        from unittest.mock import MagicMock
        mock_db = MagicMock()
        mock_db.session = db.session
        with app.app_context():
            db.create_all()  # 确保测试前创建所有表
            yield CatService(mock_db)
            db.session.remove()

    @pytest.fixture
    def sample_cat(self, service):
        return service.create({
            'name': 'Fluffy',
            'age': 3,
            'breed': 'Persian',
            'description': 'A cute cat'
        })

    def test_create_cat(self, service):
        """测试创建猫咪"""
        cat = service.create({
            'name': 'Whiskers',
            'age': 2,
            'breed': 'Siamese',
            'description': 'Playful cat'
        })
        assert cat.id is not None
        assert cat.name == 'Whiskers'

    def test_get_cat_by_id(self, service, sample_cat):
        """测试根据ID获取猫咪"""
        cat = service.get_by_id(sample_cat.id)
        assert cat.id == sample_cat.id
        assert cat.name == 'Fluffy'

    def test_update_cat(self, service, sample_cat):
        """测试更新猫咪信息"""
        updated = service.update(sample_cat.id, {
            'name': 'Fluffy Updated',
            'age': 4
        })
        assert updated.name == 'Fluffy Updated'
        assert updated.age == 4

    def test_delete_cat(self, service, sample_cat):
        """测试删除猫咪"""
        service.delete(sample_cat.id)
        assert service.get_by_id(sample_cat.id) is None

    def test_list_cats(self, service):
        """测试获取猫咪列表"""
        service.create({'name': 'Cat1', 'age': 1, 'breed': 'TestBreed1', 'description': 'Test cat 1'})
        service.create({'name': 'Cat2', 'age': 2, 'breed': 'TestBreed2', 'description': 'Test cat 2'})
        cats = service.list_all()
        assert len(cats) >= 2

    def test_search_cats(self, service):
        """测试搜索猫咪"""
        service.create({'name': 'SearchCat', 'breed': 'TestBreed', 'age': 3, 'description': 'Test search cat'})
        results = service.search({'breed': 'TestBreed'})
        assert len(results) > 0
        assert results[0].breed == 'TestBreed'

    def test_get_cat_stats(self, service):
        """测试获取猫咪统计信息"""
        stats = service.get_cat_stats()
        assert 'total' in stats
        assert 'by_breed' in stats

    def test_upload_cat_image(self, service, sample_cat):
        """测试上传猫咪图片"""
        # 这里可以模拟文件上传测试
        result = service.upload_image(sample_cat.id, 'test.jpg', b'image_data')
        assert result is True
