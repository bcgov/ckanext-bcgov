# Copyright 2016, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license
#
# Highway Three Solutions Inc.
# Author: Jared Smith <github@jrods>

from ckan.controllers.api import ApiController

import cgi
import logging
import requests as reqs
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


def log_response(resp, call_type):
    log.debug(u'OFI check object name, call type: %s', call_type)
    log.debug(u'OFI check object name, url: %s', resp.url)
    log.debug(u'OFI api response:\n %s', pformat({
        u'status': resp.status_code,
        u'reason': resp.reason,
        u'headers': resp.headers,
        u'elapsed': str(resp.elapsed.total_seconds()) + u's'
    }))
    log.debug(u'OFI api content: %s', pformat(resp.text))   


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

        cookies = {}
        for key, value in request.cookies.iteritems():
            cookies[key] = value

        log.debug(u'OFI user cookie: %s', pformat(cookies))

        log.debug(u'OFI config:\n %s \n', pformat(self._config))

        log.debug(u'OFI api context:\n %s\n', pformat(context))

        extra_vars = {}

        if call_action == 'check_object_name':
            pub_response = reqs.get(u'https://delivery.apps.gov.bc.ca/pub/dwds-ofi/security/productAllowedByFeatureType/WHSE_MINERAL_TENURE.MINPOT_MINERAL_POTENTIAL')
            #pub_response = reqs.get(u'https://catalogue.data.gov.bc.ca/api/action/package_show?id=consolidated-revenue-fund-detailed-schedules-of-payments-order-in-council-other-appointees-and-emplo')
            log_response(pub_response, u'public')

            sec_response = reqs.get(u'https://delivery.apps.gov.bc.ca/pub/dwds-ofi/secure/security/productAllowedByFeatureType/WHSE_MINERAL_TENURE.MINPOT_MINERAL_POTENTIAL', cookies=cookies)
            #sec_response = reqs.get(u'https://catalogue.data.gov.bc.ca/api/action/package_show?id=consolidated-revenue-fund-detailed-schedules-of-payments-order-in-council-other-appointees-and-empl')
            log_response(sec_response, u'secure')

            #return self._finish(ofi_response.status_code, ofi_response.json(), content_type='json' )

        return base.render(u'ofi/ofi_test.html', extra_vars=extra_vars)
