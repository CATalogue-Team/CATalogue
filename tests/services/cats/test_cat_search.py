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
    session.query.return_value.filter = MagicMock()
    session.query.return_value.filter.return_value.filter = MagicMock()
    session.query.return_value.filter.return_value.filter.return_value.all = MagicMock(return_value=[])
    
    return db

@pytest.fixture
def cat_service(mock_db):
    service = CatService(mock_db)
    service.db = mock_db
    return service

@pytest.mark.search
class TestCatSearch:
    def test_search_all_conditions(self, cat_service, mock_db):
        mock_cats = [MagicMock(), MagicMock()]
        query_mock = MagicMock()
        
        mock_db.session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = mock_cats
        
        results = cat_service.search(query="test", min_age=1, max_age=10, breed="Persian", is_adopted=False)
        assert len(results) == 2
        assert query_mock.filter.call_count == 5  # 5个过滤条件(包括ilike)
        assert query_mock.all.call_count == 1

    def test_search_no_conditions(self, cat_service, mock_db):
        mock_cats = [MagicMock(), MagicMock(), MagicMock()]
        mock_db.session.query.return_value.all.return_value = mock_cats
        results = cat_service.search()
        assert len(results) == 3

    def test_search_partial_conditions(self, cat_service, mock_db):
        mock_cats = [MagicMock()]
        mock_db.session.query.return_value.filter.return_value.filter.return_value.all.return_value = mock_cats
        results = cat_service.search(query="kitty", min_age=2)
        assert len(results) == 1

    def test_search_empty_result(self, cat_service, mock_db):
        mock_db.session.query.return_value.filter.return_value.filter.return_value.all.return_value = []
        results = cat_service.search(query="nonexistent")
        assert len(results) == 0

    def test_search_case_insensitive(self, cat_service, mock_db):
        mock_cats = [MagicMock()]
        mock_db.session.query.return_value.filter.return_value.filter.return_value.all.return_value = mock_cats
        results = cat_service.search(query="KITTY", breed="persian")
        assert len(results) == 1
