import pytest
from datetime import datetime
from app import create_app
from app.models import User, Cat, CatImage
from colorama import init
from .TestReporter import TestReporter

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
        TestReporter.test_step("创建用户")
        user = User(username=f'test_{datetime.now().timestamp()}')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # 验证密码
        TestReporter.test_step("验证密码")
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
        user = User(username=f'owner_{datetime.now().timestamp()}')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # 测试猫咪创建
        TestReporter.test_step("创建猫咪")
        cat = Cat(name='Test Cat', breed='Test Breed', 
                 age=2, description='Test description',
                 user_id=user.id)
        db.session.add(cat)
        db.session.commit()
        
        # 验证关系
        TestReporter.test_step("验证用户-猫咪关系")
        assert cat.owner == user
        assert cat in user.cats
        
        TestReporter.success("猫咪模型测试通过")

def test_cat_image_model(app):
    """测试猫咪图片模型"""
    TestReporter.start_test("猫咪图片模型测试")
    with app.app_context():
        from app.extensions import db
        db.create_all()
        
        # 创建测试数据
        user = User(username=f'owner_{datetime.now().timestamp()}')
        user.set_password('password')
        db.session.add(user)
        
        # 确保用户先提交
        db.session.commit()
        cat = Cat(name='Test Cat', user_id=user.id)
        db.session.add(cat)
        db.session.commit()
        
        # 测试图片创建
        TestReporter.test_step("创建猫咪图片")
        image = CatImage(url='test.jpg', cat_id=cat.id)
        db.session.add(image)
        db.session.commit()
        
        # 验证关系
        TestReporter.test_step("验证猫咪-图片关系")
        assert image.cat == cat
        assert image in cat.images
        
        TestReporter.success("猫咪图片模型测试通过")
