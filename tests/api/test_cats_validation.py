import pytest
from fastapi import status
from datetime import date
from uuid import uuid4
from tests.api.conftest import assert_response_error

@pytest.mark.asyncio
async def test_create_cat_missing_required_fields(client, auth_headers):
    """测试创建猫咪-缺少必填字段"""
    # 缺少name字段
    invalid_data = {
        "breed": "Persian",
        "birth_date": "2025-01-01",
        "owner_id": str(uuid4())
    }
    response = await client.post(
        "/api/v1/cats",
        json=invalid_data,
        headers=auth_headers
    )
    assert_response_error(response, status.HTTP_422_UNPROCESSABLE_ENTITY)

    # 缺少owner_id字段
    invalid_data = {
        "name": "Fluffy",
        "breed": "Persian",
        "birth_date": "2025-01-01"
    }
    response = await client.post(
        "/api/v1/cats",
        json=invalid_data,
        headers=auth_headers
    )
    assert_response_error(response, status.HTTP_422_UNPROCESSABLE_ENTITY)

@pytest.mark.asyncio
async def test_create_cat_field_length_validation(client, auth_headers):
    """测试字段长度验证"""
    # name字段超过100字符
    long_name = "x" * 101
    invalid_data = {
        "name": long_name,
        "owner_id": str(uuid4())
    }
    response = await client.post(
        "/api/v1/cats",
        json=invalid_data,
        headers=auth_headers
    )
    assert_response_error(response, status.HTTP_422_UNPROCESSABLE_ENTITY)

    # breed字段超过50字符
    long_breed = "x" * 51
    invalid_data = {
        "name": "Fluffy",
        "breed": long_breed,
        "owner_id": str(uuid4())
    }
    response = await client.post(
        "/api/v1/cats",
        json=invalid_data,
        headers=auth_headers
    )
    assert_response_error(response, status.HTTP_422_UNPROCESSABLE_ENTITY)

@pytest.mark.asyncio
async def test_create_cat_invalid_date_format(client, auth_headers):
    """测试无效日期格式"""
    invalid_data = {
        "name": "Fluffy",
        "birth_date": "2025/01/01",  # 无效格式
        "owner_id": str(uuid4())
    }
    response = await client.post(
        "/api/v1/cats",
        json=invalid_data,
        headers=auth_headers
    )
    assert_response_error(response, status.HTTP_422_UNPROCESSABLE_ENTITY)

    invalid_data = {
        "name": "Fluffy",
        "birth_date": "not-a-date",  # 完全无效
        "owner_id": str(uuid4())
    }
    response = await client.post(
        "/api/v1/cats",
        json=invalid_data,
        headers=auth_headers
    )
    assert_response_error(response, status.HTTP_422_UNPROCESSABLE_ENTITY)

@pytest.mark.asyncio
async def test_create_cat_invalid_owner_id(client, auth_headers):
    """测试无效owner_id格式"""
    invalid_data = {
        "name": "Fluffy",
        "owner_id": "not-a-uuid"  # 无效UUID格式
    }
    response = await client.post(
        "/api/v1/cats",
        json=invalid_data,
        headers=auth_headers
    )
    assert_response_error(response, status.HTTP_422_UNPROCESSABLE_ENTITY)
