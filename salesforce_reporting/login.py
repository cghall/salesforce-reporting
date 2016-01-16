"""Authentication for salesforce-reporting"""
import requests
import xml.dom.minidom

try:
    # Python 3+
    from html import escape
except ImportError:
    from cgi import escape


class Connection:
    """
    Create a valid Salesforce connection for accessing the Salesforce Analytics API using
    the Password authentication method.

    Parameters
    ----------
    username: the Salesforce username used for authentication
    password: the Salesforce password used for authentication
    security_token: the Salesforce security token used for authentication

    """

    def __init__(self, username=None, password=None, security_token=None):
        self.username = username
        self.password = password
        self.security_token = security_token
        self.login_details = self.login(self.username, self.password, self.security_token)
        self.token = self.login_details['oauth']
        self.instance = self.login_details['instance']
        self.headers = {'Authorization': 'OAuth {}'.format(self.token)}
        self.base_url = 'https://{}/services/data/v29.0/analytics/reports/'.format(self.instance)

    @staticmethod
    def getUniqueElementValueFromXmlString(xml_string, element_name):
        xml_string_as_dom = xml.dom.minidom.parseString(xml_string)
        elements_by_name = xml_string_as_dom.getElementsByTagName(element_name)
        element_value = None

        if len(elements_by_name) > 0:
            element_value = elements_by_name[0].toxml().replace('<' + element_name + '>', '').replace(
                '</' + element_name + '>', '')

        return element_value

    def login(self, username, password, security_token):
        username = escape(username)
        password = escape(password)

        url = 'https://login.salesforce.com/services/Soap/u/v29.0'

        request_body = """<?xml version="1.0" encoding="utf-8" ?>
        <env:Envelope
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
            <env:Body>
                <n1:login xmlns:n1="urn:partner.soap.sforce.com">
                    <n1:username>{username}</n1:username>
                    <n1:password>{password}{token}</n1:password>
                </n1:login>
            </env:Body>
        </env:Envelope>""".format(
            username=username, password=password, token=security_token)

        request_headers = {
            'content-type': 'text/xml',
            'charset': 'UTF-8',
            'SOAPAction': 'login'
        }

        response = requests.post(url, request_body, headers=request_headers)

        oauth_token = self.getUniqueElementValueFromXmlString(response.content, 'sessionId')
        server_url = self.getUniqueElementValueFromXmlString(response.content, 'serverUrl')

        instance = (server_url.replace('http://', '')
                     .replace('https://', '')
                     .split('/')[0]
                     .replace('-api', ''))

        return {'oauth': oauth_token, 'instance': instance}

    def _get_metadata(self, url):
        return requests.get(url + '/describe', headers=self.headers).json()

    def _get_report_filtered(self, url, filters):
        metadata = self._get_metadata(url)
        for report_filter in filters:
            metadata["reportMetadata"]["reportFilters"].append(report_filter)

        return requests.post(url, headers=self.headers, json=metadata).json()

    def _get_report_all(self, url):
        return requests.post(url, headers=self.headers).json()

    def get_report(self, report_id, filters=None, details=True):
        """
        Return the full JSON content of a Salesforce report, with or without filters.

        Parameters
        ----------
        report_id: string
            Salesforce Id of target report
        filters: dict {field: filter}, optional
        details: boolean, default True
            Whether or not detail rows are included in report output

        Returns
        -------
        report: JSON
        """
        details = 'true' if details else 'false'
        url = '{}{}?includeDetails={}'.format(self.base_url, report_id, details)

        if filters:
            return self._get_report_filtered(url, filters)
        else:
            return self._get_report_all(url)
