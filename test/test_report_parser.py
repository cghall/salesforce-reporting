from salesforce_reporting import ReportParser
from test.common import ParserTest


class ReportParserTest(ParserTest):

    def test_get_records_simple_tabular(self):
        report = ReportParser(self.build_mock_report('tabular_basic'))

        records = report.records()
        self.assertEquals(len(records), 20)
        self.assertEquals(records[1][2], 'James')

    def test_get_record_dict_simple_tabular(self):
        report = ReportParser(self.build_mock_report('tabular_basic'))

        records = report.records_dict()
        field_value = records[0]["Mailing Street"]

        self.assertEquals(len(records), 20)
        self.assertIsNotNone(field_value)

    def test_get_records_simple_summary(self):
        report = ReportParser(self.build_mock_report('summary_basic_single_group'))

        records = report.records()

        self.assertEquals(len(records), 13)
        self.assertEquals(records[0][0], 'Chris Hall')

    def test_get_record_dict_simple_summary(self):
        report = ReportParser(self.build_mock_report('summary_basic_single_group'))

        records = report.records_dict()
        field_value = records[0]["Created Date"]

        self.assertEquals(len(records), 13)
        self.assertIsNotNone(field_value)

    def test_get_records_basic_matrix(self):
        report = ReportParser(self.build_mock_report('matrix_basic'))

        records = report.records()

        self.assertEquals(len(records), 18)

    def test_get_records_without_details(self):
        report = ReportParser(self.build_mock_report('matrix_complex'))

        self.assertRaises(ValueError, report.records)

    def test_get_records_dict_without_details(self):
        report = ReportParser(self.build_mock_report('matrix_complex'))

        self.assertRaises(ValueError, report.records_dict)

    def test_get_grand_total_on_summary_report(self):
        report = ReportParser(self.build_mock_report('summary_basic_single_group'))

        grand_total = report.get_grand_total()

        self.assertEquals(grand_total, 9469000000)

    def test_get_grand_total_on_matrix_report(self):
        report = ReportParser(self.build_mock_report('matrix_basic'))

        grand_total = report.get_grand_total()

        self.assertEquals(grand_total, 3645000)
