import requests


class Connection:
    """
    Connection to the Salesforce Reporting API
    """

    def __init__(self, client_id, client_secret, username, password, instance):
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'password',
            'username': username,
            'password': password
        }
        self.token = self._get_token(payload)
        self.headers = {'Authorization': 'OAuth {}'.format(self.token)}
        self.base_url = 'https://{}.salesforce.com/services/data/v29.0/analytics/reports/'.format(instance)

    @staticmethod
    def _get_token(payload):
        login_url = 'https://login.salesforce.com/services/oauth2/token'
        token_request = requests.post(login_url, data=payload)
        return token_request.json()['access_token']

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
        Return report content as a dict

        Parameters
        ----------
        report_id: string
            Salesforce Id of target report
        filters: dict, optional
        details: boolean, default True
            Whether or not detail rows are included in report output

        Returns
        -------
        report: dict
        """
        details = 'true' if details else 'false'
        url = '{}{}?includeDetails={}'.format(self.base_url, report_id, details)

        if filters:
            return self._get_report_filtered(url, filters)
        else:
            return self._get_report_all(url)
