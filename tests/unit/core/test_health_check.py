import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from pathlib import Path
import os

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
        'UPLOAD_FOLDER': '/tmp/test_uploads',
        'FLASK_ENV': 'development'
    })
    return app

@pytest.fixture
def checker(app):
    """创建EnvironmentChecker实例"""
    return EnvironmentChecker(app)

class TestEnvironmentChecker:
    def test_check_dev_environment_success(self, checker, app):
        """测试开发环境检查成功情况"""
        with patch.object(checker, '_check_test_environment', return_value=True), \
             patch.object(checker, '_check_database', return_value=True), \
             patch.object(checker, '_clean_temp_files', return_value=1), \
             patch.object(checker, '_validate_urls', return_value=True), \
             patch.object(checker, '_check_config', return_value=True), \
             patch.object(checker, '_check_dependencies', return_value=True), \
             patch.object(checker, '_check_migrations', return_value=True), \
             patch.object(checker, '_check_routes', return_value=True), \
             patch.object(checker, '_check_services_health', return_value=True):
            
            results = checker.check_dev_environment()
            assert all(results.values())

    def test_check_prod_environment_success(self, checker, app):
        """测试生产环境检查成功情况"""
        app.config['FLASK_ENV'] = 'production'
        with patch.object(checker, '_check_database', return_value=True), \
             patch.object(checker, '_check_storage', return_value=True), \
             patch.object(checker, '_check_security', return_value=True), \
             patch.object(checker, '_check_backups', return_value=True), \
             patch.object(checker, '_check_performance', return_value=True):
            
            results = checker.check_prod_environment()
            assert all(results.values())

    def test_check_database_success(self, checker, app):
        """测试数据库检查成功"""
        mock_db = MagicMock()
        app.extensions['sqlalchemy'] = {'db': mock_db}
        
        with patch('sqlalchemy.text') as mock_text:
            mock_db.session.execute.return_value = None
            assert checker._check_database() is True

    def test_check_database_failure(self, checker, app):
        """测试数据库检查失败"""
        app.extensions['sqlalchemy'] = {}
        assert checker._check_database() is False

    def test_clean_temp_files(self, checker, tmp_path):
        """测试清理临时文件"""
        test_file = tmp_path / "test.tmp"
        test_file.touch()
        
        with patch('app.core.health_check.Path', return_value=tmp_path):
            result = checker._clean_temp_files()
            assert result == 1  # 表示有文件被清理

    def test_check_services_health(self, checker, app, mock_services):
        """测试服务健康检查成功"""
        mock_services['cat_service'].check_health.return_value = True
        mock_services['user_service'].check_health.return_value = True
        
        app.cat_service = mock_services['cat_service']
        app.user_service = mock_services['user_service']
        
        assert checker._check_services_health() is True

    def test_check_services_health_failure(self, checker, app, mock_services):
        """测试服务健康检查失败"""
        mock_services['cat_service'].check_health.return_value = False
        mock_services['user_service'].check_health.return_value = True
        
        app.cat_service = mock_services['cat_service']
        app.user_service = mock_services['user_service']
        
        assert checker._check_services_health() is False

    def test_run_auto_repair(self, checker):
        """测试自动修复功能成功"""
        failed_checks = {
            'dependencies_installed': False,
            'migrations_applied': False,
            'temp_files_cleaned': False
        }
        
        with patch.object(checker, '_install_dependencies'), \
             patch.object(checker, '_apply_migrations'), \
             patch.object(checker, '_clean_temp_files', return_value=1):
            
            repaired = checker.run_auto_repair(failed_checks)
            assert repaired['dependencies_installed'] is True
            assert repaired['migrations_applied'] is True
            assert repaired['temp_files_cleaned'] is True

    def test_run_auto_repair_failure(self, checker):
        """测试自动修复功能失败"""
        failed_checks = {
            'dependencies_installed': False,
            'migrations_applied': False,
            'temp_files_cleaned': False
        }
        
        with patch.object(checker, '_install_dependencies', side_effect=Exception), \
             patch.object(checker, '_apply_migrations', side_effect=Exception), \
             patch.object(checker, '_clean_temp_files', return_value=0):
            
            repaired = checker.run_auto_repair(failed_checks)
            assert repaired['dependencies_installed'] is False
            assert repaired['migrations_applied'] is False
            assert repaired['temp_files_cleaned'] is True  # clean_temp_files在没有文件清理时返回1(True)

    def test_check_database_exception(self, checker, app):
        """测试数据库检查异常情况"""
        mock_db = MagicMock()
        app.extensions['sqlalchemy'] = {'db': mock_db}
        
        with patch('sqlalchemy.text') as mock_text:
            mock_db.session.execute.side_effect = Exception("DB Error")
            assert checker._check_database() is False
            
    def test_check_database_no_sqlalchemy(self, checker, app):
        """测试SQLAlchemy扩展不存在的情况"""
        app.extensions = {}
        assert checker._check_database() is False
        
    def test_check_test_environment_coverage_error(self, checker):
        """测试覆盖率报告生成失败情况"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('coverage.Coverage') as mock_cov, \
             patch('pytest.main', return_value=0):
            mock_cov.return_value.json_report.side_effect = Exception("Coverage Error")
            assert checker._check_test_environment() is False

    def test_register_cli_commands(self, checker, app):
        """测试CLI命令注册"""
        with patch('click.command') as mock_command:
            checker.register_cli_commands()
            assert mock_command.called
            assert hasattr(app, 'cli')

    def test_check_environment_variables(self, checker, app):
        """测试环境变量检查"""
        with patch.dict('os.environ', {'FLASK_ENV': 'development'}), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('coverage.Coverage'), \
             patch('pytest.main', return_value=0):
            assert checker._check_test_environment() is True

    def test_check_environment_variables_failure(self, checker, app):
        """测试环境变量检查失败"""
        with patch.dict('os.environ', {'FLASK_ENV': 'production'}):
            assert checker._check_test_environment() is False

    def test_check_redis_connection(self, checker, app):
        """测试Redis连接检查"""
        with patch('redis.Redis.ping', return_value=True):
            assert checker._check_redis() is True

    def test_check_redis_connection_failure(self, checker, app):
        """测试Redis连接检查失败"""
        with patch('redis.Redis.ping', side_effect=Exception):
            assert checker._check_redis() is False

    def test_environment_initialization(self, app):
        """测试环境检查器初始化"""
        checker = EnvironmentChecker(app)
        assert checker.app == app
        assert checker.logger.name == 'app.core.health_check'

    def test_check_database_details(self, checker, app):
        """测试数据库详细检查"""
        mock_db = MagicMock()
        app.extensions['sqlalchemy'] = {'db': mock_db}
        
        with patch('sqlalchemy.text') as mock_text:
            # 测试生产环境性能检查
            app.config['FLASK_ENV'] = 'production'
            assert checker._check_database() is True
            
            # 测试模拟数据库情况
            app.extensions['sqlalchemy'] = {'db': {'mock': True}}
            assert checker._check_database() is True

    def test_check_services_details(self, checker, app, mock_services):
        """测试服务健康检查详细逻辑"""
        mock_services['cat_service'].check_health.return_value = True
        mock_services['user_service'].check_health.return_value = True
        
        app.cat_service = mock_services['cat_service']
        app.user_service = mock_services['user_service']
        
        # 测试服务不存在情况
        del app.cat_service
        assert checker._check_services_health() is False
        
        # 测试健康检查方法不存在
        app.cat_service = MagicMock()
        del app.cat_service.check_health  # 确保没有check_health方法
        assert checker._check_services_health() is False

    def test_check_test_environment_exception(self, checker):
        """测试测试环境检查异常情况"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('coverage.Coverage') as mock_cov, \
             patch('pytest.main', side_effect=Exception("Test Error")):
            mock_cov.return_value.start.side_effect = Exception("Coverage Error")
            assert checker._check_test_environment() is False
            
    def test_check_test_environment_logging(self, checker):
        """测试测试环境检查日志记录"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('coverage.Coverage'), \
             patch('pytest.main', return_value=0), \
             patch.object(checker.logger, 'info') as mock_logger:
            checker._check_test_environment()
            assert mock_logger.called
            
    def test_auto_repair_details(self, checker):
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

    # 新增测试用例
    def test_check_storage_success(self, checker, tmp_path):
        """测试存储检查成功"""
        test_file = tmp_path / ".write_test"
        test_file.touch()
        
        with patch('app.core.health_check.Path', return_value=tmp_path):
            assert checker._check_storage() is True

    def test_check_storage_failure(self, checker, tmp_path):
        """测试存储检查失败"""
        with patch('app.core.health_check.Path', return_value=tmp_path), \
             patch('pathlib.Path.touch', side_effect=PermissionError):
            assert checker._check_storage() is False

    def test_check_config_missing_keys(self, checker, app):
        """测试配置检查缺少必要键"""
        app.config = {
            'SERVER_NAME': 'localhost',
            'APPLICATION_ROOT': '/',
            'PREFERRED_URL_SCHEME': 'http'
        }
        assert checker._check_config() is False

    def test_check_dependencies_complex(self, checker, app):
        """测试复杂依赖检查场景"""
        with patch('importlib.metadata.requires', return_value=["flask>=2.0.0"]), \
             patch('importlib.metadata.PackageNotFoundError'):
            assert checker._check_dependencies() is True

    def test_check_dependencies_failure(self, checker, app):
        """测试依赖检查失败"""
        with patch('importlib.metadata.requires', side_effect=ImportError):
            assert checker._check_dependencies() is False

    def test_check_performance_production(self, checker, app):
        """测试生产环境性能检查"""
        app.config['FLASK_ENV'] = 'production'
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 1800
        }
        app.config['TEMPLATES_AUTO_RELOAD'] = False
        assert checker._check_performance() is True

    def test_check_performance_development(self, checker, app):
        """测试开发环境性能检查"""
        app.config['FLASK_ENV'] = 'development'
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,  # 开发环境也建议启用pool_pre_ping
            'pool_recycle': 3600
        }
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        app.config['DEBUG'] = True
        with patch.object(checker, '_check_database', return_value=True), \
             patch.object(checker, '_check_redis', return_value=True):
            assert checker._check_performance() is True
