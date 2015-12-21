# SalesforceReporting.Py
Get data straight from your Salesforce reports via python using the Analytics API.

# Install
Coming soon.

# Examples
Connect to the Salesforce Analytics API and request data from a report.
```python
import salesforcereporting
    
my_sf = salesforcereporting.Connection('your_id', 'your_secret', 'your_username', 
                                           'your_password', 'your_instance')
my_sf.get_report('report_id', includeDetails=True)
```
Use the ReportParser to access all the records included in a report.
```python
report = my_sf.get_report('report_id', includeDetails=True)
parser = ReportParser(report)
    
parser.records()
```

Easily return a specified series from a Matrix Report.

![Alt text](examples/matrix_report.jpg)
For this report doing this:
```python
report = my_sf.get_report('report_id')
matrix_parser = MatrixParser(report)
    
matrix_parser.series_down('May 2012')
```
Returns:
```python
{'Prospecting': 14000, 'Needs Analysis': 18000, 'Qualification': 0,
'Proposal/Price Quote': 20000, 'Negotiation/Review': 2000}
```

# Coming Soon
- Simplified Authentication process
- Access to Dashboards

# Author & License
SalesforceReporting.py was created by Chris Hall.

