import unittest

from salesforce_reporting import MatrixParser
from test.common import ParserTest


class MatrixParserTest(ParserTest):
    def test_check_report_type_incorrect(self):
        self.assertRaises(ValueError, MatrixParser, self.build_mock_report('summary_basic_single_group'))

    def test_get_col_total_col_found(self):
        report = MatrixParser(self.build_mock_report('matrix_basic'))

        col_total = report.get_col_total('September 2013')

        self.assertEquals(col_total, 120000)

    def test_get_col_total_nested_top_level(self):
        report = MatrixParser(self.build_mock_report('matrix_complex'))

        col_total = report.get_col_total('Q3-2013')

        self.assertEquals(col_total, 5600000000)

    @unittest.skip("Functionality not yet added")
    def test_get_col_total_nested_level_down(self):
        report = MatrixParser(self.build_mock_report("matrix_complex"))

        col_total = report.get_col_total('December 2013')

        self.assertAlmostEqual(col_total, 5739000000)

    def test_get_col_total_col_not_found_default(self):
        report = MatrixParser(self.build_mock_report('matrix_basic'))

        col_total = report.get_col_total('January 2015')

        self.assertIsNone(col_total)

    def test_get_col_total_col_not_found_user_set(self):
        report = MatrixParser(self.build_mock_report('matrix_complex'))

        col_total = report.get_col_total('Q1-2016', default='No data available for period selected.')

        self.assertEquals(col_total, 'No data available for period selected.')

    def test_get_row_total_row_found(self):
        report = MatrixParser(self.build_mock_report('matrix_basic'))

        row_total = report.get_row_total('New Customer')

        self.assertEquals(row_total, 1790000)

    def test_series_for_col(self):
        matrix = MatrixParser(self.build_mock_report('matrix_basic'))

        series = matrix.series_down('March 2014')

        self.assertEquals(series["New Customer"], 430000)

    def test_series_for_row(self):
        matrix = MatrixParser(self.build_mock_report('matrix_basic'))

        series = matrix.series_across('New Customer')

        self.assertEquals(series["May 2013"], 75000)

    def test_series_for_col_with_row_grouping(self):
        matrix = MatrixParser(self.build_mock_report('matrix_basic'))

        series = matrix.series_down('December 2013', row_groups='Existing Customer - Upgrade')

        self.assertEquals(series["University of Arizona"], 90000)
        self.assertEquals(series["Edge Communications"], 60000)

    def test_series_down_with_multiple_col_groupings(self):
        matrix = MatrixParser(self.build_mock_report('matrix_complex'))

        series = matrix.series_down(['Q4-2013', 'October 2013'])

        self.assertEquals(series["New Customer"], 0)

    def test_series_down_multiple_groupings_and_metrics(self):
        matrix = MatrixParser(self.build_mock_report('matrix_complex'))

        series_record_count = matrix.series_down(['Q4-2013', 'October 2013'], row_groups='Existing Customer - Upgrade',
                                                 value_position=2)
        series_annual_revenue = matrix.series_down(['Q4-2013', 'October 2013'], row_groups='Existing Customer - Upgrade',
                                                   value_position=0)

        self.assertEquals(series_record_count["GenePoint"], 1)
        self.assertEquals(series_annual_revenue["GenePoint"], 30000000)

    def test_series_across_multiple_row_groupings(self):
        matrix = MatrixParser(self.build_mock_report('matrix_basic'))

        series = matrix.series_across(["New Customer", "GenePoint"])

        self.assertEquals(series["December 2013"], 85000)

    def test_series_across_multiple_groupings_and_metrics(self):
        matrix = MatrixParser(self.build_mock_report('matrix_complex'))

        series = matrix.series_across(['New Customer', 'Express Logistics and Transport'],
                                      col_groups='Q1-2014', value_position=1)

        self.assertEquals(series["March 2014"], 220000)
