import json
import os
import unittest


class ParserTest(unittest.TestCase):

    def build_mock_report(self, report):
        path = os.path.join(os.path.dirname(__file__), 'test_data', report) + '.json'
        path = os.path.abspath(path)
        with open(path) as f:
            return json.load(f)
