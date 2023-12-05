import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.opendir import main

class TestOpenDirectoryCheck(unittest.TestCase):
    @patch('app.opendir.log')
    def test_open_directory_detected(self, mock_log):
        mock_request = MagicMock()
        mock_request.text = 'Index of /some_directory'
        mock_request.url = 'http://example.com/some_directory'
        main(mock_request)
        mock_log.info.assert_called_with('potential open directory - %s', 'http://example.com/some_directory')

    @patch('app.opendir.log')
    def test_no_open_directory_detected(self, mock_log):
        mock_request = MagicMock()
        mock_request.text = 'welcome to my site'
        mock_request.url = 'http://example.com'
        main(mock_request)
        mock_log.debug.assert_called_with('%s does not appear to be an open directory', 'http://example.com')

if __name__ == '__main__':
    unittest.main()
