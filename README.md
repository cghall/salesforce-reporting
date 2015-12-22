# salesforce_reporting
Get data straight from your Salesforce reports via python using the Analytics API.

## Install

   pip install salesforce-reporting

## Examples

### Authentication
Connect to the Salesforce Analytics API and request data from a report.
```python
import salesforce_reporting
    
my_sf = salesforce_reporting.Connection('your_id', 'your_secret', 'your_username', 
                                           'your_password', 'your_instance')
my_sf.get_report('report_id', includeDetails=True)
```

### Get records from report
Use the ReportParser to access all the records included in a report.
```python
report = my_sf.get_report('report_id', includeDetails=True)
parser = salesforce_reporting.ReportParser(report)
    
parser.records()
```

### Extract series from matrix report
Easily return a specified series from a Matrix Report.

![Alt text](examples/matrix_report.jpg)

For this report doing this:
```python
report = my_sf.get_report('report_id')
matrix_parser = salesforce_reporting.MatrixParser(report)
    
matrix_parser.series_down('May 2012')
```
Returns:
```python
{'Prospecting': 14000, 'Needs Analysis': 18000, 'Qualification': 0,
'Proposal/Price Quote': 20000, 'Negotiation/Review': 2000}
```

## Coming Soon
- Simplified Authentication process
- Access to Dashboards

## Author & License
MIT License. Created by Chris Hall.

