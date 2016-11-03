# Copyright 2016, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license
#
# HighwayThree Solutions Inc.
# Author: Jared Smith <jrods@github>

import logging

from pprint import pprint, pformat

import requests as reqs

import ckan.logic as logic
from ckan.common import _, c, request, response

import ckanext.bcgov.logic.ofi as ofi_logic
import ckanext.bcgov.util.helpers as edc_h


log = logging.getLogger(u'ckanext.bcgov.logic.ofi')


@logic.side_effect_free
@ofi_logic.setup_action(u'/info/fileFormats')
def file_formats(url, ofi_vars, call_type):
    '''
    OFI API Call:
    TODO
    '''
    return _make_api_call(url, call_type=call_type, cookies=ofi_vars[u'cookies'])


@logic.side_effect_free
@ofi_logic.setup_action(u'/security/productAllowedByFeatureType/')
def check_object_name(url, ofi_vars, call_type):
    '''
    OFI API Call:
    TODO
    '''
    return _make_api_call(url, call_type=call_type, cookies=ofi_vars[u'cookies'])


def _make_api_call(api_url, call_type='Public', cookies=None):
    resp = reqs.get(api_url, cookies=cookies)

    _log_response(resp, call_type)

    content_type = resp.headers.get(u'content-type').split(';')[0]

    if resp.status_code == 404:
        return resp.content
    elif content_type == 'text/html':
        # switch to a raise
        return u'Need valid IDIR Login session'
    else:
        return resp.json()


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
