import pytest
from app.routes.cats.base import bp, cat_crud
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

def test_blueprint_registration(app):
    """测试蓝图是否正确注册"""
    with app.test_client() as client:
        assert 'cats' in app.blueprints
        assert cat_crud is not None
