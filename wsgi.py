# -*- coding: utf-8 -*-

import os
from logging.config import fileConfig as loggingFileConfig
from ckan.config.middleware import make_app
from ckan.cli import CKANConfigLoader

print('**************THE INI IS AT', os.environ.get('CKAN_INI'))

if os.environ.get('CKAN_INI'):
    config_path = os.environ['CKAN_INI']
else:
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'ckan.ini')

if not os.path.exists(config_path):
    raise RuntimeError('CKAN config option not found: {}'.format(config_path))

print('**************THE CONFIG PATH IS AT', config_path)

loggingFileConfig(config_path)
config = CKANConfigLoader(config_path).get_config()

application = make_app(config)
