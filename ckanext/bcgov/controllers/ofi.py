# Copyright 2016, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license
#
# Highway Three Solutions Inc.
# Author: Jared Smith <github@jrods>

from ckan.controllers.api import ApiController

import cgi
import logging
import requests as reqs
from pprint import pformat, pprint

# import ckan
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import ckanext.bcgov.util.helpers as edc_h

from ckan.common import _, c, request, response
try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config

# shortcuts
get_action = logic.get_action
NotAuthorized = logic.NotAuthorized
NotFound = logic.NotFound
ValidationError = logic.ValidationError

log = logging.getLogger(u'ckanext.bcgov.controllers.ofi')


def log_response(resp, call_type):
    log.debug(u'OFI check object name, call type: %s', call_type)
    log.debug(u'OFI check object name, url: %s', resp.url)
    log.debug(u'OFI api response:\n %s', pformat({
        u'status': resp.status_code,
        u'reason': resp.reason,
        u'headers': resp.headers,
        u'cookies': resp.cookies,
        u'elapsed': str(resp.elapsed.total_seconds()) + u's'
    }))
    log.debug(u'OFI api content: %s', pformat(resp.text))


class EDCOfiController(ApiController):
    def __init__(self):
        self._config = edc_h.get_ofi_config()
        self.ofi_url = self._build_url()
        self.cookies = {}
        self.cookies[u'SMSESSION'] = request.cookies.get(u'SMSESSION', '')
        self.query_params = {}
#       for key, value in request.cookies.iteritems():
#            self.cookies[key] = value

    def ofi(self, call_action, object_name=None, ver=None):
        '''
        API Entry
        TODO
        '''
        context = {
            u'model': model,
            u'session': model.Session,
            u'user': c.user,
            u'api_version': ver,
            u'id': id,
            u'auth_user_obj': c.userobj
        }

        log.debug(u'OFI user cookie: %s', pformat(self.cookies))

        log.debug(u'OFI config:\n %s \n', pformat(self._config))

        log.debug(u'OFI api context:\n %s\n', pformat(context))

        try:
            self.query_params = self._get_request_data(try_url_params=True)
        except ValueError, inst:
            log.info('Bad Action API request data: %s', inst)
            return self._finish_bad_request(_('JSON Error: %s') % inst)

        if call_action == 'check_object_name':
            return self._check_object_name()
        else:
            return base.abort(400, _('Bad call action: %s') % call_action)

    def _check_object_name(self):
        '''
        OFI API Call:
        TODO
        '''
        resp = reqs.get(self.ofi_url, cookies=self.cookies)
        content_type = resp.headers.get(u'content-type').split(';')[0]

        log_response(resp, u'secure')

        log.debug(u'Inital SMSESSION: %s', request.cookies.get(u'SMSESSION', u''))
        log.debug(u'OFI api cookie SMSESSION: %s', resp.cookies.get(u'SMSESSION', u''))

        if self.ofi_url != resp.url or content_type == 'text/html':
            return self._finish_not_authz(_('Need valid IDIR Login session'))
        else:
            return self._finish(resp.status_code, resp.json(), content_type='json')

    def _build_url(self):
        '''
        TODO
        '''
        url = u'https://delivery.apps.gov.bc.ca/pub/dwds-ofi/secure/security/productAllowedByFeatureType/WHSE_MINERAL_TENURE.MINPOT_MINERAL_POTENTIAL'
        log.debug(u'OFI API URL: %s', url)
        return url
