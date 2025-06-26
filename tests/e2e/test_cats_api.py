import pytest
from app import create_app
from app.models import db, Cat

@pytest.fixture
def client():
    from app.config import TestingConfig
    app = create_app(TestingConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_invalid_cat_id(client):
    """测试无效猫咪ID"""
    # 不存在的ID
    response = client.get('/cats/api/v1/cats/9999')
    assert response.status_code == 404
    data = response.get_json()
    assert '猫咪不存在' in data['error']['message']

def test_invalid_json(client):
    """测试无效JSON格式"""
    # 非JSON请求
    response = client.post('/cats/api/v1/cats', 
        data='invalid json',
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'The browser (or proxy) sent a request that this server could not understand.' in data['message']

def test_create_cat_validation(client):
    """测试创建猫咪的参数验证"""
    # 缺少user_id
    response = client.post('/cats/api/v1/cats', json={
        'name': 'Invalid Cat'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert '缺少user_id字段' in data['error']['message']

def test_update_cat_permission(client):
    """测试更新猫咪的权限验证"""
    test_cat = Cat(name='Protected Cat', age=3, user_id=2)
    db.session.add(test_cat)
    db.session.commit()

    # 尝试用不同用户更新
    response = client.put(f'/cats/api/v1/cats/{test_cat.id}', json={
        'user_id': 1,  # 非所有者
        'name': 'Hacked Cat'
    })
    assert response.status_code == 403

def test_get_cats_list(client):
    # 准备测试数据
    test_cat = Cat(name='Test Cat', age=3, user_id=1)
    db.session.add(test_cat)
    db.session.commit()

    # 调用API
    response = client.get('/cats/api/v1/cats')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['data']) == 1
    assert data['data'][0]['name'] == 'Test Cat'

def test_create_cat(client):
    # 测试创建猫咪
    response = client.post('/cats/api/v1/cats', json={
        'user_id': 1,
        'name': 'New Cat',
        'age': 2
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['data']['name'] == 'New Cat'

def test_update_cat(client):
    # 准备测试数据
    test_cat = Cat(name='Old Cat', age=3, user_id=1)
    db.session.add(test_cat)
    db.session.commit()

    # 测试更新
    response = client.put(f'/cats/api/v1/cats/{test_cat.id}', json={
        'user_id': 1,
        'name': 'Updated Cat'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['data']['name'] == 'Updated Cat'

def test_delete_cat(client):
    # 准备测试数据
    test_cat = Cat(name='To Delete', age=3, user_id=1)
    db.session.add(test_cat)
    db.session.commit()

    # 测试删除
    response = client.delete(f'/cats/api/v1/cats/{test_cat.id}', json={
        'user_id': 1
    })
    assert response.status_code == 204
