import pytest
from unittest.mock import MagicMock, patch
from app.services.base_service import BaseService
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

# 创建测试模型
Base = declarative_base()

class TestModel(Base):
    __tablename__ = 'test_model'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(100), nullable=True)

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.session = MagicMock()
    return db

def test_init_with_invalid_db():
    """测试无效db参数初始化"""
    with pytest.raises(ValueError):
        BaseService(None)
    
    db = MagicMock()
    del db.session
    with pytest.raises(ValueError):
        BaseService(db)

def test_init_with_missing_get_method():
    """测试缺少get方法的db.session"""
    db = MagicMock()
    db.session = MagicMock()
    del db.session.get
    with pytest.raises(ValueError):
        BaseService(db)

def test_create_with_missing_required_fields(mock_db):
    """测试缺少必填字段"""
    service = BaseService(mock_db)
    with pytest.raises(ValueError) as excinfo:
        service.create(TestModel, description="test")
    assert "缺少必填字段" in str(excinfo.value)

def test_create_success(mock_db):
    """测试成功创建记录"""
    service = BaseService(mock_db)
    mock_db.session.get.return_value = None
    
    result = service.create(TestModel, name="test", description="desc")
    assert mock_db.session.add.called
    assert mock_db.session.commit.called

def test_update_not_found(mock_db):
    """测试更新不存在的记录"""
    service = BaseService(mock_db)
    mock_db.session.get.return_value = None
    
    result = service.update(TestModel, 1, name="new")
    assert result is None
    assert not mock_db.session.commit.called

def test_update_success(mock_db):
    """测试成功更新记录"""
    service = BaseService(mock_db)
    mock_obj = MagicMock()
    mock_db.session.get.return_value = mock_obj
    
    result = service.update(TestModel, 1, name="new")
    assert result == mock_obj
    assert mock_db.session.commit.called

def test_get_paginated_with_filters(mock_db):
    """测试带过滤条件的分页查询"""
    service = BaseService(mock_db)
    query_mock = MagicMock()
    mock_db.session.query.return_value = query_mock
    
    # 测试等于过滤
    service.get_paginated(TestModel, name="test")
    assert query_mock.filter.call_count == 1
    
    # 测试模糊查询
    service.get_paginated(TestModel, name__ilike="%test%")
    assert query_mock.filter.call_count == 2
    assert "LIKE" in str(query_mock.filter.call_args[0][0])

def test_get_paginated_ordering(mock_db):
    """测试排序功能"""
    service = BaseService(mock_db)
    query_mock = MagicMock()
    mock_db.session.query.return_value = query_mock
    
    # 测试升序
    service.get_paginated(TestModel, order_by="name")
    assert query_mock.order_by.call_count == 1
    
    # 测试降序
    service.get_paginated(TestModel, order_by="-name")
    assert query_mock.order_by.call_count == 2
    assert "DESC" in str(query_mock.order_by.call_args[0][0])

def test_get_paginated_config(mock_db):
    """测试分页配置"""
    service = BaseService(mock_db)
    query_mock = MagicMock()
    mock_db.session.query.return_value = query_mock
    
    # 测试自定义每页数量
    with patch('flask.current_app') as mock_app:
        mock_app.config = {'ITEMS_PER_PAGE': 5}
        service.get_paginated(TestModel, per_page=10)
        assert query_mock.paginate.call_args[1]['per_page'] == 10

def test_error_handling(mock_db):
    """测试错误处理"""
    service = BaseService(mock_db)
    mock_db.session.commit.side_effect = Exception("DB error")
    
    with pytest.raises(Exception):
        service.create(TestModel, name="test")
    assert mock_db.session.rollback.called
