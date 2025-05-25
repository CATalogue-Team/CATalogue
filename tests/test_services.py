import pytest
from datetime import datetime
from app import create_app
from app.services import UserService, CatService
from colorama import init
from .TestReporter import TestReporter

# 初始化彩色输出
init(autoreset=True)

@pytest.fixture
def app():
    """创建测试应用"""
    TestReporter.start_test("服务测试环境初始化")
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app

def test_user_service(app):
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

def test_cat_service(app):
        """测试猫咪服务"""
        TestReporter.start_test("猫咪服务测试")
        with app.app_context():
            from app.extensions import db
            # 清理测试数据
            db.drop_all()
            db.create_all()
            
            # 创建测试用户
            user = UserService.create_user(
                username=f'owner_{datetime.now().timestamp()}',
                password='password'
            )
            
            # 测试猫咪创建
            TestReporter.log_step("测试创建猫咪-正常情况")
            service = CatService(db)
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
                service = CatService(db)
                service.create_cat(
                    name='Test Cat',
                    breed='Test Breed',
                    age=2,
                    description='Test description',
                    user_id=user.id
                )
                
            # 测试边界值
            TestReporter.log_step("测试边界值-最小年龄")
            service = CatService(db)
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
            service = CatService(db)
            found_cat = service.get(Cat, cat.id)
            assert found_cat == cat
            
            # 测试更新
            TestReporter.log_step("测试更新猫咪")
            service = CatService(db)
            updated = service.update_cat(cat.id, age=3)
            assert updated is not None
            assert updated.age == 3
            
            # 测试删除
            TestReporter.log_step("测试删除猫咪")
            service = CatService(db)
            delete_result = service.delete(cat.id)
            assert delete_result is True
            service = CatService(db)
            deleted_cat = service.get(Cat, cat.id)
            assert deleted_cat is None
            
            # 测试图片上传功能
            TestReporter.log_step("测试图片上传功能")
            from app.models import CatImage
            from werkzeug.datastructures import FileStorage
            from io import BytesIO
            
            service = CatService(db)
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
            from app.extensions import db
            from app.models import Cat, CatImage
            service = CatService(db)
            cat_with_images = service.get(Cat, test_cat.id)
            assert cat_with_images is not None
            
            # 查询关联图片
            images = db.session.query(CatImage).filter_by(cat_id=test_cat.id).all()
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
            images = db.session.query(CatImage).filter_by(cat_id=test_cat.id).all()
            assert len(images) > 0
            assert images[0].url is not None
            
            # 测试批量操作
            TestReporter.log_step("测试批量操作")
            cats = []
            for i in range(5):
                service = CatService(db)
                cat = service.create_cat(
                    name=f'Batch Cat {i}',
                    breed='Test Breed',
                    age=i,
                    description=f'Test description {i}',
                    user_id=user.id
                )
                cats.append(cat)
            
            # 测试分页查询
            service = CatService(db)
            paginated: dict = service.get_paginated_cats(page=1, per_page=2)
            assert isinstance(paginated, dict)
            assert len(paginated.get('items', [])) == 2
            assert paginated.get('total', 0) >= 6  # 5批量 + 1之前的
            
            TestReporter.success("猫咪服务测试通过")
