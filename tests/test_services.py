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
        TestReporter.test_step("测试创建用户")
        user = UserService.create_user(
            username=f'testuser_{datetime.now().timestamp()}',
            password='password'
        )
        assert user.id is not None
        
        # 测试用户查询
        TestReporter.test_step("测试查询用户")
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
            TestReporter.test_step("测试创建猫咪-正常情况")
            cat = CatService.create_cat(
                name='Test Cat',
                breed='Test Breed',
                age=2,
                description='Test description',
                user_id=user.id
            )
            assert cat.id is not None
            
            # 测试重复创建
            TestReporter.test_step("测试创建猫咪-重复名称")
            with pytest.raises(ValueError):
                CatService.create_cat(
                    name='Test Cat',
                    breed='Test Breed',
                    age=2,
                    description='Test description',
                    user_id=user.id
                )
                
            # 测试边界值
            TestReporter.test_step("测试边界值-最小年龄")
            young_cat = CatService.create_cat(
                name='Young Cat',
                breed='Test Breed',
                age=0,
                description='Test description',
                user_id=user.id
            )
            assert young_cat.age == 0
            
            # 测试查询
            TestReporter.test_step("测试查询猫咪")
            found_cat = CatService.get(cat.id)
            assert found_cat == cat
            
            # 测试更新
            TestReporter.test_step("测试更新猫咪")
            updated = CatService.update_cat(cat.id, age=3)
            assert updated is not None
            assert updated.age == 3
            
            # 测试删除
            TestReporter.test_step("测试删除猫咪")
            delete_result = CatService.delete(cat.id)
            assert delete_result is True
            deleted_cat = CatService.get(cat.id)
            assert deleted_cat is None
            
            # 测试图片上传功能
            TestReporter.test_step("测试图片上传功能")
            from app.models import CatImage
            test_cat = CatService.create_cat(
                name='Image Test Cat',
                breed='Test Breed',
                age=2,
                description='Test description',
                user_id=user.id
            )
            
            # 添加图片
            image_url = '/static/uploads/test.jpg'
            CatService._handle_images(test_cat.id, [image_url])
            
            # 验证图片
            cat_with_images = CatService.get(test_cat.id)
            assert len(cat_with_images.images) == 1
            assert cat_with_images.images[0].url == image_url
            assert cat_with_images.primary_image == image_url
            
            # 测试无效图片URL
            TestReporter.test_step("测试无效图片URL")
            with pytest.raises(ValueError):
                CatService._handle_images(test_cat.id, ["invalid_url"])
            
            # 测试批量操作
            TestReporter.test_step("测试批量操作")
            cats = []
            for i in range(5):
                cat = CatService.create_cat(
                    name=f'Batch Cat {i}',
                    breed='Test Breed',
                    age=i,
                    description=f'Test description {i}',
                    user_id=user.id
                )
                cats.append(cat)
            
            # 测试分页查询
            paginated = CatService.get_paginated_cats(page=1, per_page=2)
            assert len(paginated.items) == 2
            assert paginated.total == 6  # 5批量 + 1之前的
            
            TestReporter.success("猫咪服务测试通过")
