import pytest
from app.routes.cats.base import bp, init_cat_crud
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
        # 测试初始化CRUD
        crud = init_cat_crud(app.cat_service)
        assert crud is not None
