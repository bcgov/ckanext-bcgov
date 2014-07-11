from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
	name='disqus',
	version=version,
	description="Disqus commenting feature for CKAN",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='ckan, disqus, comments, commenting, discussion',
	author='Open Knowledge Foundation',
	author_email='info@okfn.org',
	url='http://okfn.org',
	license='GPL',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.disqus'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
    [ckan.plugins]
	disqus = ckanext.disqus.plugin:Disqus
	""",
)
