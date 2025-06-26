import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from pathlib import Path
import os
import datetime

from app.core.environment_checker import EnvironmentChecker

@pytest.fixture
def mock_services():
    """模拟服务健康检查"""
    cat_service = MagicMock()
    user_service = MagicMock()
    return {
        'cat_service': cat_service,
        'user_service': user_service
    }

@pytest.fixture
def app():
    """创建测试应用"""
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'UPLOAD_FOLDER': '/tmp/test_uploads',
        'FLASK_ENV': 'development',
        'SERVER_NAME': 'localhost.localdomain:5000'
    })
    return app

@pytest.fixture
def checker(app):
    """创建EnvironmentChecker实例"""
    return EnvironmentChecker(app)

def test_check_services_health_details(checker, app, mock_services):
    """测试服务健康检查详细逻辑"""
    # 测试服务不存在情况
    assert checker._check_services_health() is False
    
    # 测试健康检查方法不存在
    app.cat_service = MagicMock()
    assert checker._check_services_health() is False
    
    # 测试正常情况
    mock_services['cat_service'].check_health = MagicMock(return_value=True)
    mock_services['user_service'].check_health = MagicMock(return_value=True)
    app.cat_service = mock_services['cat_service']
    app.user_service = mock_services['user_service']
    assert checker._check_services_health() is True

def test_run_auto_repair_details(checker):
    """测试自动修复功能详细实现"""
    failed_checks = {
        'db_connected': True,
        'migrations_applied': True
    }

    with patch.object(checker, '_repair_database', return_value=True) as mock_db, \
         patch.object(checker, '_check_migrations', return_value=True) as mock_migrate:
        repaired = checker.run_auto_repair(failed_checks)
        assert repaired['db_connected'] is True
        assert repaired['migrations_applied'] is True
        mock_db.assert_called_once()
        mock_migrate.assert_called_once()

def test_check_config_details(checker, app):
    """测试配置检查详细逻辑"""
    # 测试必需配置缺失
    with patch.dict(app.config, clear=True):
        assert checker._check_config() is False
    
    # 测试配置完整
    with patch.dict(app.config, {
        'SECRET_KEY': 'test',
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',
        'UPLOAD_FOLDER': '/tmp'
    }):
        assert checker._check_config() is True

def test_check_database_details(checker, app):
    """测试数据库检查详细逻辑"""
    # 测试SQLAlchemy扩展不存在
    app.extensions = {}
    assert checker._check_database() is False
    
    # 测试模拟数据库情况
    mock_db = MagicMock()
    mock_db.session = MagicMock()
    app.extensions['sqlalchemy'] = {'db': mock_db}
    with patch('sqlalchemy.text'):
        assert checker._check_database() is True

def test_check_dependencies_failure(checker):
    """测试依赖检查失败情况"""
    with patch('pkg_resources.get_distribution', side_effect=Exception):
        assert checker._check_dependencies() is False

def test_check_migrations_failure(checker, app):
    """测试迁移检查失败情况"""
    mock_db = MagicMock()
    app.extensions['sqlalchemy'] = {'db': mock_db}
    with patch('sqlalchemy.text'), \
         patch.object(mock_db.session, 'execute', side_effect=Exception):
        assert checker._check_migrations() is False
        
    # 测试SQLAlchemy扩展不存在
    app.extensions = {}
    assert checker._check_migrations() is False
    
    # 测试模拟数据库情况
    app.extensions['sqlalchemy'] = {'db': mock_db}
    with patch('sqlalchemy.text'):
        assert checker._check_migrations() is True

def test_run_auto_repair_failure(checker):
    """测试自动修复失败情况"""
    failed_checks = {
        'db_connected': True,
        'migrations_applied': True
    }
    
    with patch.object(checker, '_repair_database', return_value=False) as mock_db, \
         patch.object(checker, '_check_migrations', return_value=False) as mock_migrate:
        repaired = checker.run_auto_repair(failed_checks)
        assert repaired['db_connected'] is False
        assert repaired['migrations_applied'] is False

def test_check_dev_environment_exceptions(checker):
    """测试开发环境检查异常处理"""
    with patch.object(checker, '_check_dependencies', side_effect=Exception):
        result = checker.check_dev_environment()
        assert isinstance(result, dict)
        assert result['dependencies_installed'] is False

def test_check_prod_environment(checker, app):
    """测试生产环境检查"""
    app.config['FLASK_ENV'] = 'production'
    with patch.multiple(checker,
        _check_database=MagicMock(return_value=True),
        _check_storage=MagicMock(return_value=True),
        _check_security=MagicMock(return_value=True),
        _check_backups=MagicMock(return_value=True),
        _check_performance=MagicMock(return_value=True)):
        result = checker.check_prod_environment()
        assert isinstance(result, dict)
        assert all(result.values())

def test_clean_temp_files(checker, tmp_path):
    """测试清理临时文件"""
    # 创建测试文件
    test_file = tmp_path / "test.tmp"
    test_file.write_text("test")
    
    # 测试清理
    with patch.object(checker, 'app') as mock_app:
        mock_app.root_path = str(tmp_path)
        assert checker._clean_temp_files() == 1
        
    # 测试无文件可清理
    assert checker._clean_temp_files() == 0

def test_validate_urls(checker):
    """测试URL验证"""
    with patch('app.core.image_url_validator.validate_and_fix_image_urls') as mock_validate:
        mock_validate.return_value = True
        assert checker._validate_urls() is True
        
    with patch('app.core.image_url_validator.validate_and_fix_image_urls', side_effect=Exception):
        assert checker._validate_urls() is False

def test_check_performance(checker, app):
    """测试性能检查"""
    # 测试开发环境
    app.config['FLASK_ENV'] = 'development'
    with patch.dict(app.config, {
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'pool_pre_ping': True,
            'pool_recycle': 3600
        }
    }):
        assert checker._check_performance() is True
    
    # 测试生产环境
    app.config['FLASK_ENV'] = 'production'
    with patch.dict(app.config, {
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'pool_pre_ping': True,
            'pool_recycle': 3600
        },
        'TEMPLATES_AUTO_RELOAD': False
    }):
        assert checker._check_performance() is True
        
    # 测试失败情况
    with patch.dict(app.config, {
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'pool_pre_ping': False,
            'pool_recycle': 4000
        }
    }):
        assert checker._check_performance() is False

def test_save_check_results(checker, app):
    """测试保存检查结果"""
    result = checker.save_check_results({'test': True})
    assert result is True
    assert 'LAST_ENV_CHECK' in app.config
    
    # 测试异常情况
    with patch.object(checker, 'app') as mock_app:
        mock_app.config = {}
        result = checker.save_check_results({'test': True})
        assert result is False
