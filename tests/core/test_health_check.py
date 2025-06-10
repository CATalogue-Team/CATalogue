import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify

from app.core.health_check import EnvironmentChecker

@pytest.fixture
def client():
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestEnvironmentChecker:
    def test_check_dev_environment(self):
        """测试开发环境检查"""
        app = Flask(__name__)
        checker = EnvironmentChecker(app)
        
        with patch.object(checker, '_check_database', return_value=True), \
             patch.object(checker, '_check_test_environment', return_value=True), \
             patch.object(checker, '_clean_temp_files', return_value=1), \
             patch.object(checker, '_validate_urls', return_value=True), \
             patch.object(checker, '_check_config', return_value=True), \
             patch.object(checker, '_check_dependencies', return_value=True), \
             patch.object(checker, '_check_migrations', return_value=True), \
             patch.object(checker, '_check_routes', return_value=True), \
             patch.object(checker, '_check_services_health', return_value=True):
            
            results = checker.check_dev_environment()
            assert all(results.values())

    def test_check_prod_environment(self):
        """测试生产环境检查"""
        app = Flask(__name__)
        checker = EnvironmentChecker(app)
        
        with patch.object(checker, '_check_database', return_value=True), \
             patch.object(checker, '_check_storage', return_value=True), \
             patch.object(checker, '_check_security', return_value=True), \
             patch.object(checker, '_check_backups', return_value=True), \
             patch.object(checker, '_check_performance', return_value=True):
            
            results = checker.check_prod_environment()
            assert all(results.values())

    def test_save_check_results(self):
        """测试保存检查结果"""
        app = Flask(__name__)
        app.extensions = {
            'sqlalchemy': {
                'db': MagicMock()
            }
        }
        checker = EnvironmentChecker(app)
        
        mock_results = {
            'db_connected': True,
            'storage_writable': True
        }
        
        with patch('app.models.EnvironmentCheck'):
            app.extensions['sqlalchemy']['db'].session.commit.return_value = True
            assert checker.save_check_results(mock_results) is True

    def test_run_auto_repair(self):
        """测试自动修复功能"""
        app = Flask(__name__)
        checker = EnvironmentChecker(app)
        
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

    def test_check_failures(self):
        """测试检查失败的情况"""
        app = Flask(__name__)
        checker = EnvironmentChecker(app)
        
        with patch.object(checker, '_check_database', return_value=False), \
             patch.object(checker, '_check_test_environment', return_value=False):
            
            results = checker.check_dev_environment()
            assert results['db_ready'] is False
            assert results['test_ready'] is False

    def test_exception_handling(self):
        """测试异常处理"""
        app = Flask(__name__)
        app.extensions = {
            'sqlalchemy': {
                'db': MagicMock()
            }
        }
        checker = EnvironmentChecker(app)
        
        # 测试_check_database方法本身的异常处理
        with patch('sqlalchemy.text'):
            db = app.extensions['sqlalchemy']['db']
            db.session.execute.side_effect = Exception("DB error")
            assert checker._check_database() is False

    def test_production_checks(self):
        """测试生产环境特定检查"""
        app = Flask(__name__)
        app.config['FLASK_ENV'] = 'production'
        checker = EnvironmentChecker(app)
        
        with patch.object(checker, '_check_database', return_value=True), \
             patch.object(checker, '_check_performance', return_value=True):
            
            results = checker.check_prod_environment()
            assert results['performance_optimized'] is True

    def test_cli_commands(self):
        """测试CLI命令"""
        app = Flask(__name__)
        app.cli = MagicMock()
        checker = EnvironmentChecker(app)
        
        checker.register_cli_commands()
        assert app.cli.add_command.called

    def test_redis_connection(self):
        """测试Redis连接检查"""
        app = Flask(__name__)
        app.config['FLASK_ENV'] = 'production'
        checker = EnvironmentChecker(app)
        
        with patch('redis.Redis.ping', return_value=True):
            assert checker._check_redis() is True
            
        with patch('redis.Redis.ping', side_effect=Exception("Redis error")):
            assert checker._check_redis() is False

    def test_database_performance(self):
        """测试数据库性能检查"""
        app = Flask(__name__)
        app.config['FLASK_ENV'] = 'production'
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_size': 5}
        app.extensions = {
            'sqlalchemy': {
                'db': MagicMock()
            }
        }
        checker = EnvironmentChecker(app)
        
        # 模拟基础连接检查通过
        with patch.object(checker.app.extensions['sqlalchemy']['db'].session, 
                         'execute', return_value=MagicMock()):
            # 生产环境性能检查
            assert checker._check_database() is True
            
        # 模拟基础连接检查失败
        with patch.object(checker.app.extensions['sqlalchemy']['db'].session,
                         'execute', side_effect=Exception("DB error")):
            assert checker._check_database() is False
            
        # 模拟无SQLAlchemy扩展
        app.extensions = {}
        assert checker._check_database() is False

    def test_rate_limit_config(self):
        """测试限流配置检查"""
        app = Flask(__name__)
        app.extensions = {
            'limiter': MagicMock(enabled=True)
        }
        checker = EnvironmentChecker(app)
        
        # 测试启用状态
        assert checker._check_rate_limit() is True
        
        # 测试禁用状态
        app.extensions['limiter'].enabled = False
        assert checker._check_rate_limit() is False
        
        # 测试无limiter扩展
        app.extensions = {}
        assert checker._check_rate_limit() is False
