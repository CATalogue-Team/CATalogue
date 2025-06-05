import pytest
from datetime import datetime
from unittest.mock import patch
from app.models import User
from app.services import UserService
from app.extensions import db
from tests.shared.factories.user import UserFactory
from tests.services.users.test_reporter import TestReporter

@pytest.mark.service
@pytest.mark.user
class TestUserService:
    """UserService测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前的初始化"""
        self.reporter = TestReporter()
        
    def test_create_user(self, user_service, app):
        """测试创建用户"""
        with app.app_context():
            self.reporter.start_test("用户创建测试")

            # 重置测试数据库
            from app.models import Cat, User
            db.session.rollback()
            
            # 删除所有测试相关数据
            db.session.query(Cat).delete()
            db.session.query(User).filter(
                User.username.in_(["testuser", "testuser_concurrent"])
            ).delete()
            db.session.commit()
            
            # 确保数据库干净
            assert db.session.query(User).filter_by(username="testuser").first() is None

            # 测试正常创建
            self.reporter.log_step("测试正常创建")
            user = user_service.create_user(username="testuser", password="testpassword")
            assert user.id is not None
            assert user.username == "testuser"
            
            # 测试重复用户名
            self.reporter.log_step("测试重复用户名")
            with pytest.raises(ValueError):
                user_service.create_user(username="testuser", password="testpassword")
                
            # 清理测试数据
            cats = db.session.query(Cat).filter_by(user_id=user.id).all()
            for cat in cats:
                db.session.delete(cat)
            db.session.delete(user)
            db.session.commit()
            
            self.reporter.success("用户创建测试通过")
            
    def test_get_user(self, user_service, app):
        """测试查询用户"""
        with app.app_context():
            self.reporter.start_test("用户查询测试")

            # 创建测试用户
            user = UserFactory().make_instance(username="testuser")
            db.session.add(user)
            db.session.commit()
            user.set_password("testpassword")
            db.session.commit()
            
            # 测试查询
            self.reporter.log_step("测试用户名查询")
            found = user_service.get_user_by_username(user.username)
            assert found.id == user.id
            
            # 测试不存在的用户
            self.reporter.log_step("测试不存在的用户")
            assert user_service.get_user_by_username("nonexistent") is None
            
            self.reporter.success("用户查询测试通过")
