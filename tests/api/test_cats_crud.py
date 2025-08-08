import pytest
from fastapi import status
from uuid import uuid4
from datetime import datetime
from tests.api.conftest import assert_response_ok, assert_response_error

@pytest.mark.asyncio
async def test_create_cat(client, auth_headers, test_cat_data, mocker):
    """测试创建猫咪"""
    # Mock CatService with complete fields
    mock_cat = {
        "id": str(uuid4()),
        "name": test_cat_data["name"],
        "owner_id": str(uuid4()),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "breed": test_cat_data.get("breed"),
        "birth_date": test_cat_data.get("birth_date"),
        "photos": []
    }
    mocker.patch(
        "api.services.cat_service.CatService.create_cat",
        return_value=mock_cat
    )
    
    response = await client.post(
        "/api/v1/cats",
        json=test_cat_data,
        headers=auth_headers
    )
    assert_response_ok(response, status.HTTP_201_CREATED)
    assert response.json()["name"] == test_cat_data["name"]

@pytest.mark.asyncio
async def test_get_cats(client, auth_headers, mocker):
    """测试获取猫咪列表"""
    # Mock CatService with complete fields
    mock_cats = [
        {
            "id": str(uuid4()),
            "name": "Cat1",
            "owner_id": str(uuid4()),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "breed": "Breed1",
            "birth_date": "2025-01-01",
            "photos": []
        },
        {
            "id": str(uuid4()),
            "name": "Cat2",
            "owner_id": str(uuid4()),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "breed": "Breed2",
            "birth_date": "2025-01-02",
            "photos": []
        }
    ]
    mocker.patch(
        "api.services.cat_service.CatService.get_all_cats",
        return_value=mock_cats
    )
    
    response = await client.get("/api/v1/cats", headers=auth_headers)
    assert_response_ok(response)
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2

@pytest.mark.asyncio
async def test_get_cat_by_id(client, auth_headers, test_cat_data, mocker):
    """测试获取单个猫咪"""
    # Mock CatService with complete fields
    mock_cat = {
        "id": str(uuid4()),
        "name": test_cat_data["name"],
        "owner_id": str(uuid4()),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "breed": test_cat_data.get("breed"),
        "birth_date": test_cat_data.get("birth_date"),
        "photos": []
    }
    mocker.patch(
        "api.services.cat_service.CatService.get_cat_by_id",
        return_value=mock_cat
    )
    
    cat_id = str(uuid4())
    response = await client.get(f"/api/v1/cats/{cat_id}")
    assert_response_ok(response)
    assert response.json()["id"] == mock_cat["id"]

@pytest.mark.asyncio
async def test_update_cat(client, auth_headers, mocker):
    """测试更新猫咪信息"""
    # Mock CatService with complete fields
    mock_cat = {
        "id": str(uuid4()),
        "name": "Updated Cat",
        "owner_id": str(uuid4()),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "breed": "Updated Breed",
        "birth_date": "2025-01-01",
        "photos": []
    }
    mocker.patch(
        "api.services.cat_service.CatService.update_cat",
        return_value=mock_cat
    )
    
    cat_id = str(uuid4())
    response = await client.put(
        f"/api/v1/cats/{cat_id}",
        json={"name": "Updated Cat"},
        headers=auth_headers
    )
    assert_response_ok(response)
    assert response.json()["name"] == "Updated Cat"

@pytest.mark.asyncio
async def test_delete_cat(client, auth_headers, mocker):
    """测试删除猫咪"""
    # Mock CatService
    mocker.patch(
        "api.services.cat_service.CatService.delete_cat",
        return_value=True
    )
    
    cat_id = str(uuid4())
    response = await client.delete(
        f"/api/v1/cats/{cat_id}",
        headers=auth_headers
    )
    assert_response_ok(response)
    
    # Mock 404 response
    mocker.patch(
        "api.services.cat_service.CatService.get_cat_by_id",
        return_value=None
    )
    non_existent_id = str(uuid4())
    get_res = await client.get(f"/cats/{non_existent_id}")
    assert_response_error(get_res, status.HTTP_404_NOT_FOUND)

@pytest.mark.asyncio
async def test_create_cat_invalid_data(db_session, client, auth_headers):
    """测试创建猫咪-无效数据"""
    response = await client.post(
        "/api/v1/cats",
        json={"invalid": "data"},
        headers=auth_headers
    )
    assert_response_error(response, status.HTTP_422_UNPROCESSABLE_ENTITY)

@pytest.mark.asyncio
async def test_update_nonexistent_cat(db_session, client, auth_headers, mocker):
    """测试更新不存在的猫咪"""
    # Mock CatService to return None for non-existent cat
    mocker.patch(
        "api.services.cat_service.CatService.update_cat",
        return_value=None
    )
    
    cat_id = str(uuid4())
    response = await client.put(
        f"/cats/{cat_id}",
        json={"name": "Nonexistent"},
        headers=auth_headers
    )
    assert_response_error(response, status.HTTP_404_NOT_FOUND)

@pytest.mark.asyncio
async def test_delete_nonexistent_cat(db_session, client, auth_headers, mocker):
    """测试删除不存在的猫咪"""
    # Mock CatService to return False for non-existent cat
    mocker.patch(
        "api.services.cat_service.CatService.delete_cat",
        return_value=False
    )
    
    cat_id = str(uuid4())
    response = await client.delete(
        f"/cats/{cat_id}",
        headers=auth_headers
    )
    assert_response_error(response, status.HTTP_404_NOT_FOUND)
