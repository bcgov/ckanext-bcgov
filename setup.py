# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
from setuptools import setup, find_packages
import sys, os

# for version variable
exec(open("ckanext/bcgov/version.py").read())

setup(
    name='ckanext-bcgov',
    version=version,
    description="CKAN Extension - BC Data Catalogue.",
    long_description="""\
    """,
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Khalegh Mamakni',
    author_email='khalegh@highwaythreesolutions.com',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.bcgov'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'ckan==2.3.1',
        'pycurl==7.19.5',
        'validate_email==1.2',
    ],
    entry_points=\
    """
    [ckan.plugins]
    # Add plugins here, eg
    edc_dataset=ckanext.bcgov.plugin:SchemaPlugin
#    edc_new=ckanext.bcgov.forms.dataset_form:EDC_DatasetForm
    edc_app = ckanext.bcgov.forms.edc_datasets:EDC_ApplicationForm
    edc_geo = ckanext.bcgov.forms.edc_datasets:EDC_GeoSpatialForm
    edc_ngeo = ckanext.bcgov.forms.edc_datasets:EDC_NonGeoSpatialForm
    edc_webservice = ckanext.bcgov.forms.edc_datasets:EDC_WebServiceForm
    edc_disqus = ckanext.bcgov.plugin:EDCDisqusPlugin

    [paste.paster_command]
    edc_command = ckanext.bcgov.commands.edc_commands:EdcCommand
    """,
)
