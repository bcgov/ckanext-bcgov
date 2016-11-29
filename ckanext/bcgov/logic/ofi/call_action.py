# Copyright 2016, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license
#
# HighwayThree Solutions Inc.
# Author: Jared Smith <jrods@github>

import logging
from pprint import pprint, pformat
import json

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
    TODO: this should be moved to the ofi controller, considering it returns html
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
            u'format': str(file_format[u'formatID'])
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
        pkg_dict = toolkit.get_action(u'package_show')(context, {'id': ofi_vars[u'package_id']})

        # easiest way to change the dataset state, too difficult to do on the front end
        pkg_dict.update({
            u'state': u'active'
        })
        pkg_dict = toolkit.get_action(u'package_update')(context, pkg_dict)

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

    file_formats = toolkit.get_action(u'file_formats')({}, {})

    results = {}

    # get all ofi resources in the dataset
    ofi_resources = [i for i in pkg_dict[u'resources'] if u'ofi' in i and i[u'ofi']]

    if toolkit.request.method == 'GET':
        # get the first ofi resource, it doesn't matter which type it is
        ofi_resource = ofi_resources[0] or False

        # just the format names from the ofi api call
        # TODO: maybe store both the format name and id in the resource meta data?
        file_formats = [i[u'formatname'] for i in file_formats]

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


@ofi_logic.setup_ofi_action(u'/security/productAllowedByFeatureType/')
def get_max_aoi(context, ofi_vars, ofi_resp):
    '''
    TODO
    Also checks object_name for users eg. opening the mow
    '''
    results = {}

    #pprint(ofi_vars)
    #pprint(ofi_resp.text)

    if ofi_resp.status_code == 200:
        resp_dict = ofi_resp.json()
        if u'allowed' in resp_dict and resp_dict[u'allowed'] is False:
            results.update({
                u'success': False,
                u'error': True,
                u'user_not_allowed': True,
                u'error_msg': unicode('User is not allowed to view object.'),
                u'content': resp_dict
            })
            return results
    else:
        results.update({
            u'success': False,
            u'error': True,
            u'error_msg': unicode(ofi_resp.text)
        })
        return results

    if u'object_name' in ofi_vars:
        # TODO: move url and resource_id as config params
        url = 'https://catalogue.data.gov.bc.ca/api/action/datastore_search'
        data = {
            'resource_id': 'd52c3bff-459d-422a-8922-7fd3493a60c2',
            'q': {
                'FEATURE_TYPE': ofi_vars[u'object_name']
            }
        }

        resp = reqs.request('post', url, json=data)

        resp_dict = resp.json()
        search_results = resp_dict[u'result']
        records_found = len(search_results[u'records'])

        if u'success' in resp_dict and resp_dict[u'success'] and records_found > 0:
            results.update({
                u'success': True,
                u'datastore_response': search_results
            })
        else:
            results.update({
                u'success': False,
                u'error': True,
                u'error_msg': 'Datastore_search failed',
                u'datastore_response': resp_dict
            })

            if records_found == 0:
                results.update({
                    u'error_msg': 'datastore_search didn\'t find any records with given object_name',
                    u'records_found': records_found
                })
    else:
        results.update({
            u'success': False,
            u'error': True,
            u'error_msg': 'No object_name'
        })

    return results


@ofi_logic.setup_ofi_action()
def create_aoi(context, ofi_vars, ofi_resp):
    from string import Template

    results = {}

    aoi_data = ofi_vars.get('aoi_params', {})

    if u'aoi_params' not in ofi_vars:
        results.update({
            u'success': False,
            u'error': True,
            u'error_msg': u'Missing aoi parameters.'
        })
        return results

    aoi = aoi_data.get(u'aoi', [])
    aoi_coordinates = [str(item.get(u'lat', 0.0)) + ',' + str(item.get(u'lng', 0.0)) for item in aoi]
    coordinates = ' '.join(aoi_coordinates)

    aoi_str = u'<?xml version="1.0" encoding="UTF-8" ?><areaOfInterest xmlns:gml="http://www.opengis.net/gml"><gml:Polygon xmlns:gml="urn:gml"><gml:outerBoundaryIs><gml:LinearRing><gml:coordinates>$coordinates</gml:coordinates></gml:LinearRing></gml:outerBoundaryIs></gml:Polygon></areaOfInterest>'

    aoi_template = Template(aoi_str)
    aoi_xml = aoi_template.safe_substitute(coordinates=coordinates)

    data_dict = {
        u'aoi': aoi_xml,
        u'emailAddress': aoi_data.get(u'emailAddress'),
        u'featureItems': aoi_data.get(u'featureItems'),
        u'formatType': aoi_data.get(u'formatType'),
        u'useAOIBounds': u'0',
        u'aoiType': u'1',
        u'clippingMethodType': u'0',
        # crsType should always be 6, it will specify the AOI coordinates in latitude/longitude format
        u'crsType': u'6',
        u'prepackagedItems': u'',
        u'aoiName': None
    }

    log.debug(u'AOI create order data - %s', pformat(data_dict))

    if u'auth_user_obj' in context and context[u'auth_user_obj']:
        url = ofi_vars[u'ofi_url'] + u'/order/createOrderFiltered'
    else:
        url = ofi_vars[u'ofi_url'] + u'/order/createOrderFilteredSM'

    resp = reqs.request(u'post', url, json=data_dict, cookies=ofi_vars[u'cookies'])

    if resp.status_code == 200:
        results.update({
            u'order_response': resp.json()
        })

    return results
