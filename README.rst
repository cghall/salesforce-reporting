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

Connect to the Salesforce Analytics API and request data from a report::

    import salesforce_reporting

    my_sf = salesforce_reporting.Connection('your_id', 'your_secret',
    'your_username', 'your_password', 'your_instance')
    my_sf.get_report('report_id', includeDetails=True)

^^^^^^^^^^^^^^^^^^^^^^^
Get records from report
^^^^^^^^^^^^^^^^^^^^^^^

Use the ReportParser to access all the records included in a report::

   report = my_sf.get_report('report_id', includeDetails=True)
   parser = salesforce_reporting.ReportParser(report)

   parser.records()

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
- Simplified Authentication process
- Access to Dashboards

-----------------
Author & License
-----------------
MIT License. Created by Chris Hall.

