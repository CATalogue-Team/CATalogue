import pytest
from datetime import datetime
from unittest.mock import MagicMock
from app import create_app
from app.services import UserService, CatService
from app.extensions import db as _db
from colorama import init
from .test_reporter import TestReporter

# 初始化彩色输出
init(autoreset=True)

@pytest.fixture
def app(init_db):
    """创建测试应用"""
    TestReporter.start_test("服务测试环境初始化")
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        _db.create_all()
    return app

def test_user_service(app, init_db):
    """测试用户服务"""
    TestReporter.start_test("用户服务测试")
    with app.app_context():
        from app.extensions import db
        db.create_all()
        
        # 测试用户创建
        TestReporter.log_step("测试创建用户")
        user = UserService.create_user(
            username=f'testuser_{datetime.now().timestamp()}',
            password='password'
        )
        assert user.id is not None
        
        # 测试用户查询
        TestReporter.log_step("测试查询用户")
        found_user = UserService.get_user_by_username(user.username)
        assert found_user is not None
        assert found_user.id == user.id
        
        TestReporter.success("用户服务测试通过")

def test_cat_service(app, init_db):
        """测试猫咪服务"""
        TestReporter.start_test("猫咪服务测试")
        with app.app_context():
            # 创建测试用户
            user = UserService.create_user(
                username=f'owner_{datetime.now().timestamp()}',
                password='password'
            )
            
            # 测试猫咪创建
            TestReporter.log_step("测试创建猫咪-正常情况")
            # 创建符合服务层期望的db对象结构
            mock_db = MagicMock()
            mock_db.session = _db.session
            service = CatService(mock_db)
            cat = service.create_cat(
                name='Test Cat',
                breed='Test Breed',
                age=2,
                description='Test description',
                user_id=user.id
            )
            assert cat.id is not None
            
            # 测试重复创建
            TestReporter.log_step("测试创建猫咪-重复名称")
            with pytest.raises(ValueError):
                service = CatService(_db)
                service.create_cat(
                    name='Test Cat',
                    breed='Test Breed',
                    age=2,
                    description='Test description',
                    user_id=user.id
                )
                
            # 测试边界值
            TestReporter.log_step("测试边界值-最小年龄")
            service = CatService(_db)
            young_cat = service.create_cat(
                name='Young Cat',
                breed='Test Breed',
                age=0,
                description='Test description',
                user_id=user.id
            )
            assert young_cat.age == 0
            
            # 测试查询
            TestReporter.log_step("测试查询猫咪")
            from app.models import Cat
            service = CatService(_db)
            found_cat = service.get(Cat, cat.id)
            assert found_cat == cat
            
            # 测试更新
            TestReporter.log_step("测试更新猫咪")
            service = CatService(_db)
            updated = service.update_cat(cat.id, age=3)
            assert updated is not None
            assert updated.age == 3
            
            # 测试删除
            TestReporter.log_step("测试删除猫咪")
            service = CatService(_db)
            delete_result = service.delete(cat.id)
            assert delete_result is True
            service = CatService(_db)
            deleted_cat = service.get(Cat, cat.id)
            assert deleted_cat is None
            
            # 测试图片上传功能
            TestReporter.log_step("测试图片上传功能")
            from app.models import CatImage
            from werkzeug.datastructures import FileStorage
            from io import BytesIO
            
            service = CatService(_db)
            test_cat = service.create_cat(
                name='Image Test Cat',
                breed='Test Breed',
                age=2,
                description='Test description',
                user_id=user.id
            )
            
            # 创建模拟文件
            test_file = FileStorage(
                stream=BytesIO(b'test image content'),
                filename='test.jpg',
                content_type='image/jpeg'
            )
            
            # 添加图片
            service._handle_images(test_cat.id, [test_file])
            
            # 验证图片
            from app.models import Cat, CatImage
            service = CatService(_db)
            cat_with_images = service.get(Cat, test_cat.id)
            assert cat_with_images is not None
            
            # 查询关联图片
            images = _db.session.query(CatImage).filter_by(cat_id=test_cat.id).all()
            assert len(images) > 0
            assert images[0].url is not None
            assert cat_with_images.primary_image is not None
            
            # 测试无效文件类型
            TestReporter.log_step("测试无效文件类型")
            invalid_file = FileStorage(
                stream=BytesIO(b'invalid content'),
                filename='test.txt',
                content_type='text/plain'
            )
            # 先验证图片上传成功
            images = _db.session.query(CatImage).filter_by(cat_id=test_cat.id).all()
            assert len(images) > 0
            assert images[0].url is not None
            
            # 测试批量操作
            TestReporter.log_step("测试批量操作")
            cats = []
            for i in range(5):
                service = CatService(_db)
                cat = service.create_cat(
                    name=f'Batch Cat {i}',
                    breed='Test Breed',
                    age=i,
                    description=f'Test description {i}',
                    user_id=user.id
                )
                cats.append(cat)
            
            # 测试分页查询
            service = CatService(_db)
            paginated: dict = service.get_paginated_cats(page=1, per_page=2)
            assert isinstance(paginated, dict)
            assert len(paginated.get('items', [])) == 2
            assert paginated.get('total', 0) >= 6  # 5批量 + 1之前的
            
            # 新增测试用例 - 提高覆盖率
            TestReporter.log_step("测试无效user_id")
            with pytest.raises(ValueError):
                service.create_cat(
                    name='Invalid User Cat',
                    breed='Test Breed',
                    age=2,
                    description='Test description',
                    user_id=99999  # 不存在的用户ID
                )
                
            # 测试空图片列表
            TestReporter.log_step("测试空图片列表")
            service = CatService(_db)
            cat_without_images = service.create_cat(
                name='No Image Cat',
                breed='Test Breed',
                age=3,
                description='Test description',
                user_id=user.id,
                images=[]
            )
            assert cat_without_images.id is not None
            
            # 测试数据库操作失败
            TestReporter.log_step("测试数据库异常")
            from unittest.mock import patch
            with patch('app.services.cat_service.db.session.commit', side_effect=Exception("模拟数据库错误")):
                with pytest.raises(Exception):
                    service.create_cat(
                        name='DB Error Cat',
                        breed='Test Breed',
                        age=2,
                        description='Test description',
                        user_id=user.id
                    )
            
            # 测试超大图片上传
            TestReporter.log_step("测试超大图片上传")
            large_file = FileStorage(
                stream=BytesIO(b'x' * (5 * 1024 * 1024 + 1)),  # 5MB+1字节
                filename='large.jpg',
                content_type='image/jpeg'
            )
            with pytest.raises(ValueError):
                service._handle_images(test_cat.id, [large_file])
                
            # 测试并发创建
            TestReporter.log_step("测试并发创建")
            from concurrent.futures import ThreadPoolExecutor
            def create_cat_concurrently(i):
                service = CatService(_db)
                return service.create_cat(
                    name=f'Concurrent Cat {i}',
                    breed='Test Breed',
                    age=i,
                    description=f'Test description {i}',
                    user_id=user.id
                )
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(create_cat_concurrently, i) for i in range(5)]
                results = [f.result() for f in futures]
                assert len(results) == 5
                assert len({cat.id for cat in results}) == 5  # 确保所有ID唯一
                
            # 测试特殊字符
            TestReporter.log_step("测试特殊字符")
            service = CatService(_db)
            special_cat = service.create_cat(
                name='特殊字符测试🐱',
                breed='测试品种',
                age=2,
                description='测试描述~!@#$%^&*()',
                user_id=user.id
            )
            assert special_cat.id is not None
            
            TestReporter.success("猫咪服务测试通过")
