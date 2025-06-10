import pytest
import json
from unittest.mock import patch, MagicMock
from flask import jsonify, current_app
from io import BytesIO
from datetime import datetime

from app.models import Cat
from app.services.cat_service import CatService
from tests.test_client import CustomTestClient
from tests.services.users.test_reporter import TestReporter

@pytest.fixture
def client(app):
    """使用CustomTestClient"""
    return CustomTestClient(app, TestReporter())

class TestCatRoutes:
    def test_get_cats(self, client):
        with patch('app.services.cat_service.CatService.search') as mock_get:
            mock_cat = Cat(id=1, name='Test Cat', age=3)
            mock_get.return_value = [mock_cat]
            response = client.get('/api/v1/cats', auth_token='test_token')
            assert response.status_code == 200
            assert len(response.json) == 1
            assert response.json[0]['name'] == 'Test Cat'

    def test_create_cat(self, client):
        with patch('app.routes.cats.CatService.create_cat') as mock_create:
            mock_cat = Cat(
                id=1, 
                name='New Cat', 
                age=2, 
                breed='Test Breed', 
                description='', 
                is_adopted=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            mock_create.return_value = mock_cat
            
            current_app.logger.info("Starting test_create_cat")
            
            response = client.post(
                '/api/v1/cats',
                data={
                    'name': 'New Cat',
                    'age': 2,
                    'breed': 'Test Breed',
                    'description': '',
                    'is_adopted': False,
                    'user_id': 1
                },
                auth_token='test_token_123'
            )
            
            assert response.status_code == 201
            assert response.json['id'] == 1
            assert response.json['name'] == 'New Cat'
            assert response.json['breed'] == 'Test Breed'
            assert response.json['age'] == 2

    def test_get_cat(self, client):
        with patch('app.services.cat_service.CatService.get') as mock_get:
            mock_get.return_value = Cat(id=1, name='Test Cat', age=3)
            response = client.get('/api/v1/cats/1', auth_token='test_token')
            assert response.status_code == 200
            assert response.json['name'] == 'Test Cat'

    def test_update_cat(self, client):
        with patch('app.routes.cats.CatService.update_cat') as mock_update:
            mock_update.return_value = Cat(id=1, name='Updated Cat', age=4)
            response = client.put(
                '/api/v1/cats/1',
                data={
                    'name': 'Updated Cat', 
                    'age': 4,
                    'breed': 'Test Breed',
                    'description': '',
                    'is_adopted': False
                },
                auth_token='test_token'
            )
            assert response.status_code == 200
            assert response.json['name'] == 'Updated Cat'

    def test_delete_cat(self, client):
        with patch('app.routes.cats.CatService.delete_cat') as mock_delete:
            mock_delete.return_value = True
            response = client.delete(
                '/api/v1/cats/1',
                auth_token='test_token'
            )
            assert response.status_code == 204

    def test_search_cats(self, client):
        with patch('app.services.cat_service.CatService.search') as mock_search:
            mock_cat = Cat(id=1, name='Found Cat', age=3)
            mock_search.return_value = [mock_cat]
            response = client.get('/api/v1/cats/search?q=Found', auth_token='test_token')
            assert response.status_code == 200
            assert response.json[0]['name'] == 'Found Cat'

    def test_upload_cat_image(self, client):
        with patch('app.services.cat_service.CatService.get') as mock_get, \
             patch('app.services.cat_service.CatService.update_cat') as mock_update, \
             patch('app.routes.cats.os.path.join') as mock_join, \
             patch('app.routes.cats.os.makedirs'):
            
            mock_get.return_value = Cat(id=1, name='Test Cat')
            mock_update.return_value = Cat(id=1, name='Test Cat')
            mock_join.return_value = '/tmp/mock_path/test.jpg'

            mock_file = MagicMock()
            mock_file.filename = 'test.jpg'
            mock_file.save = MagicMock()

            with patch('app.routes.cats.request') as mock_request:
                mock_request.files = {'file': mock_file}

                response = client.post_file(
                    '/api/v1/cats/1/image',
                    file_data={'file': (BytesIO(b'test_image_data'), 'test.jpg')},
                    auth_token='test_token'
                )
                assert response.status_code == 200
                
    # 新增测试用例
    def test_get_non_existent_cat(self, client):
        """测试获取不存在的猫咪"""
        with patch('app.services.cat_service.CatService.get') as mock_get:
            mock_get.return_value = None
            response = client.get('/api/v1/cats/999', auth_token='test_token')
            assert response.status_code == 404
            assert 'Cat not found' in response.json['error']

    def test_create_cat_missing_fields(self, client):
        """测试创建猫咪缺少必填字段"""
        response = client.post(
            '/api/v1/cats',
            data={},  # 缺少所有必填字段
            auth_token='test_token'
        )
        assert response.status_code == 400
        assert 'Missing required fields' in response.json['error']
        assert 'name' in response.json['missing']
        assert 'age' in response.json['missing']
        assert 'breed' in response.json['missing']

    def test_update_non_existent_cat(self, client):
        """测试更新不存在的猫咪"""
        with patch('app.routes.cats.CatService.update_cat') as mock_update:
            mock_update.return_value = None
            response = client.put(
                '/api/v1/cats/999',
                data={
                    'name': 'Updated Cat', 
                    'age': 4,
                    'breed': 'Test Breed',
                    'description': '',
                    'is_adopted': False
                },
                auth_token='test_token'
            )
            assert response.status_code == 404
            assert 'Cat not found' in response.json['error']

    def test_delete_non_existent_cat(self, client):
        """测试删除不存在的猫咪"""
        with patch('app.routes.cats.CatService.delete_cat') as mock_delete:
            mock_delete.return_value = False
            response = client.delete(
                '/api/v1/cats/999',
                auth_token='test_token'
            )
            assert response.status_code == 404
            assert 'Cat not found' in response.json['error']

    def test_search_invalid_params(self, client):
        """测试搜索参数无效的情况"""
        with patch('app.services.cat_service.CatService.search') as mock_search:
            mock_search.return_value = []
            # 测试年龄参数无效
            response = client.get('/api/v1/cats/search?min_age=abc', auth_token='test_token')
            assert response.status_code == 200
            assert len(response.json) == 0
            
            # 测试布尔参数无效
            response = client.get('/api/v1/cats/search?is_adopted=invalid', auth_token='test_token')
            assert response.status_code == 200
            assert len(response.json) == 0

    def test_upload_image_errors(self, client):
        """测试上传图片的各种错误情况"""
        # 猫咪不存在
        with patch('app.services.cat_service.CatService.get') as mock_get:
            mock_get.return_value = None
            response = client.post_file(
                '/api/v1/cats/999/image',
                file_data={'file': (BytesIO(b'test_image_data'), 'test.jpg')},
                auth_token='test_token'
            )
            assert response.status_code == 404
            assert 'Cat not found' in response.json['error']
        
        # 无文件部分
        with patch('app.services.cat_service.CatService.get') as mock_get:
            mock_get.return_value = Cat(id=1, name='Test Cat')
            with patch('app.routes.cats.request') as mock_request:
                mock_request.files = {}
                response = client.post_file(
                    '/api/v1/cats/1/image',
                    file_data={},
                    auth_token='test_token'
                )
                assert response.status_code == 400
                assert 'No file part' in response.json['error']
        
        # 文件名为空
        with patch('app.services.cat_service.CatService.get') as mock_get:
            mock_get.return_value = Cat(id=1, name='Test Cat')
            with patch('app.routes.cats.request') as mock_request:
                mock_file = MagicMock()
                mock_file.filename = ''
                mock_request.files = {'file': mock_file}
                
                response = client.post_file(
                    '/api/v1/cats/1/image',
                    file_data={'file': (BytesIO(b''), '')},
                    auth_token='test_token'
                )
                assert response.status_code == 400
                assert 'No selected file' in response.json['error']
        
        # 无效内容类型
        with patch('app.services.cat_service.CatService.get') as mock_get:
            mock_get.return_value = Cat(id=1, name='Test Cat')
            with patch('app.routes.cats.request') as mock_request:
                mock_request.content_type = 'application/json'
                mock_file = MagicMock()
                mock_file.filename = 'test.jpg'
                mock_request.files = {'file': mock_file}
                
                response = client.post_file(
                    '/api/v1/cats/1/image',
                    file_data={'file': (BytesIO(b'test_image_data'), 'test.jpg')},
                    auth_token='test_token'
                )
                assert response.status_code == 400
                assert 'Content-Type must be multipart/form-data' in response.json['error']
