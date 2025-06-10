import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
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
                
    def test_update_cat(self, cat_service, app):
        """测试更新猫咪信息"""
        with app.app_context():
            # 创建测试用户和猫咪
            from app.models import User, Cat
            user = User(username="testuser_update")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()
            
            cat = Cat(name="TestCat", breed="Breed", age=2, description="Test", user_id=user.id)
            db.session.add(cat)
            db.session.commit()
            
            # 正常更新
            updated_cat = cat_service.update_cat(cat.id, name="UpdatedCat", age=3)
            assert updated_cat.name == "UpdatedCat"
            assert updated_cat.age == 3
            
            # 更新不存在ID
            with pytest.raises(ValueError):
                cat_service.update_cat(999, name="Nonexistent")
                
            # 清理
            db.session.delete(cat)
            db.session.delete(user)
            db.session.commit()
            
    def test_delete_cat(self, cat_service, app):
        """测试删除猫咪"""
        with app.app_context():
            # 创建测试用户和猫咪
            from app.models import User, Cat
            user = User(username="testuser_delete")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()
            
            cat = Cat(name="TestCat", breed="Breed", age=2, description="Test", user_id=user.id)
            db.session.add(cat)
            db.session.commit()
            
            # 正常删除
            assert cat_service.delete_cat(cat.id) is True
            
            # 删除不存在ID
            with pytest.raises(ValueError):
                cat_service.delete_cat(999)
                
            # 清理
            db.session.delete(user)
            db.session.commit()
            
    def test_batch_update(self, cat_service, app):
        """测试批量更新猫咪"""
        with app.app_context():
            # 创建测试用户和猫咪
            from app.models import User, Cat
            user = User(username="testuser_batch_update")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()
            
            cat1 = Cat(name="Cat1", breed="Breed", age=1, user_id=user.id)
            cat2 = Cat(name="Cat2", breed="Breed", age=2, user_id=user.id)
            db.session.add_all([cat1, cat2])
            db.session.commit()
            
            # 批量更新
            updates = {
                cat1.id: {"age": 3},
                cat2.id: {"name": "UpdatedCat2", "age": 4}
            }
            results = cat_service.batch_update(updates)
            assert len(results) == 2
            assert all(result is not None for result in results)
            
            # 验证更新
            updated_cat1 = db.session.get(Cat, cat1.id)
            assert updated_cat1 is not None
            assert updated_cat1.age == 3
            updated_cat2 = db.session.get(Cat, cat2.id)
            assert updated_cat2 is not None
            assert updated_cat2.name == "UpdatedCat2"
            assert updated_cat2.age == 4
            
            # 清理
            db.session.delete(cat1)
            db.session.delete(cat2)
            db.session.delete(user)
            db.session.commit()
            
    def test_search_cats(self, cat_service, app):
        """测试搜索猫咪"""
        with app.app_context():
            # 创建测试用户和猫咪
            from app.models import User, Cat
            user = User(username="testuser_search")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()
            
            cat1 = Cat(name="Fluffy", breed="Persian", age=3, description="White fluffy cat", user_id=user.id)
            cat2 = Cat(name="Whiskers", breed="Siamese", age=5, description="Playful cat", user_id=user.id)
            db.session.add_all([cat1, cat2])
            db.session.commit()
            
            # 按名称搜索
            results = cat_service.search(name="Fluffy")
            assert len(results) == 1
            assert results[0].name == "Fluffy"
            
            # 按品种搜索
            results = cat_service.search(breed="Siamese")
            assert len(results) == 1
            assert results[0].breed == "Siamese"
            
            # 按年龄范围搜索
            results = cat_service.search(min_age=4, max_age=6)
            assert len(results) == 1
            assert results[0].name == "Whiskers"
            
            # 测试空结果
            results = cat_service.search(name="Nonexistent")
            assert len(results) == 0
            
            # 清理
            db.session.delete(cat1)
            db.session.delete(cat2)
            db.session.delete(user)
            db.session.commit()

