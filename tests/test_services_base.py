import unittest
from unittest.mock import patch, MagicMock
from tests.base import BaseTestCase
from app.services.base_service import BaseService
from app.models import Cat
from app.extensions import db

class TestBaseService(BaseTestCase):
    def test_create(self):
        data = {'name': 'Mittens', 'user_id': 1}
        result = BaseService.create(Cat, **data)
        self.assertEqual(result.name, 'Mittens')
        self.assertEqual(result.user_id, 1)
        self.assertIsNotNone(result.id)

    def test_get(self):
        cat = Cat(**{'name': 'Whiskers', 'user_id': 1})
        db.session.add(cat)
        db.session.commit()

        result = BaseService.get(Cat, cat.id)
        self.assertEqual(getattr(result, 'name', None), 'Whiskers')
        self.assertEqual(getattr(result, 'user_id', None), 1)

    def test_get_not_found(self):
        result = BaseService.get(Cat, 999)
        self.assertIsNone(result)

    def test_get_all(self):
        # 创建真实测试数据
        cat1 = Cat(**{'name': 'Fluffy', 'user_id': 1})
        cat2 = Cat(**{'name': 'Spot', 'user_id': 2})
        db.session.add_all([cat1, cat2])
        db.session.commit()
        
        results = BaseService.get_all(Cat)
        self.assertEqual(len(results), 2)
        self.assertEqual({cat.name for cat in results}, {'Fluffy', 'Spot'})

    def test_update(self):
        # 创建初始记录
        cat = Cat(**{'name': 'Original', 'user_id': 1})
        db.session.add(cat)
        db.session.commit()

        # 更新记录
        updated = BaseService.update(Cat, cat.id, **{'name': 'Updated'})
        
        # 重新从数据库加载以确保更新持久化
        refreshed = Cat.query.get(cat.id)
        
        # 验证更新结果
        self.assertEqual(getattr(updated, 'name', None), 'Updated')
        self.assertEqual(getattr(updated, 'user_id', None), 1)
        self.assertEqual(getattr(refreshed, 'name', None), 'Updated')
        self.assertEqual(getattr(refreshed, 'user_id', None), 1)

    def test_delete(self):
        cat = Cat(**{'name': 'ToDelete', 'user_id': 1})
        db.session.add(cat)
        db.session.commit()

        success = BaseService.delete(Cat, cat.id)
        self.assertTrue(success)
        self.assertIsNone(Cat.query.get(cat.id))
