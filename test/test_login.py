import unittest

from salesforce_reporting import Connection, AuthenticationFailure


class ConnectionTest(unittest.TestCase):

    @unittest.skip("Skip for normal tests - runtime length")
    def test_incorrect_password_raises_exception(self):
        self.assertRaises(AuthenticationFailure, Connection, username="fake@user.com", password="1234",
                          security_token="5678")
