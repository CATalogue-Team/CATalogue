import pytest
from unittest.mock import MagicMock, patch
from flask import Flask, url_for

from app.core.base_crud import BaseCRUD

@pytest.fixture
def mock_service():
    """模拟服务层"""
    service = MagicMock()
    service.get.return_value = {'id': 1, 'name': 'Test Item'}
    service.delete.return_value = True
    return service

@pytest.fixture
def test_app():
    """创建测试Flask应用"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret'
    
    # 添加测试路由
    @app.route('/items')
    def item_list():
        return "item list"
    
    @app.route('/items/<int:id>')
    def item_detail(id):
        return f"item {id}"
    
    @app.route('/items/create')
    def item_create():
        return "create item"
    
    @app.route('/items/<int:id>/edit')
    def item_edit(id):
        return f"edit item {id}"
    
    @app.route('/items/<int:id>/delete')
    def item_delete(id):
        return f"delete item {id}"
    
    with app.test_request_context():
        yield app

@pytest.fixture
def base_crud(mock_service, test_app):
    """创建BaseCRUD实例"""
    with test_app.test_request_context():
        return BaseCRUD(
            service=mock_service,
            model_name='item',
            list_template='list.html',
            detail_template='detail.html',
            edit_template='edit.html',
            list_route='item_list',
            detail_route='item_detail',
            create_route='item_create',
            edit_route='item_edit',
            delete_route='item_delete'
        )

class TestBaseCRUD:
    def test_detail_success(self, base_crud, mock_service):
        """测试成功获取详情"""
        with patch('flask.render_template') as mock_render:
            mock_render.return_value = 'detail page'
            response = base_crud.detail(1)
            
            mock_service.get.assert_called_once_with(1)
            assert response.status_code == 302
            assert response.location == '/items'

    def test_detail_not_found(self, base_crud, mock_service):
        """测试获取不存在的详情"""
        mock_service.get.return_value = None
        with patch('flask.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirect'
            response = base_crud.detail(1)
            
            mock_service.get.assert_called_once_with(1)
            assert response.status_code == 302
            assert response.location == '/items'

    def test_delete_success(self, base_crud, mock_service):
        """测试成功删除"""
        with patch('flask.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirect'
            response = base_crud.delete(1)
            
            mock_service.get.assert_called_once_with(1)
            mock_service.delete.assert_called_once_with(1)
            assert response.status_code == 302
            assert response.location == '/items'

    def test_delete_with_callback(self, base_crud, mock_service):
        """测试带回调的删除"""
        mock_callback = MagicMock()
        with patch('flask.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirect'
            response = base_crud.delete(1, before_delete=mock_callback)
            
            mock_callback.assert_called_once_with({'id': 1, 'name': 'Test Item'})
            assert response.status_code == 302
            assert response.location == '/items'

    def test_delete_not_found(self, base_crud, mock_service):
        """测试删除不存在的项"""
        mock_service.get.return_value = None
        with patch('flask.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirect'
            response = base_crud.delete(1)
            
            mock_service.get.assert_called_once_with(1)
            mock_service.delete.assert_not_called()
            assert response.status_code == 302
            assert response.location == '/items'
