from setuptools import setup

setup(
  name = 'salesforce-reporting',
  packages = ['salesforce_reporting'],
  version = '0.1.1',
  description = 'Get data from Salesforce reports with python',
  author = 'Chris Hall',
  author_email = 'chris@impactbox.co.uk',
  url = 'https://github.com/cghall/salesforce-reporting',
  keywords = ['python', 'salesforce', 'salesforce.com'],
  install_requires= ['requests'],
  classifiers = [
      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 3'
  ],
  include_package_data=True,
)