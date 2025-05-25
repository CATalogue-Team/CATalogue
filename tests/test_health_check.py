import pytest
from unittest.mock import MagicMock, patch
from app.core.health_check import EnvironmentChecker
from flask import Flask

class TestEnvironmentChecker:
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def checker(self, app):
        return EnvironmentChecker(app)

    def test_check_dev_environment(self, checker):
        """测试开发环境检查"""
        with patch.object(checker, '_check_database', return_value=True), \
             patch.object(checker, '_check_test_environment', return_value=True), \
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
        """测试生产环境检查"""
        with patch.object(checker, '_check_database', return_value=True), \
             patch.object(checker, '_check_storage', return_value=True), \
             patch.object(checker, '_check_security', return_value=True), \
             patch.object(checker, '_check_backups', return_value=True), \
             patch.object(checker, '_check_performance', return_value=True):
            
            result = checker.check_prod_environment()
            assert isinstance(result, dict)
            assert all(result.values())

    def test_check_database_success(self, checker):
        """测试数据库检查成功"""
        with patch('app.core.health_check.db') as mock_db:
            mock_db.session.execute.return_value = True
            result = checker._check_database()
            assert result is True

    def test_check_database_failure(self, checker):
        """测试数据库检查失败"""
        with patch('app.core.health_check.db') as mock_db:
            mock_db.session.execute.side_effect = Exception('DB error')
            result = checker._check_database()
            assert result is False

    def test_check_services_health(self, checker):
        """测试服务健康检查"""
        checker.app.cat_service = MagicMock()
        checker.app.user_service = MagicMock()
        result = checker._check_services_health()
        assert result is True

    def test_run_auto_repair(self, checker):
        """测试自动修复功能"""
        failed_checks = {
            'dependencies_installed': False,
            'migrations_applied': False
        }
        with patch.object(checker, '_install_dependencies'), \
             patch.object(checker, '_apply_migrations'):
            
            result = checker.run_auto_repair(failed_checks)
            assert isinstance(result, dict)
            assert all(result.values())
