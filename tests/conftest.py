import pytest
from app import create_app
from app.extensions import db
from app.config import TestingConfig

@pytest.fixture(scope='module')
def test_client():
    app = create_app(TestingConfig)
    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()

@pytest.fixture(scope='module')
def init_db():
    db.create_all()
    
    yield db
    
    db.session.remove()
    db.drop_all()

@pytest.fixture
def auth_headers(test_client):
    # Helper to get auth headers after login
    response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    return {
        'Authorization': f'Bearer {response.json["access_token"]}'
    }
