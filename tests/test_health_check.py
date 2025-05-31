import pytest
from unittest.mock import MagicMock, patch
from app.core.health_check import EnvironmentChecker

class TestEnvironmentChecker:
    @pytest.fixture
    def app(self, app):
        """使用conftest.py中的app fixture"""
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

    def test_check_database_success(self, checker, app):
        """测试数据库检查成功"""
        mock_db = MagicMock()
        mock_db.session.execute.return_value = True
        app.extensions = {'sqlalchemy': {'db': mock_db}}
        
        result = checker._check_database()
        assert result is True

    def test_check_database_failure(self, checker, app):
        """测试数据库检查失败"""
        mock_db = MagicMock()
        mock_db.session.execute.side_effect = Exception('DB error')
        app.extensions = {'sqlalchemy': {'db': mock_db}}
        
        result = checker._check_database()
        assert result is False

    def test_check_services_health(self, checker, app):
        """测试服务健康检查"""
        # 创建模拟服务实例
        mock_cat_service = MagicMock()
        mock_user_service = MagicMock()
        
        # 设置服务健康检查返回True
        mock_cat_service.check_health.return_value = True
        mock_user_service.check_health.return_value = True
        
        # 将模拟服务添加到app上下文
        app.cat_service = mock_cat_service
        app.user_service = mock_user_service
        
        result = checker._check_services_health()
        assert result is True
        
        # 验证服务方法被调用
        mock_cat_service.check_health.assert_called_once()
        mock_user_service.check_health.assert_called_once()

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
