import json
import unittest

from salesforce_reporting import ReportParser


class ReportParserTest(unittest.TestCase):

    def build_mock_report(self, fp):
        with open(fp) as json_file:
             report_data = json.load(json_file)
        return report_data

    def test_get_records_simple_tabular(self):
        report = ReportParser(self.build_mock_report('test/test_data/simple_tabular.json'))

        records = report.records()
        self.assertEquals(len(records), 34)
        self.assertEquals(records[0][0], 'P-0167')

    def test_get_record_dict_simple_tabular(self):
        report = ReportParser(self.build_mock_report('test/test_data/simple_tabular.json'))

        records = report.records_dict()
        field_value = records[0]["Programme: Programme Number"]

        self.assertEquals(len(records), 34)
        self.assertIsNotNone(field_value)

    def test_get_records_simple_summary(self):
        report = ReportParser(self.build_mock_report('test/test_data/simple_summary.json'))

        records = report.records()

        self.assertEquals(len(records), 34)

    def test_get_record_dict_simple_summary(self):
        report = ReportParser(self.build_mock_report('test/test_data/simple_summary.json'))

        records = report.records_dict()
        field_value = records[0]["Programme: Programme Number"]

        self.assertEquals(len(records), 34)
        self.assertIsNotNone(field_value)

    def test_get_records_basic_matrix(self):
        report = ReportParser(self.build_mock_report('test/test_data/basic_matrix.json'))

        records = report.records()

        self.assertEquals(len(records), 1427)

    def test_get_records_without_details(self):
        report = ReportParser(self.build_mock_report('test/test_data/multiple_matrix.json'))

        self.assertRaises(ValueError, report.records)

    def test_get_records_dict_without_details(self):
        report = ReportParser(self.build_mock_report('test/test_data/multiple_matrix.json'))

        self.assertRaises(ValueError, report.records_dict)

    def test_get_grand_total_on_summary_report(self):
        report = ReportParser(self.build_mock_report('test/test_data/simple_summary.json'))

        grand_total = report.get_grand_total()

        self.assertEquals(grand_total, 241)

    def test_get_grand_total_on_matrix_report(self):
        report = ReportParser(self.build_mock_report('test/test_data/simple_matrix.json'))

        grand_total = report.get_grand_total()

        self.assertAlmostEqual(grand_total, 85.85, 2)
