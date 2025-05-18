import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime
from flask import Flask
from app.core.health_check import EnvironmentChecker

@pytest.fixture
def mock_app():
    app = Flask(__name__)
    app.config.update({
        'FLASK_ENV': 'development',
        'SECRET_KEY': 'test',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'UPLOAD_FOLDER': 'uploads',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    # 创建完整的SQLAlchemy mock结构
    db_mock = MagicMock()
    db_mock.session = MagicMock()
    db_mock.engine = MagicMock()
    
    # 创建迁移mock
    migrate_mock = MagicMock()
    migrate_mock.get_config.return_value = MagicMock()
    
    app.extensions = {
        'sqlalchemy': {
            'db': db_mock
        },
        'migrate': migrate_mock
    }
    return app

@pytest.fixture
def checker(mock_app):
    return EnvironmentChecker(mock_app)

class TestEnvironmentChecker:
    def test_init(self, checker, mock_app):
        assert checker.app == mock_app
        assert checker.logger.name == 'app.core.health_check'

    def test_check_dev_environment(self, checker):
        with patch.object(checker, '_check_test_environment', return_value=True), \
             patch.object(checker, '_check_database', return_value=True), \
             patch.object(checker, '_clean_temp_files', return_value=1), \
             patch.object(checker, '_validate_urls', return_value=True), \
             patch.object(checker, '_check_config', return_value=True), \
             patch.object(checker, '_check_dependencies', return_value=True), \
             patch.object(checker, '_check_migrations', return_value=True), \
             patch.object(checker, '_check_routes', return_value=True), \
             patch.object(checker, '_check_services_health', return_value=True):
            
            result = checker.check_dev_environment()
            assert isinstance(result, dict)
            assert all(result.values())

    def test_check_prod_environment(self, checker):
        checker.app.config['FLASK_ENV'] = 'production'
        with patch.object(checker, '_check_database', return_value=True), \
             patch.object(checker, '_check_storage', return_value=True), \
             patch.object(checker, '_check_security', return_value=True), \
             patch.object(checker, '_check_backups', return_value=True), \
             patch.object(checker, '_check_performance', return_value=True):
            
            result = checker.check_prod_environment()
            assert isinstance(result, dict)
            # 检查实际存在的检查项
            expected_keys = ['db_connected', 'storage_writable', 
                           'security_configured', 'backup_configured',
                           'performance_optimized']
            assert all(k in result for k in expected_keys)

    def test_check_test_environment(self, checker):
        with patch('builtins.__import__'), \
             patch('coverage.Coverage'), \
             patch('pytest.main', return_value=0), \
             patch.object(Path, 'exists', return_value=True):
            
            result = checker._check_test_environment()
            assert result is True

    @pytest.mark.parametrize("mock_side_effect,expected", [
        (None, True),
        (Exception("DB error"), False)
    ])
    def test_check_database(self, checker, mock_side_effect, expected):
        with patch('sqlalchemy.text'), \
             patch.object(checker.app.extensions['sqlalchemy']['db'].session, 
                        'execute', 
                        side_effect=mock_side_effect):
            result = checker._check_database()
            assert result is expected

    def test_clean_temp_files(self, checker):
        with patch.object(Path, 'glob', return_value=[]):
            result = checker._clean_temp_files()
            assert result == 1

    def test_validate_urls(self, checker):
        with patch('image_url_validator.validate_and_fix_image_urls'):
            result = checker._validate_urls()
            assert result is True

    def test_check_config(self, checker):
        result = checker._check_config()
        assert result is True

    def test_check_dependencies(self, checker):
        with patch('pkg_resources.parse_requirements'), \
             patch('pkg_resources.require'):
            result = checker._check_dependencies()
            assert result is True

    def test_check_migrations(self, checker):
        with patch('flask_migrate.upgrade'), \
             patch('flask_migrate.Migrate'):
            result = checker._check_migrations()
            assert result is True

    def test_save_check_results(self, checker):
        with patch('app.models.EnvironmentCheck'), \
             patch.object(checker.app.extensions['sqlalchemy']['db'].session, 'add'), \
             patch.object(checker.app.extensions['sqlalchemy']['db'].session, 'commit'):
            result = checker.save_check_results({'test': True})
            assert result is True

    def test_run_auto_repair(self, checker):
        with patch.object(checker, '_install_dependencies'), \
             patch.object(checker, '_apply_migrations'), \
             patch.object(checker, '_clean_temp_files'), \
             patch.object(checker, '_validate_urls'), \
             patch.object(checker, '_repair_missing_config'), \
             patch.object(checker, '_optimize_performance'):
            
            result = checker.run_auto_repair({
                'dependencies_installed': False,
                'migrations_applied': False,
                'temp_files_cleaned': False,
                'urls_validated': False,
                'config_valid': False,
                'performance_optimized': False
            })
            assert all(result.values())

    def test_register_cli_commands(self, checker):
        with patch('click.command'), \
             patch('click.option'), \
             patch.object(checker.app.cli, 'add_command'):
            checker.register_cli_commands()
