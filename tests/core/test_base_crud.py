import pytest
import logging
from unittest.mock import patch
from flask import url_for
from app.core.base_crud import BaseCRUD
from app.models import Cat, User
from app import db
from app.services.cat_service import CatService

class TestBaseCRUD:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        app.config.update({
            'SERVER_NAME': 'localhost.localdomain',
            'APPLICATION_ROOT': '/',
            'PREFERRED_URL_SCHEME': 'http'
        })
        
        self.service = CatService(db)
        self.crud = BaseCRUD(
            service=self.service,
            model_name='cat',
            list_template='cats/list.html',
            detail_template='cats/detail.html',
            edit_template='cats/edit.html',
            list_route='admin_cats.list_cats',
            detail_route='admin_cats.get_cat',
            create_route='admin_cats.create_cat',
            edit_route='admin_cats.update_cat',
            delete_route='admin_cats.delete_cat'
        )
        with app.app_context():
            db.create_all()
            # 创建测试数据
            self.test_user = User(username='test', password_hash='test')
            db.session.add(self.test_user)
            db.session.commit()
            yield
            db.drop_all()

    def test_detail(self, app):
        """测试详情页"""
        with app.test_request_context():
            cat = Cat(name='Test Cat', age=2, user_id=self.test_user.id)
            db.session.add(cat)
            db.session.commit()
            
            response = self.crud.detail(cat.id)
            assert response.status_code == 302
            assert url_for('admin_cats.list_cats') in response.location

    def test_delete(self, app):
        """测试删除操作"""
        with app.test_request_context():
            cat = Cat(name='To Delete', age=3, user_id=self.test_user.id)
            db.session.add(cat)
            db.session.commit()
            
            def mock_before_delete(item):
                assert item.id == cat.id
            
            # 测试正常删除
            response = self.crud.delete(
                id=cat.id,
                user_id=self.test_user.id,
                before_delete=mock_before_delete,
                success_message='删除成功!'
            )
            assert response.status_code == 302
            assert url_for('admin_cats.list_cats') in response.location
            
            # 测试不存在的item
            response = self.crud.delete(
                id=999,
                user_id=self.test_user.id
            )
            assert response.status_code == 302
            
            # 测试before_delete抛出异常
            def failing_before_delete(item):
                raise Exception("Test error")
            
            cat = Cat(name='To Delete 2', age=3, user_id=self.test_user.id)
            db.session.add(cat)
            db.session.commit()
            
            response = self.crud.delete(
                id=cat.id,
                user_id=self.test_user.id,
                before_delete=failing_before_delete
            )
            assert response.status_code == 302

    def test_detail_error_cases(self, app):
        """测试详情页错误情况"""
        with app.test_request_context():
            # 测试不存在的item
            response = self.crud.detail(999)
            assert response.status_code == 302
            
            # 测试模板渲染失败
            original_template = self.crud.detail_template
            self.crud.detail_template = 'nonexistent_template.html'
            cat = Cat(name='Test Cat', age=2, user_id=self.test_user.id)
            db.session.add(cat)
            db.session.commit()
            
            response = self.crud.detail(cat.id)
            assert response.status_code == 302
            self.crud.detail_template = original_template

    def test_delete_error_logging(self, app, caplog):
        """测试删除操作错误日志记录"""
        with app.test_request_context():
            cat = Cat(name='To Delete', age=3, user_id=self.test_user.id)
            db.session.add(cat)
            db.session.commit()
            
            # 模拟删除失败
            with patch.object(self.service, 'delete', side_effect=Exception("Test error")):
                response = self.crud.delete(
                    id=cat.id,
                    user_id=self.test_user.id
                )
                assert response.status_code == 302
                assert "删除cat失败" in caplog.text
                assert "Test error" in caplog.text

    def test_detail_error_logging(self, app, caplog):
        """测试详情页错误日志记录"""
        with app.test_request_context():
            # 确保日志级别设置为DEBUG
            caplog.set_level(logging.DEBUG)
            
            # 模拟模板渲染失败
            cat = Cat(name='Test Cat', age=2, user_id=self.test_user.id)
            db.session.add(cat)
            db.session.commit()
            
            # 同时mock render_template和service.get
            with patch('app.core.base_crud.render_template', side_effect=Exception("Template render error")), \
                 patch.object(self.service, 'get', return_value=cat):
                response = self.crud.detail(cat.id)
                assert response.status_code == 302
                assert "获取cat详情失败" in caplog.text
                assert "Template render error" in caplog.text
                assert any(record.levelname == "ERROR" for record in caplog.records)
                assert any("Template render error" in record.message for record in caplog.records)
                # 确保日志记录器被调用
                assert any(record.name == "app.core.base_crud" for record in caplog.records)
