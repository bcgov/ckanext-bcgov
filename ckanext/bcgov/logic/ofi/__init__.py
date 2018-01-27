# Copyright 2016, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license
#
# HighwayThree Solutions Inc.
# Author: Jared Smith <jrods@github>

import logging
from functools import wraps
from pprint import pprint, pformat

import requests as reqs

from ckan.common import request

import ckan.plugins.toolkit as toolkit

import ckanext.bcgov.util.helpers as edc_h

log = logging.getLogger(u'ckanext.bcgov.logic.ofi')


def check_access(action):
    """
    Decorator for call_action functions to check authorization.

    Even if the call_action doesn't need any authorization checks, there should still be
    a defined auth check for the call_action.
    """
    @wraps(action)
    def wrapper(context, data):
        toolkit.check_access(action.__name__, context, data)
        return action(context, data)
    return wrapper


def setup_ofi_action(api_url=None):
    """
    Decorator for call_action functions.

    This decorator should be used last before the actual call to the
    call_action function

    This sets up common params and options for call_action functions.

    The api_url should be used for prerequisite use only, such as getting
    DWDS file formats or CRS Types, etc. It doesn't support OFI POST API calls.

    :param api_url: An OFI DWDS API endpoint or NoneType
    :returns: call_action function location from logic.ofi.call_action,
              these args are manditory for call_actions:
              def call_action(context, data, ofi_resp)
    """
    def action_decorator(action):
        @wraps(action)
        def wrapper(context, data):
            """
            Context and data are args for get_action calls

            :returns: call_action function location from logic.ofi.call_action,
                      these args are manditory for call_actions:
                        def call_action(context, data, ofi_resp)
            """
            if u'secure' not in data:
                data[u'secure'] = False

            # these action calls don't need to be the secure url
            if action.__name__ in ['file_formats', 'crs_types']:
                data.update(_prepare(False))
            else:
                data.update(_prepare(toolkit.asbool(data[u'secure'])))

            if action.__name__ == 'edit_ofi_resources':
                if u'package_id' not in data:
                    data[u'package_id'] = data.query_params.getone('package_id')

                if u'object_name' not in data:
                    data[u'object_name'] = data.query_params.getone('object_name')

            # allows the decorator to be used for just getting query params, cookies, etc.
            if api_url is not None:
                url = data[u'ofi_url'] + api_url

                # expecting additonal pathing if incoming api endpoint ends with a '/'
                if api_url.endswith(u'/'):
                    if 'object_name' in data and data[u'object_name']:
                        url += data[u'object_name']

                data[u'api_url'] = url

                call_type = u'Secure' if data[u'secure'] else u'Public'  # call_type is for logging purposes

                try:
                    ofi_resp = _make_api_call(url, call_type=call_type, cookies=data[u'cookies'])
                except Exception as e:
                    log.error(u'OFI call exception | url: %s | error: %s' % (url, e))
                    raise OFIServiceError(unicode(e))
            else:
                ofi_resp = reqs.Response()

            return action(context, data, ofi_resp)

        return wrapper
    return action_decorator


def _prepare(secure=False):
    ofi_vars = {}
    ofi_vars[u'config'] = edc_h.get_ofi_config()
    ofi_vars[u'cookies'] = {
        u'SMSESSION': request.cookies.get(u'SMSESSION', '')
    }
    try:
        ofi_vars[u'query_params'] = request.params
    except ValueError, inst:
        log.info('Bad Action API request data: %s', inst)
        return {}

    ofi_vars[u'secure'] = secure
    ofi_vars[u'ofi_url'] = edc_h._build_ofi_url(secure)

    return ofi_vars


def _make_api_call(api_url, call_type='Public', cookies=None):
    log.info(u'OFI outgoing, call type: %s, api url: %s', call_type, api_url)

    resp = reqs.get(api_url, cookies=cookies)

    _log_response(resp, call_type)

    resp.raise_for_status()

    return resp


def _log_response(resp, call_type):
    log.debug(u'OFI response, api response:\n %s', pformat({
        u'url': resp.url,
        u'status': resp.status_code,
        u'reason': resp.reason,
        u'headers': resp.headers,
        u'cookies': resp.cookies,
        u'elapsed': str(resp.elapsed.total_seconds()) + u's'
    }))
    log.debug(u'OFI api content: %s', pformat(resp.text))


class OFIServiceError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
