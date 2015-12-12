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
        details = 'true' if details else 'false'
        url = '{}{}?includeDetails={}'.format(self.base_url, report_id, details)

        if filters:
            return self._get_report_filtered(url, filters)
        else:
            return self._get_report_all(url)

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

    def get_grand_total(self):
        return self.data["factMap"]["T!T"]["aggregates"][0]["value"]


class MatrixParser(ReportParser):
    def __init__(self, report):
        self.data = report
        self._check_type()

    def _check_type(self):
        report_format = self.data["reportMetadata"]["reportFormat"]

        if report_format != "MATRIX":
            raise ValueError
        else:
            pass

    def get_col_total(self, col_heading, default=None):
        grp_across_list = self.data["groupingsAcross"]["groupings"]
        col_dict = {grp['label']: int(grp['key']) for grp in grp_across_list}

        try:
            col_key = col_dict[col_heading]
            aggregate_key = 'T!{}'.format(col_key)
            return self.data["factMap"][aggregate_key]["aggregates"][0]["value"]

        except KeyError:
            return default

    def get_row_total(self, row_heading, default=None):
        grp_down_list = self.data["groupingsDown"]["groupings"]
        row_dict = {grp["label"]: int(grp["key"]) for grp in grp_down_list}

        try:
            row_key = row_dict[row_heading]
            aggregate_key = '{}!T'.format(row_key)
            return self.data["factMap"][aggregate_key]["aggregates"][0]["value"]

        except KeyError:
            return default

    def _get_grp_levels(self, grp):
        level = 0

        if grp is not None:
            if type(grp) is str:
                level = 1
            else:
                level = len(grp)

        return level

    def _get_subgroup_key(self, grouping, group_of_interest):
        name_key_dict = {grp['label']: i for i, grp in enumerate(grouping)}
        key = name_key_dict[group_of_interest]
        return key

    def _get_grouping(self, group_of_interest, start_grouping, count):
        count = count
        grouping = start_grouping
        while count > 1:
            subgroup_key = self._get_subgroup_key(grouping, group_of_interest[count-2])
            grouping = start_grouping[subgroup_key]["groupings"]
            count = count - 1
            self._get_grouping(group_of_interest[count-2], grouping, count)
        return grouping

    def _set_col_key(self, col_grp):
        col_grp_level = self._get_grp_levels(col_grp)
        top_level_grouping = self.data["groupingsAcross"]["groupings"]
        col_groupings = self._get_grouping(col_grp, top_level_grouping, col_grp_level)

        col_dict = {grp['label']: grp['key'] for grp in col_groupings}

        if col_grp_level > 1:
            col_grp = col_grp[col_grp_level-1]

        col_key = col_dict[col_grp]

        return col_key

    def _build_key_label_dict(self, col_grp, row_grp):

        row_grp_level = self._get_grp_levels(row_grp)
        row_groupings = self.data["groupingsDown"]["groupings"]

        col_key = self._set_col_key(col_grp)

        if row_grp_level > 0:
            row_dict = {grp['label']: int(grp['key']) for grp in row_groupings}
            row_key = row_dict[row_grp]

            for _ in range(row_grp_level):
                row_groupings = row_groupings[row_key]["groupings"]

        row_keys = [row_grp["key"] for row_grp in row_groupings]

        keys = []

        for el in row_keys:
            key = "{}!{}".format(el, col_key)
            keys.append(key)
        labels = [row_grp["label"] for row_grp in row_groupings]

        return {"keys": keys, "labels": labels}

    def series_down(self, col_grp, row_grp=None):
        key_label_dict = self._build_key_label_dict(col_grp, row_grp)

        values = []

        for key in key_label_dict["keys"]:
            value = self.data["factMap"][key]["aggregates"][0]["value"]
            values.append(value)

        labels = key_label_dict["labels"]

        series = dict(zip(labels, values))
        return series