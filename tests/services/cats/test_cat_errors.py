import pytest
from unittest.mock import MagicMock
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
    
    return db

@pytest.fixture
def cat_service(mock_db):
    service = CatService(mock_db)
    service.db = mock_db
    return service

@pytest.mark.errors
class TestCatErrors:
    def test_get_with_db_error(self, cat_service, mock_db):
        mock_db.session.get.side_effect = SQLAlchemyError("DB Error")
        with pytest.raises(SQLAlchemyError):
            cat_service.get(1)

    def test_create_cat_with_db_error_on_add(self, cat_service, mock_db):
        mock_db.session.add.side_effect = SQLAlchemyError("DB Error")
        with pytest.raises(SQLAlchemyError):
            cat_service.create_cat(user_id=1, name='ErrorCat', age=2)

    def test_update_with_db_error(self, cat_service, mock_db):
        mock_cat = MagicMock()
        mock_cat.user_id = 1
        mock_db.session.get.return_value = mock_cat
        mock_db.session.commit.side_effect = SQLAlchemyError("DB Error")
        with pytest.raises(SQLAlchemyError):
            cat_service.update(1, 1, name='ErrorUpdate')

    def test_delete_with_db_error(self, cat_service, mock_db):
        mock_cat = MagicMock()
        mock_cat.user_id = 1
        mock_db.session.get.return_value = mock_cat
        mock_db.session.commit.side_effect = SQLAlchemyError("DB Error")
        with pytest.raises(SQLAlchemyError):
            cat_service.delete(1, 1)

    def test_get_with_model_class_db_error(self, cat_service, mock_db):
        mock_db.session.query.return_value.first.side_effect = SQLAlchemyError("DB Error")
        with pytest.raises(SQLAlchemyError):
            cat_service.get(Cat)

    def test_create_cat_missing_user_id(self, cat_service, mock_db):
        with pytest.raises(ValueError):
            cat_service.create_cat(user_id=None, name='NoOwnerCat', age=2)

    def test_update_invalid_data(self, cat_service, mock_db):
        mock_cat = MagicMock()
        mock_cat.user_id = 1
        mock_db.session.get.return_value = mock_cat
        with pytest.raises(ValueError):
            cat_service.update(1, 1, age=-1)
