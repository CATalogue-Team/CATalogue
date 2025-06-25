import pytest
from unittest.mock import MagicMock, patch
from app.services.cat_service import CatService
from app.models import Cat
from sqlalchemy.exc import SQLAlchemyError

@pytest.fixture
def mock_db():
    db = MagicMock()
    session = MagicMock()
    
    session.commit = MagicMock(return_value=None)
    session.rollback = MagicMock(return_value=None)
    session.db = db
    db.session = session
    
    session.query = MagicMock()
    session.query.return_value.filter_by = MagicMock()
    session.query.return_value.filter_by.return_value.first = MagicMock(return_value=None)
    
    session.get = MagicMock()
    session.add = MagicMock()
    session.flush = MagicMock()
    session.expunge = MagicMock()
    session.delete = MagicMock(return_value=True)
    
    session.begin = MagicMock(return_value=session)
    session.__enter__ = MagicMock(return_value=session)
    session.__exit__ = MagicMock(return_value=None)
    
    return db

@pytest.fixture
def cat_service(mock_db):
    service = CatService(mock_db)
    service.db = mock_db
    return service

@pytest.mark.crud
class TestCatCRUD:
    def test_create_cat_empty_name(self, cat_service, mock_db):
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = None
        with pytest.raises(ValueError):
            cat_service.create_cat(user_id=1, name='', age=2)

    def test_create_cat_max_age(self, cat_service, mock_db):
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = None
        cat = cat_service.create_cat(user_id=1, name='OldCat', age=30)
        assert cat.age == 30

    def test_create_cat_db_rollback(self, cat_service, mock_db):
        mock_db.session.commit.side_effect = Exception("DB Error")
        with pytest.raises(Exception):
            cat_service.create_cat(user_id=1, name='RollbackCat', age=3)
        mock_db.session.commit.assert_called_once()
        mock_db.session.rollback.assert_called_once()

    def test_update_permission_check(self, cat_service, mock_db):
        mock_cat = MagicMock()
        mock_cat.user_id = 2
        mock_db.session.get.return_value = mock_cat
        with pytest.raises(PermissionError):
            cat_service.update(1, 1, name='NewName')

    def test_delete_permission_check(self, cat_service, mock_db):
        mock_cat = MagicMock()
        mock_cat.user_id = 2
        mock_db.session.get.return_value = mock_cat
        with pytest.raises(PermissionError):
            cat_service.delete(1, 1)

    def test_update_nonexistent_cat(self, cat_service, mock_db):
        mock_db.session.get.return_value = None
        with pytest.raises(ValueError):
            cat_service.update(999, 1, name='Nonexistent')

    def test_delete_nonexistent_cat(self, cat_service, mock_db):
        mock_db.session.get.return_value = None
        with pytest.raises(ValueError):
            cat_service.delete(999, 1)

    def test_create_cat_invalid_age(self, cat_service, mock_db):
        with pytest.raises(ValueError):
            cat_service.create_cat(user_id=1, name='InvalidAge', age=-1)
        with pytest.raises(ValueError):
            cat_service.create_cat(user_id=1, name='InvalidAge', age=31)

    def test_create_cat_duplicate_name(self, cat_service, mock_db):
        mock_cat = MagicMock()
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = mock_cat
        with pytest.raises(ValueError):
            cat_service.create_cat(user_id=1, name='DuplicateCat', age=2)

    def test_update_success(self, cat_service, mock_db):
        mock_cat = MagicMock()
        mock_cat.user_id = 1
        mock_db.session.get.return_value = mock_cat
        updated_cat = cat_service.update(1, 1, name='UpdatedName')
        assert updated_cat is not None

    def test_update_failure(self, cat_service, mock_db):
        """测试父类update返回False的情况"""
        mock_cat = MagicMock()
        mock_cat.user_id = 1
        mock_db.session.get.return_value = mock_cat
        
        # 直接模拟BaseService.update方法返回False
        with patch('app.services.cat_service.BaseService.update', return_value=False):
            with pytest.raises(ValueError, match="更新猫咪信息失败"):
                cat_service.update(1, 1, name='ShouldFail')

    def test_delete_success(self, cat_service, mock_db):
        mock_cat = MagicMock()
        mock_cat.user_id = 1
        mock_db.session.get.return_value = mock_cat
        result = cat_service.delete(1, 1)
        assert result is True
        assert mock_db.session.delete.called

    def test_get_with_model_class(self, cat_service, mock_db):
        mock_cat = MagicMock()
        mock_db.session.query.return_value.first.return_value = mock_cat
        result = cat_service.get(Cat)
        assert result == mock_cat

    def test_get_invalid_type(self, cat_service, mock_db):
        with pytest.raises(ValueError):
            cat_service.get("invalid_id")

    def test_create_cat_success(self, cat_service, mock_db):
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = None
        result = cat_service.create_cat(user_id=1, name='TestCat', age=3)
        assert result is not None
        assert mock_db.session.add.called
        assert mock_db.session.commit.called

    def test_update_with_model_class(self, cat_service, mock_db):
        mock_cat = MagicMock()
        mock_cat.user_id = 1
        mock_db.session.get.return_value = mock_cat
        result = cat_service.update(1, 1, name='UpdatedName')
        assert result is not None
