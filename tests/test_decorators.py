import unittest
from unittest.mock import patch, MagicMock
from tests.base import BaseTestCase
from app.decorators import prevent_self_operation

class TestDecorators(BaseTestCase):
    def test_prevent_self_operation(self):
        mock_func = MagicMock()
        decorated_func = prevent_self_operation(mock_func)
        
        # Test with different user IDs
        with patch('flask.request') as mock_request:
            mock_request.json = {'user_id': 1}
            
            # Same user ID should raise error
            with self.assertRaises(ValueError):
                decorated_func(1)
                
            # Different user ID should call original function
            decorated_func(2)
            mock_func.assert_called_once_with(2)
