from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
	name='ckanext-ga-report',
	version=version,
	description="GA reporting for CKAN",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='David Read',
	author_email='david.read@hackneyworkshop.com',
	url='',
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.ga_report'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		'gdata',
		'google-api-python-client'
	],
	entry_points=\
	"""
        [ckan.plugins]
	# Add plugins here
	ga-report=ckanext.ga_report.plugin:GAReportPlugin

        [paste.paster_command]
        loadanalytics = ckanext.ga_report.command:LoadAnalytics
        initdb = ckanext.ga_report.command:InitDB
        getauthtoken = ckanext.ga_report.command:GetAuthToken
        fixtimeperiods = ckanext.ga_report.command:FixTimePeriods
	""",
)
