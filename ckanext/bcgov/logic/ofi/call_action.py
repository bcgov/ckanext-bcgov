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
@ofi_logic.setup_ofi_action(u'/info/fileFormats')
def file_formats(ofi_resp, ofi_vars):
    '''
    OFI API Call:
    TODO
    '''
    return ofi_resp.json()


@logic.side_effect_free
@ofi_logic.setup_ofi_action(u'/security/productAllowedByFeatureType/')
def check_object_name(ofi_resp, ofi_vars):
    '''
    OFI API Call:
    TODO
    '''
    success = True if ofi_resp.status_code == 200 else False
    open_dialog = True
    if success:
        content = ofi_resp.json()
    else:
        content = ofi_resp.content

    results = {
        u'success': success,
        u'open_dialog': open_dialog,
        u'content': content
    }

    return results
