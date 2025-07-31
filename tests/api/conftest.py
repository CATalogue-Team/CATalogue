import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture
def test_client():
    """创建FastAPI测试客户端"""
    return TestClient(app)

@pytest.fixture
def auth_headers(test_client):
    """获取认证头信息"""
    # 测试用户登录获取token
    response = test_client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
