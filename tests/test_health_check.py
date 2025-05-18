import pytest
from unittest.mock import MagicMock, patch
from app.core.health_check import EnvironmentChecker
from flask import Flask
from .TestReporter import TestReporter

class TestEnvironmentChecker:
    """环境检查测试类"""

    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.extensions = {'sqlalchemy': {'db': MagicMock()}}
        return app

    @pytest.fixture
    def checker(self, app):
        """创建环境检查器实例"""
        return EnvironmentChecker(app)

    def test_check_dev_environment(self, checker, app):
        """测试开发环境检查"""
        TestReporter.start_test("测试开发环境检查")
        with patch.object(checker, '_check_database', return_value=True), \
             patch.object(checker, '_check_test_environment', return_value=True):
            results = checker.check_dev_environment()
            assert isinstance(results, dict)
            assert 'test_ready' in results
            assert 'db_ready' in results
            TestReporter.success("开发环境检查测试通过")

    def test_check_database(self, checker, app):
        """测试数据库检查"""
        TestReporter.start_test("测试数据库检查")
        app.config['FLASK_ENV'] = 'development'
        with app.app_context():
            with patch('sqlalchemy.text') as mock_text:
                mock_text.return_value = 'SELECT 1'
                result = checker._check_database()
                assert result is True
                TestReporter.success("数据库检查测试通过")

    def test_check_config(self, checker):
        """测试配置检查"""
        TestReporter.start_test("测试配置验证")
        checker.app.config.update({
            'SECRET_KEY': 'test',
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'UPLOAD_FOLDER': '/tmp'
        })
        result = checker._check_config()
        assert result is True
        TestReporter.success("配置验证测试通过")

    def test_check_dependencies(self, checker):
        """测试依赖检查"""
        TestReporter.start_test("测试依赖检查")
        with patch('pkg_resources.require') as mock_require:
            mock_require.return_value = True
            result = checker._check_dependencies()
            assert result is True
            TestReporter.success("依赖检查测试通过")

    def test_save_check_results(self, checker, app):
        """测试保存检查结果"""
        TestReporter.start_test("测试保存检查结果")
        with app.app_context():
            with patch('app.models.EnvironmentCheck') as mock_model:
                mock_model.return_value = MagicMock()
                result = checker.save_check_results({'test': True})
                assert result is True
                TestReporter.success("保存结果测试通过")
