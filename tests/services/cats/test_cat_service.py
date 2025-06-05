import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

from app.models import Cat, CatImage
from app.services import CatService
from app.extensions import db
from tests.shared.factories.cat import CatFactory

@pytest.mark.service
@pytest.mark.cat
class TestCatService:
    """CatService测试类"""
    
    def test_create_cat(self, cat_service, test_cat_data, app):
        """测试创建猫咪"""
        with app.app_context():
            # 创建测试用户
            from app.models import User
            user = User(username="testuser")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()
            
            # 测试正常创建
            cat = cat_service.create_cat(**test_cat_data, user_id=user.id)
            assert cat.id is not None
            assert cat.name == test_cat_data['name']
            
            # 测试重复名称
            with pytest.raises(ValueError):
                cat_service.create_cat(**test_cat_data, user_id=1)
                
    def test_boundary_values(self, cat_service, app):
        """测试边界值"""
        with app.app_context():
            # 创建测试用户
            from app.models import User
            user = User(username="testuser")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()
            
            # 测试最小年龄
            young_cat = cat_service.create_cat(
                name='Young_Cat',
                breed='Test Breed',
                age=0,
                description='Test',
                user_id=user.id
            )
            assert young_cat.age == 0
            
    def test_crud_operations(self, cat_service, test_cat_data, app):
        """测试CRUD操作"""
        with app.app_context():
            # 创建测试用户
            from app.models import User
            user = User(username="testuser")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()
            
            # 创建
            cat = cat_service.create_cat(**test_cat_data, user_id=user.id)
            
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
        """测试并发操作(使用单线程模拟)"""
        with app.app_context():
            # 创建测试用户
            from app.models import User
            user = User(username="testuser_concurrent")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()

            test_data = [
                {'name': f'Cat_{i}', 'breed': 'B', 'age': i, 'description': 'D', 'user_id': user.id}
                for i in range(5)
            ]

            created_ids = []
            
            # 使用单线程循环模拟并发
            for data in test_data:
                try:
                    cat = cat_service.create_cat(**data)
                    db.session.commit()
                    created_ids.append(cat.id)
                except:
                    db.session.rollback()
            
            assert len(created_ids) == 5
                
            # 清理测试数据
            for cat_id in created_ids:
                cat = db.session.get(Cat, cat_id)
                if cat:
                    db.session.delete(cat)
            db.session.delete(user)
            db.session.commit()
