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

import ckanext.bcgov.util.helpers as edc_h

log = logging.getLogger(u'ckanext.bcgov.logic.ofi')


def setup_ofi_action(api_url):
    '''
    Decorator for call_action functions, macro for setting up all the vars for ofi call
    '''
    def action_decorator(action):
        @wraps(action)
        def wrapper(context, data):
            '''
            Context and data are args for get_action calls
            '''
            if 'secure' not in data:
                data[u'secure'] = False

            ofi_vars = _prepare(data[u'secure'])

            if 'object_name' in data:
                url = ofi_vars[u'ofi_url'] + api_url + data[u'object_name']
            else:
                url = ofi_vars[u'ofi_url'] + api_url

            call_type = 'Secure' if data[u'secure'] else 'Public'  # call_type is for logging purposes
            ofi_resp = _make_api_call(url, call_type=call_type, cookies=ofi_vars[u'cookies'])
            return action(ofi_resp, ofi_vars)

        return wrapper
    return action_decorator


def _prepare(secure=False):
    ofi_vars = {}
    ofi_vars[u'config'] = edc_h.get_ofi_config()
    ofi_vars[u'cookies'] = {
        u'SMSESSION': request.cookies.get(u'SMSESSION', '')
    }
    try:
        ofi_vars['query_params'] = request.params
    except ValueError, inst:
        log.info('Bad Action API request data: %s', inst)
        return {}

    ofi_vars[u'secure'] = secure
    ofi_vars[u'ofi_url'] = edc_h._build_ofi_url(secure)

    return ofi_vars


def _make_api_call(api_url, call_type='Public', cookies=None):
    resp = reqs.get(api_url, cookies=cookies)

    _log_response(resp, call_type)
    '''
    content_type = resp.headers.get(u'content-type').split(';')[0]

    if resp.status_code == 404:
        return resp.content
    elif content_type == 'text/html':
        # switch to a raise
        return u'Need valid IDIR Login session'
    else:
        return resp.json()
    '''
    return resp


def _log_response(resp, call_type):
    log.debug(u'OFI check object name, call type: %s', call_type)
    log.debug(u'OFI check object name, api response:\n %s', pformat({
        u'url': resp.url,
        u'status': resp.status_code,
        u'reason': resp.reason,
        u'headers': resp.headers,
        u'cookies': resp.cookies,
        u'elapsed': str(resp.elapsed.total_seconds()) + u's'
    }))
    log.debug(u'OFI api content: %s', pformat(resp.text))
