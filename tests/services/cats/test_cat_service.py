import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

from app.models import Cat, CatImage
from app.services import CatService
from tests.core.factories import CatFactory

@pytest.mark.service
@pytest.mark.cat
class TestCatService:
    """CatService测试类"""
    
    def test_create_cat(self, cat_service, test_cat_data, app):
        """测试创建猫咪"""
        with app.app_context():
            # 测试正常创建
            cat = cat_service.create_cat(**test_cat_data, user_id=1)
            assert cat.id is not None
            assert cat.name == test_cat_data['name']
            
            # 测试重复名称
            with pytest.raises(ValueError):
                cat_service.create_cat(**test_cat_data, user_id=1)
                
    def test_boundary_values(self, cat_service, app):
        """测试边界值"""
        with app.app_context():
            # 测试最小年龄
            young_cat = cat_service.create_cat(
                name='Young_Cat',
                breed='Test Breed',
                age=0,
                description='Test',
                user_id=1
            )
            assert young_cat.age == 0
            
    def test_crud_operations(self, cat_service, test_cat_data, app):
        """测试CRUD操作"""
        with app.app_context():
            # 创建
            cat = cat_service.create_cat(**test_cat_data, user_id=1)
            
            # 读取
            found = cat_service.get(Cat, cat.id)
            assert found == cat
            
            # 更新
            updated = cat_service.update_cat(cat.id, age=3)
            assert updated.age == 3
            
            # 删除
            assert cat_service.delete(cat.id) is True
            assert cat_service.get(Cat, cat.id) is None
            
    def test_image_handling(self, cat_service, app):
        """测试图片处理"""
        with app.app_context():
            cat = CatFactory().make_instance(user_id=1)
            
            # 测试有效图片
            valid_file = FileStorage(
                stream=BytesIO(b'test'),
                filename='test.jpg',
                content_type='image/jpeg'
            )
            cat_service._handle_images(cat.id, [valid_file])
            
            # 验证图片
            from app.extensions import db
            images = db.session.query(CatImage).filter_by(cat_id=cat.id).all()
            assert len(images) == 1
            
            # 测试无效文件类型
            invalid_file = FileStorage(
                stream=BytesIO(b'invalid'),
                filename='test.txt',
                content_type='text/plain'
            )
            with pytest.raises(ValueError):
                cat_service._handle_images(cat.id, [invalid_file])
                
    def test_concurrent_operations(self, cat_service, app):
        """测试并发操作"""
        with app.app_context():
            test_data = [
                {'name': f'Cat_{i}', 'breed': 'B', 'age': i, 'description': 'D', 'user_id': 1}
                for i in range(5)
            ]
            
            def create_cat(data):
                try:
                    return cat_service.create_cat(**data).id
                except:
                    return None
                    
            with ThreadPoolExecutor(max_workers=5) as executor:
                results = list(executor.map(create_cat, test_data))
                assert len([r for r in results if r is not None]) == 5
