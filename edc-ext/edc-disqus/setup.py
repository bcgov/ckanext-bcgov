from setuptools import setup, find_packages
import sys, os

version = '0.9.0'

setup(name='edc-disqus',
      version=version,
      description="Provides Disqus intregration for EDC",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Devin Lumley',
      author_email='devin@highwaythreesolutions.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points='''
          [ckan.plugins]
          edcdisqus=edcdisqus.plugin:EDCDisqusPlugin
      ''',
      )
