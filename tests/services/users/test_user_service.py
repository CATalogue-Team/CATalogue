import pytest
from datetime import datetime
from unittest.mock import patch
from app.models import User
from app.services import UserService
from tests.core.factories import UserFactory
from tests.services.users.test_reporter import TestReporter

@pytest.mark.service
@pytest.mark.user
class TestUserService:
    """UserService测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前的初始化"""
        self.reporter = TestReporter()
        
    def test_create_user(self, user_service, test_user_data, app):
        """测试创建用户"""
        with app.app_context():
            self.reporter.start_test("用户创建测试")
            
            # 测试正常创建
            self.reporter.log_step("测试正常创建")
            user = user_service.create_user(**test_user_data)
            assert user.id is not None
            assert user.username == test_user_data['username']
            
            # 测试重复用户名
            self.reporter.log_step("测试重复用户名")
            with pytest.raises(ValueError):
                user_service.create_user(**test_user_data)
                
            self.reporter.success("用户创建测试通过")
            
    def test_get_user(self, user_service, test_user_data, app):
        """测试查询用户"""
        with app.app_context():
            self.reporter.start_test("用户查询测试")
            
            # 创建测试用户
            user = UserFactory().make_instance(**test_user_data)
            
            # 测试查询
            self.reporter.log_step("测试用户名查询")
            found = user_service.get_user_by_username(user.username)
            assert found.id == user.id
            
            # 测试不存在的用户
            self.reporter.log_step("测试不存在的用户")
            assert user_service.get_user_by_username("nonexistent") is None
            
            self.reporter.success("用户查询测试通过")
