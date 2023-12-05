import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import pagespider

class TestPageSpider(unittest.TestCase):
    @patch('app.pagespider.requests.get')
    def test_main(self, mock_get):
        html_content = '''
            <html>
            <body>
                <a href="https://www.example.com">Example</a>
                <a href="http://sub.example.com">Subdomain</a>
                <a href="https://ciadotgov4sjwlzihbbgxnqg3xiyrg7so2r2o3lt5wz5ypk4sxyjstad.onion">Example Onion</a>
                <a href="mailto:test@example.com">Email</a>
                <a href="//protocol-relative.com">Protocol Relative</a>
            </body>
            </html>
        '''
        mock_response = MagicMock()
        mock_response.content = html_content.encode()
        mock_response.url = 'https://www.example.com'
        mock_get.return_value = mock_response
        result = pagespider.main(mock_response, False, False)
        expected = {
            'samedomain': ['https://www.example.com'],
            'extdomain': ['http://sub.example.com', 'https://ciadotgov4sjwlzihbbgxnqg3xiyrg7so2r2o3lt5wz5ypk4sxyjstad.onion', 'https://protocol-relative.com'],
            'emails': ['test@example.com']
        }
        for key in expected:
            if isinstance(expected[key], list):
                expected[key].sort()
        for key in result:
            if isinstance(result[key], list):
                result[key].sort()
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
