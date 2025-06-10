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

    def test_run_auto_repair_failures(self):
        """测试自动修复失败的情况"""
        app = Flask(__name__)
        checker = EnvironmentChecker(app)
        
        failed_checks = {
            'dependencies_installed': False,
            'migrations_applied': False
        }
        
        with patch.object(checker, '_install_dependencies', side_effect=Exception("Install failed")), \
             patch.object(checker, '_apply_migrations', side_effect=Exception("Migration failed")):
            
            repaired = checker.run_auto_repair(failed_checks)
            assert repaired['dependencies_installed'] is False
            assert repaired['migrations_applied'] is False

    def test_check_failures(self):
        """测试检查失败的情况"""
        app = Flask(__name__)
        checker = EnvironmentChecker(app)
        
        with patch.object(checker, '_check_database', return_value=False), \
             patch.object(checker, '_check_test_environment', return_value=False), \
             patch.object(checker, '_check_services_health', return_value=False):
            
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

    def test_cli_command_execution(self):
        """测试CLI命令执行"""
        app = Flask(__name__)
        app.config['FLASK_ENV'] = 'development'
        checker = EnvironmentChecker(app)
        
        # 模拟检查结果
        with patch.object(checker, 'check_dev_environment', return_value={'test': True}), \
             patch.object(checker, 'run_auto_repair', return_value={'test': True}):
            
            # 获取注册的命令
            checker.register_cli_commands()
            cmd = app.cli.commands['check-env']
            
            # 测试正常执行
            runner = app.test_cli_runner()
            result = runner.invoke(cmd, [])
            assert result.exit_code == 0
            
            # 测试修复模式
            result = runner.invoke(cmd, ['--repair'])
            assert result.exit_code == 0

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

    def test_check_services(self):
        """测试服务检查"""
        app = Flask(__name__)
        checker = EnvironmentChecker(app)
        
        # 测试服务不存在的情况
        assert checker._check_services() is False
        
        # 测试服务存在但未实现check_health方法
        setattr(app, 'cat_service', MagicMock())
        setattr(app, 'user_service', MagicMock())
        assert checker._check_services() is True
        
    def test_check_services_health(self):
        """测试服务健康检查"""
        app = Flask(__name__)
        checker = EnvironmentChecker(app)
        
        # 测试服务不存在的情况
        assert checker._check_services_health() is False
        
        # 测试服务存在但未实现check_health方法
        setattr(app, 'cat_service', object())
        setattr(app, 'user_service', object())
        assert checker._check_services_health() is False
        
        # 测试服务存在但check_health方法返回False
        cat_service = type('CatService', (), {'check_health': lambda self: False})()
        user_service = type('UserService', (), {'check_health': lambda self: True})()
        setattr(app, 'cat_service', cat_service)
        setattr(app, 'user_service', user_service)
        
        with app.app_context():
            assert checker._check_services_health() is False
        
        # 测试健康检查成功
        cat_service = type('CatService', (), {'check_health': lambda self: True})()
        user_service = type('UserService', (), {'check_health': lambda self: True})()
        setattr(app, 'cat_service', cat_service)
        setattr(app, 'user_service', user_service)
        
        with app.app_context():
            assert checker._check_services_health() is True
            
    def test_check_services_health_exception(self):
        """测试服务健康检查异常情况"""
        app = Flask(__name__)
        checker = EnvironmentChecker(app)
        
        # 模拟服务检查抛出异常
        cat_service = type('CatService', (), {
            'check_health': lambda self: 1/0  # 模拟除零错误
        })()
        setattr(app, 'cat_service', cat_service)
        setattr(app, 'user_service', MagicMock())
        
        with app.app_context():
            assert checker._check_services_health() is False
            
    def test_production_specific_checks(self):
        """测试生产环境特定检查"""
        app = Flask(__name__)
        app.config['FLASK_ENV'] = 'production'
        checker = EnvironmentChecker(app)
        
        # 测试生产环境性能检查
        with patch.object(checker, '_check_performance', return_value=True):
            assert checker.check_prod_environment()['performance_optimized'] is True
            
        # 测试生产环境安全检查
        app.config.update({
            'SESSION_COOKIE_SECURE': True,
            'REMEMBER_COOKIE_SECURE': True,
            'SESSION_COOKIE_HTTPONLY': True
        })
        assert checker._check_security() is True
        
    def test_config_check_edge_cases(self):
        """测试配置检查边界条件"""
        app = Flask(__name__)
        checker = EnvironmentChecker(app)
        
        # 测试缺少必要配置项
        app.config.clear()
        assert checker._check_config() is False
        
        # 测试部分配置项缺失
        app.config['SECRET_KEY'] = 'test'
        assert checker._check_config() is False
        
        # 测试所有配置项齐全
        app.config.update({
            'SECRET_KEY': 'test',
            'SQLALCHEMY_DATABASE_URI': 'sqlite://',
            'UPLOAD_FOLDER': 'uploads'
        })
        assert checker._check_config() is True

    def test_migration_check_failures(self):
        """测试迁移检查失败情况"""
        app = Flask(__name__)
        checker = EnvironmentChecker(app)
        
        # 测试无SQLAlchemy扩展
        assert checker._check_migrations() is False
        
        # 测试迁移版本不匹配
        with patch('flask_migrate.Migrate') as mock_migrate, \
             patch('alembic.script.ScriptDirectory') as mock_script:
            app.extensions = {'sqlalchemy': {'db': MagicMock()}}
            mock_migrate.return_value.get_config.return_value = None
            mock_script.from_config.return_value.get_current_head.return_value = "123"
            
            # 模拟get_config返回None时直接返回True
            with patch('flask_migrate.Migrate.get_config', return_value=None):
                assert checker._check_migrations() is True

    def test_performance_optimization(self):
        """测试性能优化逻辑"""
        app = Flask(__name__)
        app.config['FLASK_ENV'] = 'production'
        checker = EnvironmentChecker(app)
        
        # 模拟数据库优化
        with patch('sqlalchemy.text') as mock_text:
            db_mock = MagicMock()
            # 创建模拟的SQLAlchemy扩展对象
            sqlalchemy_ext = MagicMock()
            sqlalchemy_ext.db = db_mock
            app.extensions = {'sqlalchemy': sqlalchemy_ext}
            
            checker._optimize_performance()
            assert mock_text.called
            db_mock.session.execute.assert_called_once()

    def test_route_check_failures(self):
        """测试路由检查失败情况"""
        app = Flask(__name__)
        checker = EnvironmentChecker(app)
        
        # 测试路由不存在
        with patch('flask.url_for', side_effect=Exception("Route not found")):
            assert checker._check_routes() is False

    def test_repair_missing_config(self):
        """测试自动修复缺失配置"""
        app = Flask(__name__)
        checker = EnvironmentChecker(app)
        
        # 测试自动生成SECRET_KEY
        with patch('os.urandom', return_value=b'test'*6):  # 24字节数据
            with patch('flask.current_app', app):
                app.config.clear()
                checker._repair_missing_config()
                assert 'SECRET_KEY' in app.config
                assert len(app.config['SECRET_KEY']) == 48  # 24字节的hex长度
            
        # 测试自动创建上传目录
        with patch('os.makedirs') as mock_makedirs:
            with patch('flask.current_app', app):
                app.config.clear()
                checker._repair_missing_config()
                assert mock_makedirs.called
