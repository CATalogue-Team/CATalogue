import pytest
from unittest.mock import MagicMock, patch
from app.services.base_service import BaseService
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class MockModel(Base):
    """测试模型类"""
    __tablename__ = 'mock_model'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    nullable_field = Column(String, nullable=True)
    
    def __init__(self, id=1, name='Test', nullable_field=None):
        self.id = id
        self.name = name
        self.nullable_field = nullable_field

@pytest.fixture
def mock_db():
    db = MagicMock()
    session = MagicMock()
    db.session = session
    return db

@pytest.fixture
def base_service(mock_db):
    return BaseService(mock_db)

class TestBaseService:
    def test_init_validation(self):
        """测试初始化验证"""
        with pytest.raises(ValueError, match="db参数不能为None"):
            BaseService(None)
            
        invalid_db = MagicMock()
        del invalid_db.session
        with pytest.raises(ValueError, match="db对象必须包含session属性"):
            BaseService(invalid_db)
            
        no_get_db = MagicMock()
        no_get_db.session = MagicMock()
        del no_get_db.session.get
        with pytest.raises(ValueError, match="db.session必须支持get方法"):
            BaseService(no_get_db)

    def test_get_all(self, base_service, mock_db):
        """测试获取所有记录"""
        mock_db.session.query.return_value.all.return_value = [MockModel()]
        result = base_service.get_all(MockModel)
        assert len(result) == 1
        assert isinstance(result[0], MockModel)
        mock_db.session.query.assert_called_once_with(MockModel)

    def test_create_validation(self, base_service, mock_db):
        """测试创建记录时的字段验证"""
        class RequiredFieldModel(Base):
            __tablename__ = 'required_model'
            id = Column(Integer, primary_key=True)
            required_field = Column(String, nullable=False)
            
        with pytest.raises(ValueError, match="缺少必填字段: required_field"):
            base_service.create(RequiredFieldModel)

        mock_db.session.commit.side_effect = Exception("DB Error")
        with pytest.raises(Exception):
            base_service.create(MockModel, name="Test")
        mock_db.session.rollback.assert_called_once()

    def test_pagination(self, base_service, mock_db):
        """测试分页查询"""
        from flask_sqlalchemy.pagination import Pagination
        mock_pagination = MagicMock(spec=Pagination)
        
        # 设置mock链
        query_mock = mock_db.session.query.return_value
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.paginate.return_value = mock_pagination
        
        result = base_service.get_paginated(
            MockModel,
            page=2,
            per_page=5,
            order_by='name',
            name__ilike='test%'
        )
        
        assert result is mock_pagination
        mock_db.session.query.assert_called_once_with(MockModel)
        query_mock.filter.assert_called_once()
        query_mock.order_by.assert_called_once()
        query_mock.paginate.assert_called_once_with(
            page=2,
            per_page=5,
            error_out=False
        )

    def test_update_non_existent(self, base_service, mock_db):
        """测试更新不存在的记录"""
        mock_db.session.get.return_value = None
        result = base_service.update(MockModel, 999, name="New")
        assert result is None

    def test_delete_non_existent(self, base_service, mock_db):
        """测试删除不存在的记录"""
        mock_db.session.get.return_value = None
        result = base_service.delete(MockModel, 999)
        assert result is False
        
    def test_create_success(self, base_service, mock_db):
        """测试成功创建记录"""
        test_obj = MockModel(id=1, name="Test")
        mock_db.session.commit.return_value = None
        
        result = base_service.create(MockModel, name="Test")
        
        assert isinstance(result, MockModel)
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
        
    def test_update_success(self, base_service, mock_db):
        """测试成功更新记录"""
        test_obj = MockModel(id=1, name="Old")
        mock_db.session.get.return_value = test_obj
        
        result = base_service.update(MockModel, 1, name="New")
        
        assert result is test_obj
        assert test_obj.name == "New"
        mock_db.session.commit.assert_called_once()
        
    def test_delete_success(self, base_service, mock_db):
        """测试成功删除记录"""
        test_obj = MockModel(id=1)
        mock_db.session.get.return_value = test_obj
        
        result = base_service.delete(MockModel, 1)
        
        assert result is True
        mock_db.session.delete.assert_called_once_with(test_obj)
        mock_db.session.commit.assert_called_once()
        
    def test_pagination_desc_order(self, base_service, mock_db):
        """测试降序排序分页查询"""
        from flask_sqlalchemy.pagination import Pagination
        mock_pagination = MagicMock(spec=Pagination)
        
        query_mock = mock_db.session.query.return_value
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.paginate.return_value = mock_pagination
        
        result = base_service.get_paginated(
            MockModel,
            page=1,
            per_page=10,
            order_by='-id'
        )
        
        assert result is mock_pagination
        query_mock.order_by.assert_called_once()
        
    def test_init_with_invalid_db(self):
        """测试使用无效db对象初始化"""
        with pytest.raises(ValueError, match="db参数不能为None"):
            BaseService(None)
            
        invalid_db = MagicMock()
        del invalid_db.session
        with pytest.raises(ValueError, match="db对象必须包含session属性"):
            BaseService(invalid_db)
            
        no_get_db = MagicMock()
        no_get_db.session = MagicMock()
        del no_get_db.session.get
        with pytest.raises(ValueError, match="db.session必须支持get方法"):
            BaseService(no_get_db)
            
    def test_create_invalid_model(self, base_service, mock_db):
        """测试使用无效模型类创建记录"""
        class InvalidModel:
            pass
            
        with pytest.raises(ValueError, match="无效的模型类 - 必须继承自SQLAlchemy模型"):
            base_service.create(InvalidModel)
            
    @patch('app.services.base_service.logger')
    def test_init_logging(self, mock_logger):
        """测试初始化日志记录"""
        mock_db = MagicMock()
        mock_db.session = MagicMock()
        mock_db.session.get = MagicMock()
        
        service = BaseService(mock_db)
        mock_logger.info.assert_called_once_with("BaseService initialized with db: %s", mock_db)
        
    def test_pagination_exception(self, base_service, mock_db):
        """测试分页查询异常处理"""
        mock_query = MagicMock()
        mock_db.session.query.return_value = mock_query
        mock_query.paginate.side_effect = Exception("DB Error")

        with pytest.raises(Exception, match="DB Error"):
            base_service.get_paginated(MockModel)

        mock_db.session.rollback.assert_called_once()
