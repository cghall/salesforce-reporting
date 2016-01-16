=====================
Salesforce Reporting
=====================

Get data straight from your Salesforce reports via python using the Analytics API.

-------
Install
-------

Install via pip::

    pip install salesforce-reporting

---------
Examples
---------
^^^^^^^^^^^^^^
Authentication
^^^^^^^^^^^^^^

Connect to the Salesforce Analytics API using password authentication and request Report data using
the Salesforce Id of the Report::

    from salesforce_reporting import Connection

    sf = Connection(username='your_username', password='your_password', security_token='your_token')
    sf.get_report('report_id', includeDetails=True)

^^^^^^^^^^^^^^^^^^^^^^^
Get records from a report
^^^^^^^^^^^^^^^^^^^^^^^

Use the ReportParser to access all the records included in a report (in list format)::

   report = my_sf.get_report('report_id', includeDetails=True)
   parser = salesforce_reporting.ReportParser(report)

   parser.records()

The records_dict() method can also be used to return records in the form of a list of dicts
in {field: value, field: value} format::

   parser.records_dict()


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Extract series from matrix report
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For a matrix report grouped across the top by Calendar Month doing::

   report = my_sf.get_report('report_id')
   matrix_parser = salesforce_reporting.MatrixParser(report)

   matrix_parser.series_down('May 2012')

Will return all values for 'May 2012' as values in a dictionary with the row groupings as keys.

------------
Coming Soon
------------
- Access to Dashboards

-----------------
Author & License
-----------------
MIT License. Created by Chris Hall.

