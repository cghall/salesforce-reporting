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
    def _convert_parameter(parameter):
        if type(parameter) is str:
            new_parameter = [parameter]
        elif parameter is None:
            new_parameter = []
        elif type(parameter) is list:
            new_parameter = parameter
        else:
            raise ValueError
        return new_parameter

    @staticmethod
    def _get_subgroup_index(group_above, subgroup_name):
        subgroups_with_index = {subgroup['label']: index for index, subgroup in enumerate(group_above)}
        index = subgroups_with_index[subgroup_name]
        return index

    def _get_grouping(self, groups_of_interest, start_grouping, count):
        current_grouping = start_grouping

        while count > 1:
            group_name = groups_of_interest[count - 2]
            subgroup_index = self._get_subgroup_index(current_grouping, group_name)
            current_grouping = current_grouping[subgroup_index]["groupings"]
            count -= 1
            self._get_grouping(group_name, current_grouping, count)

        return current_grouping

    def _get_static_key(self, groups_of_interest, static_grouping_key):
        grouping_depth = len(groups_of_interest)
        group_index = grouping_depth - 1
        top_grouping = self.data[static_grouping_key]["groupings"]
        grouping = self._get_grouping(groups_of_interest, top_grouping, grouping_depth)

        keys = {group['label']: group['key'] for group in grouping}
        static_key = keys[groups_of_interest[group_index]]

        return static_key

    def _get_dynamic_keys(self, groups_of_interest, dynamic_grouping_key):
        grouping_depth = len(groups_of_interest) + 1
        top_grouping = self.data[dynamic_grouping_key]["groupings"]
        grouping = self._get_grouping(groups_of_interest, top_grouping, grouping_depth)

        dynamic_keys = [group["key"] for group in grouping]
        labels = [group["label"] for group in grouping]

        return {"keys": dynamic_keys, "labels": labels}

    def _build_keys(self, static_groups_of_interest, dynamic_groups_of_interest, static_grouping_key,
                    dynamic_grouping_key):
        static_key = self._get_static_key(static_groups_of_interest, static_grouping_key)
        dynamic_keys = self._get_dynamic_keys(dynamic_groups_of_interest, dynamic_grouping_key)

        keys = []

        if static_grouping_key == "groupingsAcross":
            for el in dynamic_keys["keys"]:
                key = "{}!{}".format(el, static_key)
                keys.append(key)
        else:
            for el in dynamic_keys["keys"]:
                key = "{}!{}".format(static_key, el)
                keys.append(key)

        return {"keys": keys, "labels": dynamic_keys["labels"]}

    def _series(self, static_groups_of_interest, static_grouping_key, dynamic_grouping_key,
                dynamic_groups_of_interest=None, value_position=0):
        static_groups_of_interest = self._convert_parameter(static_groups_of_interest)
        dynamic_groups_of_interest = self._convert_parameter(dynamic_groups_of_interest)
        keys_labels = self._build_keys(static_groups_of_interest, dynamic_groups_of_interest,
                                       static_grouping_key, dynamic_grouping_key)

        labels = keys_labels["labels"]
        values = []

        for key in keys_labels["keys"]:
            value = self.data["factMap"][key]["aggregates"][value_position]["value"]
            values.append(value)

        series = dict(zip(labels, values))
        return series

    def series_down(self, column_groups, row_groups=None, value_position=0):
        static_grouping_key = "groupingsAcross"
        dynamic_grouping_key = "groupingsDown"

        return self._series(column_groups, static_grouping_key, dynamic_grouping_key,
                            dynamic_groups_of_interest=row_groups, value_position=value_position)

    def series_across(self, row_groups, col_groups=None, value_position=0):
        static_grouping_key = "groupingsDown"
        dynamic_grouping_key = "groupingsAcross"

        return self._series(row_groups, static_grouping_key, dynamic_grouping_key,
                            dynamic_groups_of_interest=col_groups, value_position=value_position)

