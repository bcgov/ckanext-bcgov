from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='ckanext-edc-idir',
    version=version,
    description="Enable login with IDIR credentials",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='James Gagan',
    author_email='james@highwaythreesolutions.com',
    url='highwaythreesolutions.com',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.edc_idir'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        # Add plugins here, e.g.
        # myplugin=ckanext.edc-idir.plugin:PluginClass
        edc_idir=ckanext.edc_idir.plugin:IdirPlugin

    ''',
)
