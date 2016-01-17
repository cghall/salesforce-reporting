import json
import unittest

from salesforce_reporting import ReportParser


class ReportParserTest(unittest.TestCase):

    def build_mock_report(self, fp):
        with open(fp) as json_file:
             report_data = json.load(json_file)
        return report_data

    def test_get_records_simple_tabular(self):
        report = ReportParser(self.build_mock_report('test/test_data/tabular_basic.json'))

        records = report.records()
        self.assertEquals(len(records), 20)
        self.assertEquals(records[1][2], 'James')

    def test_get_record_dict_simple_tabular(self):
        report = ReportParser(self.build_mock_report('test/test_data/tabular_basic.json'))

        records = report.records_dict()
        field_value = records[0]["Mailing Street"]

        self.assertEquals(len(records), 20)
        self.assertIsNotNone(field_value)

    def test_get_records_simple_summary(self):
        report = ReportParser(self.build_mock_report('test/test_data/summary_basic_single_group.json'))

        records = report.records()

        self.assertEquals(len(records), 13)
        self.assertEquals(records[0][0], 'Chris Hall')

    def test_get_record_dict_simple_summary(self):
        report = ReportParser(self.build_mock_report('test/test_data/summary_basic_single_group.json'))

        records = report.records_dict()
        field_value = records[0]["Created Date"]

        self.assertEquals(len(records), 13)
        self.assertIsNotNone(field_value)

    def test_get_records_basic_matrix(self):
        report = ReportParser(self.build_mock_report('test/test_data/matrix_basic.json'))

        records = report.records()

        self.assertEquals(len(records), 18)

    def test_get_records_without_details(self):
        report = ReportParser(self.build_mock_report('test/test_data/matrix_complex.json'))

        self.assertRaises(ValueError, report.records)

    def test_get_records_dict_without_details(self):
        report = ReportParser(self.build_mock_report('test/test_data/matrix_complex.json'))

        self.assertRaises(ValueError, report.records_dict)

    def test_get_grand_total_on_summary_report(self):
        report = ReportParser(self.build_mock_report('test/test_data/summary_basic_single_group.json'))

        grand_total = report.get_grand_total()

        self.assertEquals(grand_total, 9469000000)

    def test_get_grand_total_on_matrix_report(self):
        report = ReportParser(self.build_mock_report('test/test_data/matrix_basic.json'))

        grand_total = report.get_grand_total()

        self.assertEquals(grand_total, 3645000)
