import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.services.cat_service import CatService
from app.models import Cat, CatImage
from werkzeug.datastructures import FileStorage

@pytest.fixture
def mock_db():
    db = MagicMock()
    session = MagicMock()
    db.session = session
    return db

@pytest.fixture
def cat_service(mock_db):
    return CatService(mock_db)

class TestCatService:
    # 已有测试用例
    def test_get_cat_stats(self, cat_service, mock_db):
        """测试获取猫咪统计信息"""
        # ... 保留原有实现 ...

    # 新增测试用例
    def test_create_cat(self, cat_service, mock_db):
        """测试创建猫咪"""
        # 模拟数据库查询结果（名称不存在）
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = None
        
        # 模拟Cat类
        mock_cat = MagicMock()
        with patch('app.services.cat_service.Cat', return_value=mock_cat):
            # 调用服务方法
            result = cat_service.create_cat(
                user_id=1,
                name='Fluffy',
                breed='Persian',
                age=2,
                description='A cute cat'
            )
            
            # 验证结果
            assert result == mock_cat
            mock_db.session.add.assert_called_once_with(mock_cat)
            mock_db.session.commit.assert_called_once()
            mock_db.session.query.return_value.filter_by.assert_called_once_with(name='Fluffy')

    def test_get(self, cat_service, mock_db):
        """测试通过ID获取猫咪"""
        mock_cat = MagicMock()
        mock_db.session.get.return_value = mock_cat
        
        result = cat_service.get(1)
        
        assert result == mock_cat
        mock_db.session.get.assert_called_once_with(Cat, 1)

    def test_update(self, cat_service, mock_db):
        """测试更新猫咪信息"""
        mock_cat = MagicMock()
        mock_cat.user_id = 1  # 设置用户ID避免权限错误
        mock_db.session.get.return_value = mock_cat
        
        result = cat_service.update(1, 1, name='Updated Name')
        
        assert result == mock_cat
        assert mock_cat.name == 'Updated Name'
        mock_db.session.commit.assert_called_once()

    def test_create_cat_duplicate_name(self, cat_service, mock_db):
        """测试创建重名猫咪"""
        # 模拟数据库查询返回已有猫咪
        existing_cat = MagicMock()
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = existing_cat
        
        # 调用服务方法并验证异常
        with pytest.raises(ValueError) as excinfo:
            cat_service.create_cat(
                user_id=1,
                name='Fluffy',
                breed='Persian',
                age=2,
                description='A cute cat'
            )
        
        assert "猫咪名称'Fluffy'已存在" in str(excinfo.value)
        mock_db.session.add.assert_not_called()
        mock_db.session.commit.assert_not_called()

    def test_create_cat_invalid_age(self, cat_service, mock_db):
        """测试创建年龄无效的猫咪"""
        # 模拟数据库查询结果（名称不存在）
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = None
        
        # 调用服务方法并验证异常
        with pytest.raises(ValueError) as excinfo:
            cat_service.create_cat(
                user_id=1,
                name='Fluffy',
                breed='Persian',
                age=-1,
                description='A cute cat'
            )
        
        assert "猫咪年龄必须在0-30岁之间" in str(excinfo.value)
        mock_db.session.add.assert_not_called()
        mock_db.session.commit.assert_not_called()

    def test_delete(self, cat_service, mock_db):
        """测试删除猫咪"""
        mock_cat = MagicMock()
        mock_cat.user_id = 1  # 设置用户ID避免权限错误
        mock_db.session.get.return_value = mock_cat
        
        result = cat_service.delete(1, 1)
        
        assert result is True
        mock_db.session.delete.assert_called_once_with(mock_cat)
        mock_db.session.commit.assert_called_once()
