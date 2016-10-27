# Copyright 2016, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license
#
# Highway Three Solutions Inc.
# Author: Jared Smith <github@jrods>

from ckan.controllers.api import ApiController

import cgi
import logging
import os
from pprint import pformat

#import ckan
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import ckanext.bcgov.util.helpers as edc_h

from ckan.common import _, c, request, response
from pylons import config

# shortcuts
get_action = logic.get_action
NotAuthorized = logic.NotAuthorized
NotFound = logic.NotFound
ValidationError = logic.ValidationError

log = logging.getLogger(u'ckanext.bcgov.controllers.ofi')


class EDCOfiController(ApiController):
	def __init__(self):
		self._config = edc_h.get_ofi_config()

	def ofi(self, call_action, ver=None, id=None, object_name=None):
		context = {
			u'model': model, 
			u'session': model.Session, 
			u'user': c.user,
			u'api_version': ver, 
			u'id': id, 
			u'auth_user_obj': c.userobj
		}

		log.debug(u'OFI user cookie: %s', request.cookies)

		log.debug(u'OFI config:\n %s \n', pformat(self._config))

		log.debug(u'OFI api context:\n %s\n', pformat(context))

		extra_vars = {}

		return base.render(u'ofi/ofi_test.html', extra_vars=extra_vars)

		def _build_url():
			pass