@pytest.mark.service
@pytest.mark.cat
class TestCatServiceEdgeCases:
    """CatService边界条件和异常测试"""

    # ... 其他测试方法保持不变 ...

    def test_batch_operations_errors(self, cat_service, app):
        """测试批量操作的错误处理"""
        with app.app_context(), \
             patch('app.services.cat_service.current_app.logger.error') as mock_logger:
            from app.models import User
            user = User(username="testuser_batch_error")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()

            # 测试批量创建失败
            with patch('app.extensions.db.session.commit', side_effect=Exception("DB Error")):
                with pytest.raises(Exception):
                    cat_service.batch_create([{
                        'name': 'Batch_Fail',
                        'breed': 'Test', 
                        'age': 1,
                        'description': 'Test'
                    }], user.id)
                
                # 验证错误日志被记录
                mock_logger.assert_called_with("创建猫咪失败: DB Error")

            # 测试批量更新失败
            cat = cat_service.create_cat(
                name='Batch_Update_Cat',
                breed='Test Breed',
                age=2,
                description='Test',
                user_id=user.id
            )
            with patch('app.extensions.db.session.commit', side_effect=Exception("DB Error")):
                with pytest.raises(Exception):
                    cat_service.batch_update({cat.id: {'age': 3}})
                mock_logger.assert_called_with("批量更新猫咪失败: DB Error")

            # 先删除所有关联的Cat对象
            for cat in db.session.query(Cat).filter_by(user_id=user.id).all():
                db.session.delete(cat)
            try:
                db.session.delete(user)
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

    def test_batch_operations_partial_success(self, cat_service, app):
        """测试批量操作的部分成功场景"""
        with app.app_context(), \
             patch('app.services.cat_service.current_app.logger.error') as mock_logger:
            from app.models import User
            user = User(username="testuser_batch_partial")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()

            # 创建部分有效数据
            batch_data = [
                {'name': 'Valid_Cat_1', 'breed': 'Breed', 'age': 1, 'description': 'Valid'},
                {'name': '', 'breed': 'Breed', 'age': 2, 'description': 'Invalid'},  # 无效名称
                {'name': 'Valid_Cat_2', 'breed': 'Breed', 'age': 3, 'description': 'Valid'}
            ]

            # 测试部分成功
            result = cat_service.batch_create(batch_data, user.id)
            
            # 验证返回列表包含3个结果
            assert isinstance(result, list)
            assert len(result) == 3
            # 验证第二个元素是None(表示失败)
            assert result[1] is None
            # 验证其他元素是Cat对象
            assert isinstance(result[0], Cat)
            assert isinstance(result[2], Cat)
            
            # 验证错误日志被记录
            mock_logger.assert_called()

            # 先删除所有关联的Cat对象
            for cat in db.session.query(Cat).filter_by(user_id=user.id).all():
                db.session.delete(cat)
            try:
                db.session.delete(user)
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

    def test_image_handling(self, cat_service, app):
        """测试图片处理逻辑"""
        with app.app_context(), patch('os.path.join'), \
             patch('werkzeug.utils.secure_filename', return_value="test.jpg"):
            
            # 创建测试用户和猫咪
            from app.models import User, Cat
            user = User(username="testuser_images")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()
            
            # 创建猫咪
            cat = cat_service.create_cat(
                name="TestCatImages",
                breed="Test",
                age=2,
                description="Test",
                user_id=user.id
            )
            
            # 模拟图片文件
            mock_image = MagicMock()
            mock_image.filename = "test.jpg"
            mock_image.content_type = "image/jpeg"
            mock_image.read.return_value = b"test image data"
            # 添加 seek 和 tell 方法
            mock_image.seek = MagicMock()
            mock_image.tell = MagicMock(return_value=1024)  # 默认1KB大小
            
            # 测试空图片列表
            cat_service._handle_images(cat.id, [])
            
            # 测试有效图片
            cat_service._handle_images(cat.id, [mock_image])
            
            # 测试图片大小超过限制
            mock_image.tell.return_value = 10 * 1024 * 1024  # 10MB
            with pytest.raises(ValueError):
                cat_service._handle_images(cat.id, [mock_image])
                
            # 测试非图片文件
            mock_image.content_type = "text/plain"
            with pytest.raises(ValueError):
                cat_service._handle_images(cat.id, [mock_image])
                
            # 清理
            db.session.delete(cat)
            db.session.delete(user)
            db.session.commit()

    def test_get_cat_stats(self, cat_service, app):
        """测试获取猫咪统计信息"""
        with app.app_context():
            # 创建测试用户和猫咪
            from app.models import User, Cat
            user = User(username="testuser_stats")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()
            
            # 创建多只猫咪
            cats = [
                Cat(name=f"Cat{i}", breed="Breed", age=i, user_id=user.id, is_adopted=(i % 2 == 0))
                for i in range(10)
            ]
            db.session.add_all(cats)
            db.session.commit()
            
            # 获取统计信息
            stats = cat_service.get_cat_stats()
            
            # 验证统计结果
            assert stats['total'] == 10
            assert stats['by_breed']['Breed'] == 10
            assert stats['by_adoption']['adopted'] == 5
            assert stats['by_adoption']['not_adopted'] == 5
            assert stats['age_distribution']['kitten'] == 1  # age=0
            assert stats['age_distribution']['young'] == 2  # age=1-2
            assert stats['age_distribution']['adult'] == 4  # age=3-6
            assert stats['age_distribution']['senior'] == 3  # age>=7
            
            # 清理
            for cat in cats:
                db.session.delete(cat)
            db.session.delete(user)
            db.session.commit()

    def test_validate_image_urls(self, cat_service, app):
        """测试验证和修复图片URL"""
        with app.app_context():
            # 创建测试用户和猫咪
            from app.models import User, Cat, CatImage
            user = User(username="testuser_images")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()
            
            # 创建猫咪
            cat = Cat(name="TestCatImages", breed="Test", age=2, description="Test", user_id=user.id)
            db.session.add(cat)
            db.session.commit()
            
            # 创建有问题的图片URL
            bad_image = CatImage(
                url="/static/uploads//static/uploads/bad.jpg",
                cat_id=cat.id
            )
            db.session.add(bad_image)
            db.session.commit()
            
            # 验证并修复URL
            invalid_urls = cat_service.validate_image_urls()
            
            # 验证结果
            assert len(invalid_urls) == 1
            assert invalid_urls[0][0] == "/static/uploads//static/uploads/bad.jpg"
            assert invalid_urls[0][1] == "/static/uploads/bad.jpg"
            
            # 清理
            db.session.delete(bad_image)
            db.session.delete(cat)
            db.session.delete(user)
            db.session.commit()

    def test_batch_update_failure(self, cat_service, app):
        """测试批量更新失败场景"""
        with app.app_context(), \
             patch('app.services.cat_service.current_app.logger.error') as mock_logger:
            from app.models import User, Cat
            user = User(username="testuser_batch_fail")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()
            
            cat = Cat(name="BatchUpdateCat", breed="Test", age=2, user_id=user.id)
            db.session.add(cat)
            db.session.commit()
            
            # 模拟数据库错误
            with patch('app.extensions.db.session.commit', side_effect=Exception("DB Error")):
                with pytest.raises(Exception):
                    cat_service.batch_update({cat.id: {'age': 3}})
                
                # 验证错误日志被记录
                mock_logger.assert_called_with("批量更新猫咪失败: DB Error")
            
            # 清理
            db.session.delete(cat)
            db.session.delete(user)
            db.session.commit()

    def test_create_cat_failure(self, cat_service, app):
        """测试创建猫咪失败场景"""
        with app.app_context(), \
             patch('app.services.cat_service.current_app.logger.error') as mock_logger:
            # 创建测试用户
            from app.models import User
            user = User(username="testuser_create_fail")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()
            
            # 模拟数据库错误
            with patch('app.extensions.db.session.commit', side_effect=Exception("DB Error")):
                with pytest.raises(Exception):
                    cat_service.create_cat(
                        user_id=user.id,
                        name="FailCat",
                        breed="Test",
                        age=2,
                        description="Test"
                    )
                
                # 验证错误日志被记录
                mock_logger.assert_called_with("创建猫咪失败: DB Error")
            
            # 清理
            db.session.delete(user)
            db.session.commit()

    # ... 其他测试方法保持不变 ...
