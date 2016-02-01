##Salesforce Reporting##

[![Build Status](https://travis-ci.org/cghall/salesforce-reporting.svg?branch=master)](https://travis-ci.org/cghall/salesforce-reporting)

Get data straight from your Salesforce reports via python using the [Analytics API](https://resources.docs.salesforce.com/sfdc/pdf/salesforce_analytics_rest_api.pdf).

###Install###

Install via pip - `pip install salesforce-reporting`

###Authentication###

Connect to the Salesforce Analytics API using password authentication:
```python
from salesforce_reporting import Connection

sf = Connection(username='your_username', password='your_password', security_token='your_token')
```

###Get records from a report###

Use the `Connection.get_report()` method to request report data and then use ReportParser to access all the records included in a report (in list format if you use the `ReportParser.records()` method):
```python
from salesforce_reporting import Connection, ReportParser

sf = Connection(username='your_username', password='your_password', security_token='your_token')
report = sf.get_report('report_id', includeDetails=True)
parser = salesforce_reporting.ReportParser(report)

parser.records()
```
The `ReportParser.records_dict()` method can also be used to return records in the form of a list of dicts
in `{field: value, field: value}` format.

###Extract series from matrix report###

For a matrix report you can return the values in a column grouping by using `MatrixParser.series_down()` which takes the column name as an argument. For example, given a matrix report grouped by Calendar Month:
```python
report = my_sf.get_report('report_id')
matrix_parser = salesforce_reporting.MatrixParser(report)

matrix_parser.series_down('Jan 2016')
```
This will return all values for 'Jan 2016' as values in a dictionary with the row groupings as keys.

Similarly you can use `MatrixParser.series_across()` to get the values in a particular row.

###Coming Soon###
- Access to Dashboards

###Author & License###
MIT License. Created by Chris Hall.

