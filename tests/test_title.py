import os
import sys
import unittest
from unittest.mock import patch, MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.title import main

class testTitleFn(unittest.TestCase):
    def setUp(self):
        self.common_titles = ["Welcome to nginx!", "RouterOS router configuration page"]
        self.mock_requestobject = MagicMock()
        self.mock_requestobject.text = "<html><title>{}</title></html>"
    @patch('app.title.subprocessors.query_shodan')
    @patch('app.title.subprocessors.query_censys')
    @patch('app.title.subprocessors.query_binaryedge')
    @patch('app.title.subprocessors.query_zoomeye')
    @patch('app.title.subprocessors.query_fofa')
    def test_unique_title(self, mock_query_fofa, mock_query_zoomeye, mock_query_binaryedge, mock_query_censys, mock_query_shodan):
        unique_title = "276F4776-FC90-4CA5-B044-C0E3D60934BF"
        self.mock_requestobject.text = self.mock_requestobject.text.format(unique_title)
        title_returned = main(self.mock_requestobject, doshodan=True, docensys=True, dobedge=True, dozoome=True, dofofa=True)
        self.assertEqual(title_returned, unique_title)
        mock_query_shodan.assert_called_with('http.title:"{}"'.format(unique_title))
        mock_query_censys.assert_called_with('services.http.response.html_title:"{}"'.format(unique_title))
        mock_query_binaryedge.assert_called_with('web.title:"{}"'.format(unique_title))
        mock_query_zoomeye.assert_called_with('title:"{}"'.format(unique_title))
        mock_query_fofa.assert_called_with('title={}'.format(unique_title))
    @patch('app.title.subprocessors.query_shodan')
    @patch('app.title.subprocessors.query_censys')
    @patch('app.title.subprocessors.query_binaryedge')
    @patch('app.title.subprocessors.query_zoomeye')
    @patch('app.title.subprocessors.query_fofa')
    def test_common_title(self, mock_query_fofa, mock_query_zoomeye, mock_query_binaryedge, mock_query_censys, mock_query_shodan):
        common_title = "Welcome to nginx!"
        self.mock_requestobject.text = self.mock_requestobject.text.format(common_title)
        title_returned = main(self.mock_requestobject, doshodan=True, docensys=True, dobedge=True, dozoome=True, dofofa=True)
        self.assertEqual(title_returned, common_title)
        mock_query_shodan.assert_not_called()
        mock_query_censys.assert_not_called()
        mock_query_binaryedge.assert_not_called()
        mock_query_zoomeye.assert_not_called()
        mock_query_fofa.assert_not_called()
    @patch('app.title.subprocessors.query_shodan')
    @patch('app.title.subprocessors.query_censys')
    @patch('app.title.subprocessors.query_binaryedge')
    @patch('app.title.subprocessors.query_zoomeye')
    @patch('app.title.subprocessors.query_fofa')
    def test_no_title(self, mock_query_fofa, mock_query_zoomeye, mock_query_binaryedge, mock_query_censys, mock_query_shodan):
        self.mock_requestobject.text = "<html></html>"
        title_returned = main(self.mock_requestobject, doshodan=True, docensys=True, dobedge=True, dozoome=True, dofofa=True)
        self.assertIsNone(title_returned)
        mock_query_shodan.assert_not_called()
        mock_query_censys.assert_not_called()
        mock_query_binaryedge.assert_not_called()
        mock_query_zoomeye.assert_not_called()
        mock_query_fofa.assert_not_called()

if __name__ == '__main__':
    unittest.main()
