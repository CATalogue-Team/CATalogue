import pytest
from fastapi import status

def test_register_user(test_client):
    """测试用户注册端点"""
    response = test_client.post(
        "/api/v1/users/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "validpassword123"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.json()

def test_login_user(test_client):
    """测试用户登录端点"""
    # 先注册测试用户
    test_client.post(
        "/api/v1/users/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "validpassword123"
        }
    )
    
    # 测试登录
    response = test_client.post(
        "/api/v1/auth/login",
        json={
            "username": "loginuser",
            "password": "validpassword123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

def test_protected_route(test_client, auth_headers):
    """测试受保护路由"""
    response = test_client.get(
        "/api/v1/users/me",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "testuser"
