from setuptools import setup, find_packages
import sys, os

version = '0.9.0'

setup(
	name='ckanext-edc-schema',
	version=version,
	description="EDC Dataset Schema extension.",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Khalegh Mamakni',
	author_email='khalegh@highwaythreesolutions.com',
	url='',
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.edc_schema'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
	# Add plugins here, eg
	edc_dataset=ckanext.edc_schema.plugin:SchemaPlugin
#	edc_new=ckanext.edc_schema.forms.dataset_form:EDC_DatasetForm
	edc_app = ckanext.edc_schema.forms.edc_datasets:EDC_ApplicationForm
	edc_geo = ckanext.edc_schema.forms.edc_datasets:EDC_GeoSpatialForm
	edc_ngeo = ckanext.edc_schema.forms.edc_datasets:EDC_NonGeoSpatialForm
	edc_webservice = ckanext.edc_schema.forms.edc_datasets:EDC_WebServiceForm
	
	[paste.paster_command]
	edc_command = ckanext.edc_schema.commands.edc_commands:EdcCommand
	""",
)
