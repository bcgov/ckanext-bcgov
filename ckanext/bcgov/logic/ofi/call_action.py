# Copyright 2016, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license
#
# HighwayThree Solutions Inc.
# Author: Jared Smith <jrods@github>

import logging
from pprint import pprint, pformat

import requests as reqs

import ckan.plugins.toolkit as toolkit

import ckanext.bcgov.logic.ofi as ofi_logic
import ckanext.bcgov.util.helpers as edc_h


log = logging.getLogger(u'ckanext.bcgov.logic.ofi')


@toolkit.side_effect_free
@ofi_logic.setup_ofi_action(u'/info/fileFormats')
def file_formats(ofi_resp, ofi_vars):
    '''
    OFI API Call:
    TODO
    '''
    return ofi_resp.json()


def geo_resource_form(context, data):
    return toolkit.render('ofi/snippets/geo_resource_form.html', extra_vars=data)


def populate_dataset_with_ofi(context, data):
    pprint(context)
    pprint(data)
    return {'good': True}


@toolkit.side_effect_free
@ofi_logic.setup_ofi_action(u'/security/productAllowedByFeatureType/')
def check_object_name(ofi_resp, ofi_vars):
    '''
    OFI API Call:
    TODO
    '''
    success = True if ofi_resp.status_code == 200 else False
    content_type = ofi_resp.headers.get(u'content-type').split(';')[0]

    open_modal = True

    if content_type == 'text/html':
        success = False
        # not sure yet, but if the content is the IDIR login page, it will try to redirect the user to log into IDIR
        # if the page then displays 404, it's most likey the user isn't logged onto the vpn
        content = ofi_resp.content
    else:
        content = ofi_resp.json()

    results = {
        u'success': success,
        u'open_modal': open_modal,
        u'content': content
    }

    return results
