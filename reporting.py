import requests
import json

class SalesforceConnection:

	""" General class for creating a connection to Salesforce via Reporting API
	and returning token"""

	def __init__(self, client_id, client_secret, username, password, instance):
		self.client_id = client_id
		self.client_secret = client_secret
		self.username = username
		self.password = password
		self.instance = instance
		self.grant_type = 'password'

	def get_token(self):
		payload = {
			'client_id': self.client_id,
			'client_secret': self.client_secret,
			'grant_type': self.grant_type,
			'username': self.username,
			'password': self.password
		}
		token_request = requests.post('https://login.salesforce.com/services/oauth2/token', data=payload)
		token = token_request.json()['access_token']
		return token

class TabularReport:

	""" Class for accessing a tabular report via Reporting API, includes methods for
	manipulating output and defining report parameters"""

	def __init__(self, sf_connection, report_id):
		self.token = sf_connection.get_token()
		self.instance = sf_connection.instance
		self.report_id = report_id
		self.URL = 'https://{}.salesforce.com/services/data/v29.0/analytics/reports/{}?includeDetails=true'.format(self.instance, self.report_id)
		self.head = {'Authorization': 'OAuth {}'.format(self.token),
					 'Content-Type': 'application/json'}
		self.filters = []

	def get_metadata(self):
		metadata = requests.get('https://{}.salesforce.com/services/data/v29.0/analytics/reports/{}/describe'.format(self.instance, self.report_id), headers=self.head).json()
		return metadata

	def set_filters(self, filter_array):
		for report_filter in filter_array:
			self.filters.append(report_filter)

	def get_report_data(self):

		if len(self.filters) > 0:
			metadata = self.get_metadata()

			for report_filter in self.filters:
				metadata["reportMetadata"]["reportFilters"].append(report_filter)
			
			string_metadata = json.dumps(metadata)
			report_data = requests.post(self.URL, headers=self.head, data=string_metadata)
		
		else:
			report_data = requests.post(self.URL, headers=self.head)

		return report_data

	def report_data_to_json(self, output_file):
		report_json = self.get_report_data().json()

		with open(output_file, 'w') as json_file:
			json.dump(report_json, json_file, indent=2)

class MatrixReport:

	""" Class for accessing a matrix report via Reporting API, includes methods for
	manipulating output and defining report parameters"""

	def __init__(self, sf_connection, report_id):
		self.token = sf_connection.get_token()
		self.instance = sf_connection.instance
		self.report_id = report_id
		self.URL = 'https://{}.salesforce.com/services/data/v29.0/analytics/reports/{}?includeDetails=true'.format(self.instance, self.report_id)
		self.head = {'Authorization': 'OAuth {}'.format(self.token),
					 'Content-Type': 'application/json'}
		self.filters = []

	def get_metadata(self):
		metadata = requests.get('https://{}.salesforce.com/services/data/v29.0/analytics/reports/{}/describe'.format(self.instance, self.report_id), headers=self.head).json()
		return metadata

	def set_filters(self, filter_array):
		for report_filter in filter_array:
			self.filters.append(report_filter)

	def get_report_data(self):

		if len(self.filters) > 0:
			metadata = self.get_metadata()

			for report_filter in self.filters:
				metadata["reportMetadata"]["reportFilters"].append(report_filter)
			
			string_metadata = json.dumps(metadata)
			report_data = requests.post(self.URL, headers=self.head, data=string_metadata)
		
		else:
			report_data = requests.post(self.URL, headers=self.head)

		return report_data

	def report_data_to_json(self, output_file):
		report_json = self.get_report_data().json()

		with open(output_file, 'w') as json_file:
			json.dump(report_json, json_file, indent=2)

	def get_grand_total(self):

		if len(self.filters) > 0:
			metadata = self.get_metadata()

			for report_filter in self.filters:
				metadata["reportMetadata"]["reportFilters"].append(report_filter)
			
			string_metadata = json.dumps(metadata)
			report_data = requests.post(self.URL, headers=self.head, data=string_metadata)
			report_json = report_data.json()
			grand_total = report_json["factMap"]["T!T"]["aggregates"][0]["value"]
		
		else:
			report_data = requests.post(self.URL, headers=self.head)
			report_json = report_data.json()
			grand_total = report_json["factMap"]["T!T"]["aggregates"][0]["value"]

		return grand_total

	def get_col_total(self, col_heading):

		if len(self.filters) > 0:
			metadata = self.get_metadata()

			for report_filter in self.filters:
				metadata["reportMetadata"]["reportFilters"].append(report_filter)
			
			string_metadata = json.dumps(metadata)
			report_data = requests.post(self.URL, headers=self.head, data=string_metadata)
			report_json = report_data.json()
			
			grp_across_list = report_json["groupingsAcross"]["groupings"]
			col_labels = [grp["label"] for grp in grp_across_list]
			col_keys = [int(grp["key"]) for grp in grp_across_list]
			col_dict = dict(zip(col_labels, col_keys))

			aggregate_key = 'T!{}'.format(col_dict[col_heading])

			col_total = report_json["factMap"][aggregate_key]["aggregates"][0]["value"]
		
		else:
			report_data = requests.post(self.URL, headers=self.head)
			report_json = report_data.json()

			grp_across_list = report_json["groupingsAcross"]["groupings"]
			col_labels = [grp["label"] for grp in grp_across_list]
			col_keys = [int(grp["key"]) for grp in grp_across_list]
			col_dict = dict(zip(col_labels, col_keys))

			aggregate_key = 'T!{}'.format(col_dict[col_heading])

			col_total = report_json["factMap"][aggregate_key]["aggregates"][0]["value"]

		return col_total