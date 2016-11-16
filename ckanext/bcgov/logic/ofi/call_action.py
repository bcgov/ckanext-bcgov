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
def file_formats(context, ofi_vars, ofi_resp):
    '''
    OFI API Call:
    TODO
    '''
    return ofi_resp.json()


def geo_resource_form(context, data):
    # Note: need to remove object_name because the decorator handles object_name if present
    #       and appends the object_name on the url, which in this case for fileFormats, is
    #       not required at this point in time
    data.pop(u'object_name', None)
    file_formats = toolkit.get_action(u'file_formats')(context, data)
    data.update({
        u'file_formats': file_formats
    })

    return toolkit.render('ofi/snippets/geo_resource_form.html', extra_vars=data)


@ofi_logic.setup_ofi_action()
def populate_dataset_with_ofi(context, ofi_vars, ofi_resp):
    pprint(ofi_vars)

    results = {}

    if 'ofi_resource_info' not in ofi_vars:
        results.update({
            u'success': False,
            u'error': True,
            u'error_msg': u'Missing ofi resource metadata'
        })
        return results

    resource_meta = {
        u'resource_storage_access_method': u'Indirect Access',
        u'resource_storage_location': u'BCGW DataStore',
        u'projection_name': u'EPSG_3005 - NAD83 BC Albers',
        u'resource_type': u'data'
    }
    resource_meta.update(ofi_vars[u'ofi_resource_info'])
    resource_meta.update({
        'package_id': ofi_vars[u'package_id']
    })

    secure = ofi_vars[u'secure']
    ofi_vars[u'secure'] = False  # just for this one call
    file_formats = toolkit.get_action(u'file_formats')(context, ofi_vars)
    ofi_vars[u'secure'] = secure

    pkg_dict = toolkit.get_action(u'package_show')(context, {'id': ofi_vars[u'package_id']})

    base_name = u'OFI-{0}-'.format(pkg_dict[u'name'])

    # error handling for adding ofi resources
    added_resources = []
    failed_resources = []
    error = False

    for file_format in file_formats:
        resource_meta.update({
            u'name':  base_name + file_format[u'formatname'],
            u'url': u'test-url-for-testing',
            u'format': file_format[u'formatname'],
            u'edc_resource_type': file_format[u'formatname'],
        })
        try:
            resource = toolkit.get_action(u'resource_create')(context, resource_meta)
            added_resources.append(resource)
        except toolkit.ValidationError, e:
            error = True
            failed_resources.append({
                u'resource': resource_meta,
                u'error_msg': 'ValidationError - %s' % unicode(e)
            })

    if error:
        results = {
            u'success': False,
            u'error': error,
            u'failed_resources': failed_resources,
            u'added_resources': added_resources
        }
    else:
        results = {
            u'success': True,
            u'added_resources': added_resources
        }

    return results


@toolkit.side_effect_free
@ofi_logic.setup_ofi_action(u'/security/productAllowedByFeatureType/')
def check_object_name(context, ofi_vars, ofi_resp):
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
