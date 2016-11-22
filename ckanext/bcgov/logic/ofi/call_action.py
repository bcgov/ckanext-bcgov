# Copyright 2016, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license
#
# HighwayThree Solutions Inc.
# Author: Jared Smith <jrods@github>

import logging
from pprint import pprint, pformat

import requests as reqs

import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit

import ckanext.bcgov.logic.ofi as ofi_logic
import ckanext.bcgov.util.helpers as edc_h

try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config

# shortcuts
_ = toolkit._
NotFound = toolkit.ObjectNotFound
ValidationError = toolkit.ValidationError
OFIServiceError = ofi_logic.OFIServiceError

log = logging.getLogger(u'ckanext.bcgov.logic.ofi')


@toolkit.side_effect_free
@ofi_logic.setup_ofi_action(u'/info/fileFormats')
def file_formats(context, ofi_vars, ofi_resp):
    '''
    OFI API Call:
    TODO
    '''
    resp_content = ofi_resp.json()

    if 'Status' in resp_content and resp_content['Status'] == 'FAILURE':
        raise OFIServiceError(_('OFI Service returning failure status - file_formats'))

    return ofi_resp.json()


def geo_resource_form(context, data):
    '''
    TODO
    '''
    # Note: need to remove object_name because the decorator handles object_name if present
    #       and appends the object_name on the url, which in this case for fileFormats, is
    #       not required at this point in time
    file_formats = toolkit.get_action(u'file_formats')(context, data)
    data.update({
        u'file_formats': file_formats
    })

    return toolkit.render('ofi/snippets/geo_resource_form.html', extra_vars=data)


@ofi_logic.setup_ofi_action()
def populate_dataset_with_ofi(context, ofi_vars, ofi_resp):
    '''
    TODO
    '''
    results = {}

    if 'ofi_resource_info' not in ofi_vars:
        results.update({
            u'success': False,
            u'error': True,
            u'error_msg': u'Missing ofi resource metadata'
        })
        return results

    # TODO: check incoming resource cycle, send form template back with error

    resource_meta = {
        u'package_id': ofi_vars[u'package_id'],
        u'resource_storage_access_method': u'Indirect Access',
        u'resource_storage_location': u'BCGW DataStore',
        u'projection_name': u'EPSG_3005 - NAD83 BC Albers',
        u'edc_resource_type': u'Data',
        u'ofi': True,
    }
    resource_meta.update(ofi_vars[u'ofi_resource_info'])

    file_formats = toolkit.get_action(u'file_formats')(context, ofi_vars)

    pkg_dict = toolkit.get_action(u'package_show')(context, {'id': ofi_vars[u'package_id']})

    base_name = u'OFI-{0}-'.format(pkg_dict[u'name'])

    # error handling for adding ofi resources
    added_resources = []
    failed_resources = []
    error = False

    base_url = config.get('ckan.site_url')

    # Try to add all avaliable OFI formats
    for file_format in file_formats:
        resource_meta.update({
            u'name':  base_name + file_format[u'formatname'],
            u'url': base_url + h.url_for('ofi resource', format=file_format[u'formatname'], object_name=ofi_vars[u'object_name']),
            u'format': file_format[u'formatname'],
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


@ofi_logic.setup_ofi_action()
def remove_ofi_resources(context, ofi_vars, ofi_resp):
    '''
    TODO
    '''
    pkg_dict = toolkit.get_action(u'package_show')(context, {'id': ofi_vars[u'package_id']})

    resources_to_keep = []
    for resource in pkg_dict[u'resources']:
        if u'ofi' not in resource or resource[u'ofi'] is False:
            resources_to_keep.append(resource)

    pkg_dict[u'resources'] = resources_to_keep

    results = {}

    try:
        package_id = toolkit.get_action(u'package_update')(context, pkg_dict)
        results.update({
            u'success': True,
            u'package_id': package_id
        })
    except (NotFound, ValidationError) as e:
        results.update({
            u'success': False,
            u'error': True,
            u'error_msg': unicode(e)
        })

    return results


@toolkit.side_effect_free
@ofi_logic.setup_ofi_action()
def edit_ofi_resources(context, ofi_vars, ofi_resp):
    '''
    TODO
    '''
    pkg_dict = toolkit.get_action(u'package_show')(context, {'id': ofi_vars[u'package_id']})

    results = {}

    # get all ofi resources in the dataset
    ofi_resources = [i for i in pkg_dict[u'resources'] if u'ofi' in i and i[u'ofi']]

    if toolkit.request.method == 'GET':
        # get the first ofi resource, it doesn't matter which type it is
        ofi_resource = ofi_resources[0] or False

        # just the format names from the ofi resources
        file_formats = []
        for resource in ofi_resources:
            if u'format' in resource:
                file_formats.append({
                    u'formatname': resource[u'format']
                })

        if ofi_resource:
            results.update({
                u'success': True,
                u'render_form': True,
                u'ofi_resource': ofi_resource,
                u'file_formats': file_formats
            })
        else:
            results.update({
                u'success': False,
                u'error': True,
                u'error_msg': _('OFI resource not found.')
            })
    else:
        update_resources = []
        for resource in pkg_dict[u'resources']:
            # update only ofi resources
            if u'ofi' in resource and resource[u'ofi']:
                resource.update(ofi_vars[u'ofi_resource_info'])

            update_resources.append(resource)

        pkg_dict[u'resources'] = update_resources

        try:
            updated_dataset = toolkit.get_action('package_update')(context, pkg_dict)
            # shorthand way to get just ofi resources
            updated_resources = [i for i in updated_dataset[u'resources'] if u'ofi' in i and i[u'ofi']]

            results.update({
                u'success': True,
                u'updated': True,
                u'updated_resources': updated_resources
            })
        except (NotFound, ValidationError) as e:
            results.update({
                u'success': False,
                u'updated': False,
                u'error': True,
                u'error_msg': unicode(e)
            })

    return results
