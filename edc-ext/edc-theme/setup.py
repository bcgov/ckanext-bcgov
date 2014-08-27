from setuptools import setup, find_packages
import sys, os

version = '0.9.0'

setup(
    name='edc-theme',
    version=version,
    description="Provides the look and feel of the DataBC site for CKAN.",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Devin Lumley',
    author_email='devin@highwaythreesolutions.com',
    url='highwaythreesolutions.com',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.edc_theme'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        edc_theme=ckanext.edc_theme.plugin:EDCThemePlugin
    ''',
)
