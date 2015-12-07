import requests


class Connection:
    """ General class for creating a connection to Salesforce via Reporting API with methods
    for accessing reports"""

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

    def _get_token(self, payload):
        login_url = 'https://login.salesforce.com/services/oauth2/token'
        token_request = requests.post(login_url, data=payload)
        return token_request.json()['access_token']

    def get_report(self, report_id, filters=None, details=True):
        url = self.base_url + report_id

        if filters:
            return self._get_report_filtered(url, filters)
        else:
            return self._get_report_all(url)
        #
        # if details:
        #     url = url +

    def _get_metadata(self, url):
        return requests.get(url + '/describe', headers=self.headers).json()

    def _get_report_filtered(self, url, filters):
        metadata = self._get_metadata(url)
        for report_filter in filters:
            metadata["reportMetadata"]["reportFilters"].append(report_filter)

        return requests.post(url, headers=self.headers, json=metadata).json()

    def _get_report_all(self, url):
        return requests.post(url, headers=self.headers).json()


class ReportParser:
    def __init__(self, report):
        self.data = report

    def get_data(self):
        pass

    def get_record_count(self):
        pass

    def get_grand_total(self):
        return self.data["factMap"]["T!T"]["aggregates"][0]["value"]


class MatrixReport(ReportParser):
    def __init__(self, report):
        self.data = report

    def get_col_total(self, col_heading, default=None):
        grp_across_list = self.data["groupingsAcross"]["groupings"]

        col_labels = [grp["label"] for grp in grp_across_list]
        col_keys = [int(grp["key"]) for grp in grp_across_list]
        col_dict = dict(zip(col_labels, col_keys))

        try:
            col_key = col_dict[col_heading]
            aggregate_key = 'T!{}'.format(col_key)
            return self.data["factMap"][aggregate_key]["aggregates"][0]["value"]

        except KeyError:
            return default

    def get_row_total(self, row_heading, default=None):
        pass
