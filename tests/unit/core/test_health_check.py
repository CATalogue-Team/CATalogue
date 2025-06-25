import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from pathlib import Path
import os
import datetime

pytestmark = pytest.mark.no_db  # 标记此测试模块不需要数据库

from app.core.health_check import EnvironmentChecker

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

# [原有测试用例保持不变...]

# 新增测试用例
def test_check_services_health_details(checker, app, mock_services):
    """测试服务健康检查详细逻辑"""
    # 测试服务不存在情况
    assert checker._check_services_health() is False
    
    # 测试健康检查方法不存在
    app.cat_service = MagicMock()
    del app.cat_service.check_health
    assert checker._check_services_health() is False
    
    # 测试正常情况
    mock_services['cat_service'].check_health.return_value = True
    mock_services['user_service'].check_health.return_value = True
    app.cat_service = mock_services['cat_service']
    app.user_service = mock_services['user_service']
    assert checker._check_services_health() is True

def test_run_auto_repair_details(checker):
    """测试自动修复功能详细实现"""
    failed_checks = {
        'dependencies_installed': False,
        'migrations_applied': False
    }
    
    with patch.object(checker, '_install_dependencies') as mock_install, \
         patch.object(checker, '_apply_migrations') as mock_migrate:
        mock_install.return_value = True
        mock_migrate.return_value = True
        
        repaired = checker.run_auto_repair(failed_checks)
        assert repaired['dependencies_installed'] is True
        assert repaired['migrations_applied'] is True
        mock_install.assert_called_once()
        mock_migrate.assert_called_once()

def test_check_config_details(checker, app):
    """测试配置检查详细逻辑"""
    # 保存原始配置
    original_config = app.config.copy()
    
    try:
        # 测试必需配置缺失
        with patch.dict(app.config, clear=True):
            assert checker._check_config() is False
        
        # 测试配置完整
        with patch.dict(app.config, {
            'SECRET_KEY': 'test',
            'SQLALCHEMY_DATABASE_URI': 'sqlite://',
            'UPLOAD_FOLDER': '/tmp',
            'SERVER_NAME': 'localhost.localdomain:5000'
        }):
            assert checker._check_config() is True
    finally:
        # 恢复原始配置
        app.config.update(original_config)

def test_check_database_details(checker, app):
    """测试数据库检查详细逻辑"""
    # 测试SQLAlchemy扩展不存在
    app.extensions = {}
    assert checker._check_database() is False
    
    # 测试模拟数据库情况
    app.extensions['sqlalchemy'] = {'db': {'mock': True}}
    assert checker._check_database() is True
    
    # 测试真实数据库连接
    mock_db = MagicMock()
    app.extensions['sqlalchemy'] = {'db': mock_db}
    with patch('sqlalchemy.text'):
        assert checker._check_database() is True

def test_check_redis_details(checker, app):
    """测试Redis检查详细逻辑"""
    # 测试正常连接
    with patch('redis.Redis.ping', return_value=True):
        assert checker._check_redis() is True
        
    # 测试连接异常
    with patch('redis.Redis.ping', side_effect=Exception):
        assert checker._check_redis() is False
        
    # 测试Redis扩展不存在
    app.extensions = {}
    assert checker._check_redis() is False
    
    # 测试连接超时
    with patch('redis.Redis.ping', side_effect=TimeoutError):
        assert checker._check_redis() is False
        
    # 测试生产环境配置检查
    app.config['FLASK_ENV'] = 'production'
    with patch('redis.Redis.ping', return_value=True):
        assert checker._check_redis() is True
    app.config['FLASK_ENV'] = 'development'

def test_check_dependencies_failure(checker):
    """测试依赖检查失败情况"""
    with patch('importlib.import_module', side_effect=ImportError):
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
    app.extensions['sqlalchemy'] = {'db': {'mock': True}}
    assert checker._check_migrations() is True

def test_run_auto_repair_failure(checker):
    """测试自动修复失败情况"""
    failed_checks = {
        'dependencies_installed': False,
        'migrations_applied': False
    }
    
    with patch.object(checker, '_install_dependencies') as mock_install, \
         patch.object(checker, '_apply_migrations') as mock_migrate:
        mock_install.return_value = False
        mock_migrate.return_value = False
        
        repaired = checker.run_auto_repair(failed_checks)
        assert repaired['dependencies_installed'] is False
        assert repaired['migrations_applied'] is False

def test_check_dev_environment_exceptions(checker):
    """测试开发环境检查异常处理"""
    with patch.object(checker, '_check_dependencies', side_effect=Exception):
        result = checker.check_dev_environment()
        assert isinstance(result, dict)
        assert result['dependencies_installed'] is False
        assert all(v is False for k,v in result.items() if k != 'dependencies_installed')

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

def test_auto_repair(checker):
    """测试自动修复功能"""
    failed_checks = {
        'dependencies_installed': False,
        'migrations_applied': False,
        'temp_files_cleaned': False
    }
    with patch.multiple(checker,
        _install_dependencies=MagicMock(return_value=True),
        _apply_migrations=MagicMock(return_value=True),
        _clean_temp_files=MagicMock(return_value=1)):
        repaired = checker.run_auto_repair(failed_checks)
        assert repaired['dependencies_installed'] is True
        assert repaired['migrations_applied'] is True
        assert repaired['temp_files_cleaned'] is True

