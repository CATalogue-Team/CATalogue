import pytest
from datetime import datetime
from app.services.base_service import BaseService
from app.models import Cat
from app.extensions import db
from .TestReporter import TestReporter

class TestBaseService:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        """测试基类服务"""
        self.app = app
        with app.app_context():
            db.create_all()
            yield
            db.drop_all()

    def test_create(self, app):
        """测试创建方法"""
        TestReporter.start_test("测试BaseService.create")
        with app.app_context():
            data = {'name': 'Mittens', 'user_id': 1}
            result = BaseService.create(Cat, **data)
            assert result.name == 'Mittens'
            assert result.user_id == 1
            assert result.id is not None
            TestReporter.success("创建测试通过")

    def test_get(self, app):
        """测试查询方法"""
        TestReporter.start_test("测试BaseService.get")
        with app.app_context():
            cat = Cat(**{'name': 'Whiskers', 'user_id': 1})
            db.session.add(cat)
            db.session.commit()

            result = BaseService.get(Cat, cat.id)
            assert getattr(result, 'name', None) == 'Whiskers'
            assert getattr(result, 'user_id', None) == 1
            TestReporter.success("查询测试通过")

    def test_get_not_found(self, app):
        """测试查询不存在记录"""
        TestReporter.start_test("测试BaseService.get不存在记录")
        with app.app_context():
            result = BaseService.get(Cat, 999)
            assert result is None
            TestReporter.success("不存在记录测试通过")

    def test_get_all(self, app):
        """测试查询所有记录"""
        TestReporter.start_test("测试BaseService.get_all")
        with app.app_context():
            cat1 = Cat(**{'name': 'Fluffy', 'user_id': 1})
            cat2 = Cat(**{'name': 'Spot', 'user_id': 2})
            db.session.add_all([cat1, cat2])
            db.session.commit()
            
            results = BaseService.get_all(Cat)
            assert len(results) == 2
            assert {cat.name for cat in results} == {'Fluffy', 'Spot'}
            TestReporter.success("查询所有测试通过")

    def test_update(self, app):
        """测试更新方法"""
        TestReporter.start_test("测试BaseService.update")
        with app.app_context():
            cat = Cat(**{'name': 'Original', 'user_id': 1})
            db.session.add(cat)
            db.session.commit()

            updated = BaseService.update(Cat, cat.id, **{'name': 'Updated'})
            refreshed = Cat.query.get(cat.id)
            
            assert getattr(updated, 'name', None) == 'Updated'
            assert getattr(updated, 'user_id', None) == 1
            assert getattr(refreshed, 'name', None) == 'Updated'
            assert getattr(refreshed, 'user_id', None) == 1
            TestReporter.success("更新测试通过")

    def test_delete(self, app):
        """测试删除方法"""
        TestReporter.start_test("测试BaseService.delete")
        with app.app_context():
            cat = Cat(**{'name': 'ToDelete', 'user_id': 1})
            db.session.add(cat)
            db.session.commit()

            success = BaseService.delete(Cat, cat.id)
            assert success is True
            assert Cat.query.get(cat.id) is None
            TestReporter.success("删除测试通过")
