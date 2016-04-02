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
    A Salesforce connection for accessing the Salesforce Analytics API using
    the Password/Token authentication. This object is then used as the central
    object for passing report requests into Salesforce.

    By default the object assumes you are connection to a Production instance
    and using API v29.0 but both of these can be overridden to allow access to Sandbox
    instances and/or use a different API version.

    Parameters
    ----------
    username: string
        the Salesforce username used for authentication
    password: string
        the Salesforce password used for authentication
    security_token: string
        the Salesforce security token used for authentication (normally tied to password)
    sandbox: boolean, default False
        whether or not the Salesforce instance connected to is a Sandbox
    api_version: string

    """

    def __init__(self, username=None, password=None, security_token=None, sandbox=False, api_version='v29.0'):
        self.username = username
        self.password = password
        self.security_token = security_token
        self.sandbox = sandbox
        self.api_version = api_version
        self.login_details = self.login(self.username, self.password, self.security_token)
        self.token = self.login_details['oauth']
        self.instance = self.login_details['instance']
        self.headers = {'Authorization': 'OAuth {}'.format(self.token)}
        self.base_url = 'https://{}/services/data/v31.0/analytics'.format(self.instance)

    @staticmethod
    def element_from_xml_string(xml_string, element):
        xml_as_dom = xml.dom.minidom.parseString(xml_string)
        elements_by_name = xml_as_dom.getElementsByTagName(element)
        element_value = None

        if len(elements_by_name) > 0:
            element_value = elements_by_name[0].toxml().replace('<' + element + '>', '').replace(
                '</' + element + '>', '')

        return element_value

    @staticmethod
    def _get_login_url(is_sandbox, api_version):
        if is_sandbox:
            return 'https://{}.salesforce.com/services/Soap/u/{}'.format('test', api_version)
        else:
            return 'https://{}.salesforce.com/services/Soap/u/{}'.format('login', api_version)

    def login(self, username, password, security_token):
        username = escape(username)
        password = escape(password)

        url = self._get_login_url(self.sandbox, self.api_version)

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

        if response.status_code != 200:
            exception_code = self.element_from_xml_string(response.content, 'sf:exceptionCode')
            exception_msg = self.element_from_xml_string(response.content, 'sf:exceptionMessage')

            raise AuthenticationFailure(exception_code, exception_msg)

        oauth_token = self.element_from_xml_string(response.content, 'sessionId')
        server_url = self.element_from_xml_string(response.content, 'serverUrl')

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
        url = '{}/reports/{}?includeDetails={}'.format(self.base_url, report_id, details)

        if filters:
            return self._get_report_filtered(url, filters)
        else:
            return self._get_report_all(url)

    def get_dashboard(self, dashboard_id):
        url = '{}/dashboards/{}/'.format(self.base_url, dashboard_id)
        return requests.get(url, headers=self.headers).json()


class AuthenticationFailure(Exception):

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "{}: {}.".format(self.code, self.msg)
