from typing import Optional
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from tests.test_client import CustomTestClient
from .TestReporter import TestReporter
from tests.core.factories import UserFactory, CatFactory

class BaseTest:
    """基础测试类"""
    
    def __init__(self):
        self._app: Optional[Flask] = None
        self._db: Optional[SQLAlchemy] = None 
        self._client: Optional[CustomTestClient] = None
        self._response_wrapper = TestReporter

    def setup(self, app: Flask, database: SQLAlchemy, test_client: CustomTestClient):
        """测试初始化"""
        if not app or not database or not test_client:
            raise ValueError("Missing required setup parameters")
            
        self._app = app
        self._db = database
        self._client = test_client
        self._client.response_wrapper = self._response_wrapper
        
        # 确保数据库表存在
        with self._app.app_context():
            self._db.create_all()
        
    @property
    def app(self) -> Flask:
        if not self._app:
            raise RuntimeError("App not initialized")
        return self._app
        
    @property 
    def db(self) -> SQLAlchemy:
        if not self._db:
            raise RuntimeError("Database not initialized")
        return self._db
        
    @property
    def client(self) -> CustomTestClient:
        if not self._client:
            raise RuntimeError("Client not initialized")
        return self._client

    def create_test_user(self, **kwargs):
        """创建测试用户"""
        with self.app.app_context():
            user = UserFactory(**kwargs)
            self.db.session.add(user)
            self.db.session.commit()
            self.db.session.refresh(user)
            return user

    def create_test_cat(self, **kwargs):
        """创建测试猫咪"""
        with self.app.app_context():
            # 确保有user_id
            if 'user_id' not in kwargs:
                user = self.create_test_user()
                kwargs['user_id'] = user.id
            cat = CatFactory(**kwargs)
            self.db.session.add(cat)
            self.db.session.commit()
            self.db.session.refresh(cat)
            return cat

    def login(self, username='testuser', password='password'):
        """测试登录"""
        user = self.create_test_user(
            username=username,
            password=password
        )
        response = self.client.post('/login', json={
            'username': username,
            'password': password
        })
        if not isinstance(response, dict) or 'data' not in response:
            raise ValueError("Login failed - invalid response format")
        return response['data']['access_token'], user
