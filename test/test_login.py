import unittest

from salesforce_reporting import Connection, AuthenticationFailure


class ConnectionTest(unittest.TestCase):

    def test_incorrect_password_raises_exception(self):
        self.assertRaises(AuthenticationFailure, Connection, username="fake@user.com", password="1234",
                          security_token="5678")

    def test_default_login_url(self):
        self.assertEquals(Connection._get_login_url(False, 'v29.0'),
                          'https://login.salesforce.com/services/Soap/u/v29.0')

    def test_sandbox_url_with_different_api(self):
        self.assertEquals(Connection._get_login_url(True, 'v33.0'),
                          'https://test.salesforce.com/services/Soap/u/v33.0')
