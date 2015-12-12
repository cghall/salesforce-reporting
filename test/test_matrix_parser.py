import json
import unittest

from reporting import MatrixParser


class MatrixParserTest(unittest.TestCase):

    def build_mock_report(self, fp):
        with open(fp) as json_file:
            report_data = json.load(json_file)
        return report_data

    def test_check_report_type_incorrect(self):
        self.assertRaises(ValueError, MatrixParser, self.build_mock_report('test/test_data/simple_summary.json'))

    def test_get_col_total_col_found(self):
        report = MatrixParser(self.build_mock_report('test/test_data/simple_matrix.json'))

        col_total = report.get_col_total('Birmingham')

        self.assertAlmostEqual(col_total, 86.80, 2)

    def test_get_col_total_nested_top_level(self):
        report = MatrixParser(self.build_mock_report('test/test_data/nested_matrix.json'))

        col_total = report.get_col_total('Birmingham')

        self.assertAlmostEqual(col_total, 86.32, 2)

    def test_get_col_total_nested_level_down(self):
        report = MatrixParser(self.build_mock_report("test/test_data/nested_matrix.json"))

        col_total = report.get_col_total('Holte School')

        self.assertAlmostEqual(col_total, 82.32, 2)

    def test_get_col_total_col_not_found_default(self):
        report = MatrixParser(self.build_mock_report('test/test_data/simple_matrix.json'))

        col_total = report.get_col_total('Nottingham')

        self.assertIsNone(col_total)

    def test_get_col_total_col_not_found_user_set(self):
        report = MatrixParser(self.build_mock_report('test/test_data/simple_matrix.json'))

        col_total = report.get_col_total('Nottingham', default='Region Not Available')

        self.assertEquals(col_total, 'Region Not Available')

    def test_get_row_total_row_found(self):
        report = MatrixParser(self.build_mock_report('test/test_data/simple_matrix.json'))

        row_total = report.get_row_total('January 2015')

        self.assertAlmostEqual(row_total, 89.01, 2)

    def test_series_for_col(self):
        matrix = MatrixParser(self.build_mock_report('test/test_data/basic_matrix.json'))

        series = matrix.series_down('London')

        self.assertEquals(series, {'CY2014': 385, 'CY2015': 339})

    def test_series_for_col_with_row_grouping(self):
        matrix = MatrixParser(self.build_mock_report('test/test_data/basic_matrix.json'))

        series = matrix.series_down('Birmingham', row_grp='CY2015')

        self.assertEquals(series["Online advert"], 4)
        self.assertEquals(series["Word of mouth"], 6)

    def test_series_for_col_with_col_grouping(self):
        matrix = MatrixParser(self.build_mock_report('test/test_data/nested_matrix.json'))

        series = matrix.series_down(['Brighton & Hove', 'Hove Park School'])

        self.assertAlmostEqual(series["November 2014"], 65.63, 2)