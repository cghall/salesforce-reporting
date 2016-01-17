class ReportParser:
    """
    Parser with generic functionality for all Report Types (Tabular, Summary, Matrix)

    Parameters
    ----------
    report: dict, return value of Connection.get_report()
    """
    def __init__(self, report):
        self.data = report
        self.type = self.data["reportMetadata"]["reportFormat"]
        self.has_details = self.data["hasDetailRows"]

    def get_grand_total(self):
        return self.data["factMap"]["T!T"]["aggregates"][0]["value"]

    @staticmethod
    def _flatten_record(record):
        return [field["label"] for field in record]

    def _get_field_labels(self):
        columns = self.data["reportMetadata"]["detailColumns"]
        column_details = self.data["reportExtendedMetadata"]["detailColumnInfo"]
        return {key: column_details[value]["label"] for key, value in enumerate(columns)}

    def records(self):
        """
        Return a list of all records included in the report. If detail rows are not included
        in the report a ValueError is returned instead.

        Returns
        -------
        records: list
        """
        if not self.has_details:
            raise ValueError('Report does not include details so cannot access individual records')

        records = []
        fact_map = self.data["factMap"]

        for group in fact_map.values():
            rows = group["rows"]
            group_records = (self._flatten_record(row["dataCells"]) for row in rows)

            for record in group_records:
                records.append(record)

        return records

    def records_dict(self):
        """
        Return a list of dictionaries for all records in the report in {field: value} format. If detail rows
        are not included in the report a ValueError is returned instead.

        Returns
        -------
        records: list of dictionaries in {field: value, field: value...} format
        """
        if not self.has_details:
            raise ValueError('Report does not include details so cannot access individual records')

        records = []
        fact_map = self.data["factMap"]
        field_labels = self._get_field_labels()

        for group in fact_map.values():
            rows = group["rows"]
            group_records = (self._flatten_record(row["dataCells"]) for row in rows)

            for record in group_records:
                labelled_record = {field_labels[key]: value for key, value in enumerate(record)}
                records.append(labelled_record)

        return records


class MatrixParser(ReportParser):
    """
    Parser with specific functionality for matrix reports

    Parameters
    ----------
    report: dict, return value of Connection.get_report()
    """
    def __init__(self, report):
        super().__init__(report)
        self.data = report
        self._check_type()

    def _check_type(self):
        expected = "MATRIX"
        if self.type != expected:
            raise ValueError("Incorrect report type. Expected {}, received {}.".format(expected, self.type))
        else:
            pass

    def get_col_total(self, col_label, default=None):
        """
        Return the total for the specified column. The default arg makes it possible to specify the return
        value if the column label is not found.

        Parameters
        ----------
        col_label: string
        default: string, optional, default None
            If column is not found determines the return value

        Returns
        -------
        total: int
        """
        grp_across_list = self.data["groupingsAcross"]["groupings"]
        col_dict = {grp['label']: int(grp['key']) for grp in grp_across_list}

        try:
            col_key = col_dict[col_label]
            return self.data["factMap"]['T!{}'.format(col_key)]["aggregates"][0]["value"]

        except KeyError:
            return default

    def get_row_total(self, row_label, default=None):
        """
        Return the total for the specified row. The default arg makes it possible to specify the return
        value if the column label is not found.

        Parameters
        ----------
        row_label: string
        default: string, optional, default None
            If row is not found determines the return value

        Returns
        -------
        total: int
        """
        grp_down_list = self.data["groupingsDown"]["groupings"]
        row_dict = {grp["label"]: int(grp["key"]) for grp in grp_down_list}

        try:
            row_key = row_dict[row_label]
            return self.data["factMap"]['{}!T'.format(row_key)]["aggregates"][0]["value"]

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
        """
        Return selected slice of a report on a vertical axis

        Parameters
        ----------
        column_groups: string or list
            The selected column to return series from
            If multiple grouping levels a list is used to identify grouping of interest
        row_groups: string, list or None, optional, default None
            Limits rows included in Series to those within specified grouping
        value_position: int, default 0
            Index of value of interest, if only one value included by default will select
            correct value

        Returns
        -------
        series: dict, {label: value, ...}
        """
        static_grouping_key = "groupingsAcross"
        dynamic_grouping_key = "groupingsDown"

        return self._series(column_groups, static_grouping_key, dynamic_grouping_key,
                            dynamic_groups_of_interest=row_groups, value_position=value_position)

    def series_across(self, row_groups, col_groups=None, value_position=0):
        """
        Return selected slice of a report on a horizontal axis

        Parameters
        ----------
        row_groups: string or list
            The selected row to return series from
            If multiple grouping levels a list is used to identify grouping of interest
        col_groups: string, list or None, optional, default None
            Limits cols included in Series to those within specified grouping
        value_position: int, default 0
            Index of value of interest, if only one value included by default will select
            correct value

        Returns
        -------
        series: dict, {label: value, ...}
        """
        static_grouping_key = "groupingsDown"
        dynamic_grouping_key = "groupingsAcross"

        return self._series(row_groups, static_grouping_key, dynamic_grouping_key,
                            dynamic_groups_of_interest=col_groups, value_position=value_position)