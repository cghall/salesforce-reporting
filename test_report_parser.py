import json
import unittest

from reporting import ReportParser


class ReportParserTest(unittest.TestCase):

    def build_mock_report(self, fp):
        with open(fp) as json_file:
             report_data = json.load(json_file)
        return report_data

    def test_get_grand_total_on_summary_report(self):
        report = ReportParser(self.build_mock_report('test/test_data/simple_summary.json'))

        grand_total = report.get_grand_total()

        self.assertEquals(grand_total, 291)

    def test_get_grand_total_on_matrix_report(self):
        report = ReportParser(self.build_mock_report('test/test_data/simple_matrix.json'))

        grand_total = report.get_grand_total()

        self.assertAlmostEqual(grand_total, 85.85, 2)