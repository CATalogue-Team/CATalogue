import os
import pytest
from app.config import Config, TestingConfig
from dotenv import load_dotenv

class TestConfig:
    def test_config_init(self):
        """测试配置类初始化"""
        config = Config()
        assert hasattr(config, 'SECRET_KEY')
        assert hasattr(config, 'SQLALCHEMY_DATABASE_URI')

    def test_default_values(self, monkeypatch):
        """测试默认值"""
        # 临时移除.env文件影响
        monkeypatch.delenv('SECRET_KEY', raising=False)
        monkeypatch.delenv('DATABASE_URL', raising=False)
        
        config = Config()
        assert config.SECRET_KEY == 'dev-secret-key-123'
        assert 'sqlite:///' in config.SQLALCHEMY_DATABASE_URI

    def test_env_override(self, monkeypatch):
        """测试环境变量覆盖"""
        monkeypatch.setenv('SECRET_KEY', 'test-secret')
        monkeypatch.setenv('DATABASE_URL', 'sqlite:///test.db')
        
        config = Config()
        assert config.SECRET_KEY == 'test-secret'
        assert config.SQLALCHEMY_DATABASE_URI == 'sqlite:///test.db'

class TestTestingConfig:
    def test_testing_config(self):
        """测试测试环境配置"""
        config = TestingConfig()
        assert config.TESTING is True
        assert config.SQLALCHEMY_DATABASE_URI == 'sqlite:///:memory:'
        assert config.CACHE_TYPE == 'NullCache'
