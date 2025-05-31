import pytest
from datetime import datetime
from typing import cast
from werkzeug.security import generate_password_hash
from app import create_app
from app.models import User, Cat, CatImage
from app.extensions import db
from colorama import init
from .test_reporter import TestReporter

# 初始化彩色输出
init(autoreset=True)

@pytest.fixture
def app():
    """创建测试应用"""
    TestReporter.start_test("模型测试环境初始化")
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app

def test_user_model(app):
    """测试用户模型"""
    TestReporter.start_test("用户模型测试")
    with app.app_context():
        from app.extensions import db
        db.create_all()
        
        # 测试用户创建
        TestReporter.log_step("创建用户")
        user = User()
        user.username = f'test_{datetime.now().timestamp()}'
        user.set_password('password')
        user.status = 'approved'
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        
        # 验证密码
        TestReporter.log_step("验证密码")
        assert user.check_password('password')
        assert not user.check_password('wrong')
        
        TestReporter.success("用户模型测试通过")

def test_cat_model(app):
    """测试猫咪模型"""
    TestReporter.start_test("猫咪模型测试")
    with app.app_context():
        from app.extensions import db
        db.create_all()
        
        # 创建测试用户
        user = User()
        user.username = f'owner_{datetime.now().timestamp()}'
        user.set_password('password')
        user.status = 'approved'
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        
        # 测试猫咪创建
        TestReporter.log_step("创建猫咪")
        cat = Cat()
        cat.name = 'Test Cat'
        cat.breed = 'Test Breed'
        cat.age = 2
        cat.description = 'Test description'
        cat.user_id = user.id
        db.session.add(cat)
        db.session.commit()
        db.session.refresh(cat)
        
        # 验证关系
        TestReporter.log_step("验证用户-猫咪关系")
        # type: ignore[attr-defined]
        assert cat.owner == user  # type: ignore[attr-defined]
        assert cat in user.cats  # type: ignore[operator]
        
        TestReporter.success("猫咪模型测试通过")

def test_cat_image_model(app):
    """测试猫咪图片模型"""
    TestReporter.start_test("猫咪图片模型测试")
    with app.app_context():
        from app.extensions import db
        db.create_all()
        
        # 创建测试数据
        user = User()
        user.username = f'owner_{datetime.now().timestamp()}'
        user.set_password('password')
        user.status = 'approved'
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        
        cat = Cat()
        cat.name = 'Test Cat'
        cat.user_id = user.id
        db.session.add(cat)
        db.session.commit()
        db.session.refresh(cat)
        
        # 测试图片创建
        TestReporter.log_step("创建猫咪图片")
        image = CatImage(url='test.jpg', cat_id=cat.id)
        db.session.add(image)
        db.session.commit()
        
        # 验证关系
        TestReporter.log_step("验证猫咪-图片关系")
        # type: ignore[attr-defined]
        assert image.cat == cat  # type: ignore[attr-defined]
        assert image in cat.images  # type: ignore[operator]
        
        TestReporter.success("猫咪图片模型测试通过")
