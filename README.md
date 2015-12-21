# SalesforceReporting.Py
Get records and data from your Salesforce reports via python using the Analytics API.

# Install
Coming soon.

# Examples
Connect to the Salesforce Analytics API and request data from a report.
    import salesforcereporting
    
    my_sf = salesforcereporting.Connection('your_id', 'your_secret', 'your_username', 'your_password', 'your_instance')
    my_sf.get_report('report_id', includeDetails=True)

Use the ReportParser to access all the records included in a report.

Easily return a specified series from a Matrix Report.

# Coming Soon
- Simpler Authentication process
- Access to Dashboards

# Author & License
SalesforceReporting.py was created by Chris Hall.

