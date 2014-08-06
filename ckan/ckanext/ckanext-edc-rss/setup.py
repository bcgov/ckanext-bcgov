from setuptools import setup, find_packages
import sys, os

version = '0.9.0'

setup(
    name='ckanext-edc-rss',
    version=version,
    description="",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Devin Lumley',
    author_email='devin@highwaythreesolutions.com',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.edc_rss'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        edc_rss=ckanext.edc_rss.plugin:EDCRSSPlugin
    ''',
)
