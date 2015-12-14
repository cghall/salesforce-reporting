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

    @staticmethod
    def _get_token(payload):
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

    @staticmethod
    def _get_value_subgroup_index(value_dict, group_of_interest):
        labels_with_index = {group['label']: index for index, group in enumerate(value_dict)}
        value_index = labels_with_index[group_of_interest]
        return value_index

    def _get_value_dict(self, group_of_interest, start_grouping, count):
        value_dict = start_grouping
        while count > 1:
            subgroup_key = self._get_value_subgroup_index(value_dict, group_of_interest[count-2])
            value_dict = value_dict[subgroup_key]["groupings"]
            count -= 1
            self._get_value_dict(group_of_interest[count-2], value_dict, count)
        return value_dict

    def _set_value_key(self, value_groups_of_interest):
        value_grouping_level = len(value_groups_of_interest)
        top_level_grouping = self.data["groupingsAcross"]["groupings"]
        value_groupings = self._get_value_dict(value_groups_of_interest, top_level_grouping, value_grouping_level)

        keys = {grp['label']: grp['key'] for grp in value_groupings}

        value_key = keys[value_groups_of_interest[value_grouping_level - 1]]

        return value_key

    def _build_keys_with_labels(self, value_groups_of_interest, label_groups_of_interest):
        label_grouping = self.data["groupingsDown"]["groupings"]
        label_grouping_level = len(label_groups_of_interest)
        value_key = self._set_value_key(value_groups_of_interest)

        if label_grouping_level > 0:
            row_dict = {grp['label']: int(grp['key']) for grp in label_grouping}
            row_key = row_dict[label_groups_of_interest[label_grouping_level - 1]]

            for _ in range(label_grouping_level):
                label_grouping = label_grouping[row_key]["groupings"]

        label_keys = [label_grp["key"] for label_grp in label_grouping]

        keys = []

        for el in label_keys:
            key = "{}!{}".format(el, value_key)
            keys.append(key)
        labels = [label_grp["label"] for label_grp in label_grouping]

        return {"keys": keys, "labels": labels}

    def series_down(self, col_grp, row_grp=None, summary_value_position=0):

        if type(col_grp) is str:
            first_value_group_of_interest = col_grp
            value_groups_of_interest = [first_value_group_of_interest]
        else:
            value_groups_of_interest = col_grp

        if row_grp is not None:
            if type(row_grp) is str:
                first_label_group_of_interest = row_grp
                label_groups_of_interest = [first_label_group_of_interest]
            else:
                label_groups_of_interest = row_grp
        else:
            label_groups_of_interest = []

        keys_with_labels = self._build_keys_with_labels(value_groups_of_interest, label_groups_of_interest)

        values = []

        for key in keys_with_labels["keys"]:
            value = self.data["factMap"][key]["aggregates"][summary_value_position]["value"]
            values.append(value)

        labels = keys_with_labels["labels"]

        series = dict(zip(labels, values))
        return series
