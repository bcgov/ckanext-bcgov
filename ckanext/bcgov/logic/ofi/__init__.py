# Copyright 2016, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license
#
# HighwayThree Solutions Inc.
# Author: Jared Smith <jrods@github>

from functools import wraps

from ckan.common import request

import ckanext.bcgov.util.helpers as edc_h


def setup_action(api_url):
    '''
    Decorator for call_action functions, macro for setting up all the vars for ofi call
    '''
    def action_decorator(action):
        @wraps(action)
        def wrapper(context, data):
            '''
            Context and data are args for get_action calls
            '''
            ofi_vars = _prepare(data[u'secure'])
            url = ofi_vars[u'ofi_url'] + api_url + data[u'object_name']
            call_type = 'Secure' if data[u'secure'] else 'Public'  # call_type is for logging purposes
            return action(url, ofi_vars, call_type)
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