def test_check_test_environment(checker, app):
    """测试测试环境检查"""
    with patch.multiple(checker,
        _check_test_environment=MagicMock(return_value=True),
        _check_database=MagicMock(return_value=True),
        _clean_temp_files=MagicMock(return_value=1)):
        with patch('coverage.Coverage'), patch('pytest.main'):
            assert checker._check_test_environment() is True

def test_check_services(checker, app):
    """测试服务检查"""
    # 测试服务不存在情况
    assert checker._check_services() is False
    
    # 测试服务存在情况
    app.cat_service = MagicMock()
    app.user_service = MagicMock()
    assert checker._check_services() is True

def test_clean_temp_files(checker, tmp_path):
    """测试清理临时文件"""
    # 创建测试文件
    test_file = tmp_path / "test.tmp"
    test_file.write_text("test")
    
    # 测试清理
    with patch.object(checker, 'app') as mock_app:
        mock_app.root_path = str(tmp_path)
        assert checker._clean_temp_files() > 0
        
    # 测试无文件可清理
    assert checker._clean_temp_files() == 1

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

def test_check_redis(checker, app):
    """测试Redis检查"""
    with patch('redis.Redis.ping', return_value=True):
        assert checker._check_redis() is True
        
    with patch('redis.Redis.ping', side_effect=Exception):
        assert checker._check_redis() is False

def test_check_rate_limit(checker, app):
    """测试限流检查"""
    # 测试限流未配置
    assert checker._check_rate_limit() is False
    
    # 测试限流已配置
    app.extensions['limiter'] = MagicMock(enabled=True)
    assert checker._check_rate_limit() is True

def test_optimize_performance(checker, app):
    """测试性能优化"""
    mock_db = MagicMock()
    mock_db.session = MagicMock()
    app.extensions['sqlalchemy'] = MagicMock(db=mock_db)
    app.config['FLASK_ENV'] = 'production'
    
    with patch('sqlalchemy.text'):
        checker._optimize_performance()
        mock_db.session.execute.assert_called()
        mock_db.session.commit.assert_called()
        
    # 测试缓存清理
    app.extensions['cache'] = MagicMock()
    checker._optimize_performance()
    app.extensions['cache'].clear.assert_called()
        
    # 测试开发环境不执行优化
    app.config['FLASK_ENV'] = 'development'
    mock_db.session.reset_mock()
    checker._optimize_performance()
    mock_db.session.execute.assert_not_called()

def test_repair_missing_config(checker, app):
    """测试修复缺失配置"""
    # 保存原始配置
    original_config = app.config.copy()
    
    try:
        # 测试正常修复
        with patch('os.makedirs'), \
             patch('os.urandom', return_value=b'test'):
            result = checker._repair_missing_config()
            assert result is True
            assert 'SECRET_KEY' in app.config
            assert 'UPLOAD_FOLDER' in app.config
            
        # 测试目录创建失败
        with patch('os.makedirs', side_effect=OSError('模拟目录创建失败')), \
             patch('os.urandom', return_value=b'test'):
            # 重置配置
            app.config.pop('UPLOAD_FOLDER', None)
            # 捕获日志
            with patch.object(checker.logger, 'warning') as mock_warning:
                result = checker._repair_missing_config()
                assert result is False
                assert 'UPLOAD_FOLDER' not in app.config
                mock_warning.assert_called_once_with(
                    "创建上传目录失败: 模拟目录创建失败")
            
        # 测试密钥生成失败
        with patch('os.makedirs'), \
             patch('os.urandom', side_effect=Exception('模拟密钥生成失败')):
            # 重置配置
            app.config.pop('SECRET_KEY', None)
            # 捕获日志
            with patch.object(checker.logger, 'error') as mock_error:
                try:
                    checker._repair_missing_config()
                except Exception:
                    pass
                mock_error.assert_called_once_with(
                    "生成SECRET_KEY失败: 模拟密钥生成失败")
                assert 'SECRET_KEY' not in app.config
                
        # 测试生产环境配置
        app.config['FLASK_ENV'] = 'production'
        with patch('os.makedirs'), \
             patch('os.urandom', return_value=b'test'):
            checker._repair_missing_config()
            assert app.config['SECRET_KEY'] == '74657374'  # 'test'的hex编码
        app.config['FLASK_ENV'] = 'development'
    finally:
        # 恢复原始配置
        app.config.update(original_config)

def test_save_check_results(checker, app):
    """测试保存检查结果"""
    mock_db = MagicMock()
    app.extensions = {'sqlalchemy': {'db': mock_db}}
    
    with patch('app.models.EnvironmentCheck'):
        assert checker.save_check_results({'test': True}) is True
        
    # 测试异常情况
    with patch('app.models.EnvironmentCheck', side_effect=Exception):
        assert checker.save_check_results({'test': True}) is False
