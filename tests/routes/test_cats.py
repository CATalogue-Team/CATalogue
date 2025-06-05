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
        with patch('app.routes.cats.CatService.get_all_cats') as mock_get:
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
                data=json.dumps({
                    'name': 'New Cat',
                    'age': 2,
                    'breed': 'Test Breed',
                    'description': '',
                    'is_adopted': False,
                    'user_id': 1,
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }),
                auth_token='test_token_123'
            )
            
            assert response.status_code == 201
            assert response.json['id'] == 1
            assert response.json['name'] == 'New Cat'
            assert response.json['breed'] == 'Test Breed'
            assert response.json['age'] == 2

    def test_get_cat(self, client):
        with patch('app.routes.cats.CatService.get_cat') as mock_get:
            mock_get.return_value = Cat(id=1, name='Test Cat', age=3)
            response = client.get('/api/v1/cats/1', auth_token='test_token')
            assert response.status_code == 200
            assert response.json['name'] == 'Test Cat'

    def test_update_cat(self, client):
        with patch('app.routes.cats.CatService.update_cat') as mock_update:
            mock_update.return_value = Cat(id=1, name='Updated Cat', age=4)
            response = client.put(
                '/api/v1/cats/1',
                data=json.dumps({
                    'name': 'Updated Cat', 
                    'age': 4,
                    'breed': 'Test Breed',
                    'description': '',
                    'is_adopted': False,
                    'updated_at': datetime.utcnow().isoformat()
                }),
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
        with patch('app.routes.cats.CatService.search_cats') as mock_search:
            mock_cat = Cat(id=1, name='Found Cat', age=3)
            mock_search.return_value = [mock_cat]
            response = client.get('/api/v1/cats/search?q=Found', auth_token='test_token')
            assert response.status_code == 200
            assert response.json[0]['name'] == 'Found Cat'

    def test_upload_cat_image(self, client):
        with patch('app.routes.cats.CatService.get_cat') as mock_get, \
             patch('app.routes.cats.CatService.update_cat') as mock_update, \
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
