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
@ofi_logic.check_access
@ofi_logic.setup_ofi_action(u'/info/fileFormats')
def file_formats(context, ofi_vars, ofi_resp):
    """
    Gets available file formats from DWDS.
    """
    resp_content = ofi_resp.json()

    if 'Status' in resp_content and resp_content['Status'] == 'FAILURE':
        raise OFIServiceError(_('OFI Service returning failure status - file_formats'))

    return resp_content


@toolkit.side_effect_free
@ofi_logic.check_access
@ofi_logic.setup_ofi_action(u'/info/crsTypes')
def crs_types(context, ofi_vars, ofi_resp):
    """
    Gets projection formats from DWDS.
    """
    resp_content = ofi_resp.json()

    if 'Status' in resp_content and resp_content['Status'] == 'FAILURE':
        raise OFIServiceError(_('OFI Service returning failure status - crs_types'))

    return resp_content


@ofi_logic.check_access
def geo_resource_form(context, data):
    """
    Returns the form for the OFI Manager create/edit of OFI resource.
    """
    return toolkit.render('ofi/snippets/geo_resource_form.html',
                          extra_vars=data)


@ofi_logic.check_access
@ofi_logic.setup_ofi_action()
def populate_dataset_with_ofi(context, ofi_vars, ofi_resp):
    """
    Creates the OFI resources in the dataset.
    """
    results = {}

    # error handling for adding ofi resources
    error = False
    errors = {}

    added_resources = []
    failed_resources = []

    if u'ofi_resource_info' not in ofi_vars:
        results.update(_err_dict(_('Missing ofi resource metadata'),
                                 missing_meta=True))
        return results

    file_formats = toolkit.get_action(u'file_formats')(context, ofi_vars)

    try:
        pkg_dict = toolkit.get_action(u'package_show')(context, {'id': ofi_vars[u'package_id']})
    except ValidationError as e:
        results.update(_err_dict(_('ValidationError - package_show'),
                                 errors=e.error_dict,
                                 validation_error=True))
        return results
    except NotFound as e:
        results.update(_err_dict(_('NotFound - package_show'),
                                 package_id=ofi_vars[u'package_id'],
                                 not_found_error=True))
        return results

    # If the dataset has no object name set, the `force_populate`
    #  parameter must be included in the request
    if u'object_name' not in pkg_dict or not pkg_dict['object_name']:
        if u'force_populate' not in ofi_vars or not ofi_vars['force_populate']:
            msg = 'No Object Name in dataset. Must include `force_populate: true` parameter ' \
                  'in the request if you wish to create the DWDS resources without an object name.'
            error_dict = {
                'missing': msg
            }

            results.update(_err_dict(_('No Object Name'),
                                     errors=error_dict,
                                     no_object_name=True))
            return results

    resource_meta = {
        u'package_id': pkg_dict['id'],
        u'resource_storage_access_method': u'Indirect Access',
        u'resource_storage_location': u'BCGW DataStore',
        u'projection_name': u'EPSG_3005 - NAD83 BC Albers',
        u'edc_resource_type': u'Data',
        u'ofi': True,
    }
    resource_meta.update(ofi_vars[u'ofi_resource_info'])

    ofi_exists = False
    for resource in pkg_dict[u'resources']:
        if u'ofi' in resource and resource['ofi']:
            ofi_exists = True
            results.update(ofi_exists=ofi_exists)
            break

    if not ofi_exists:
        # Try to add all avaliable OFI formats
        for file_format in file_formats:
            resource_url = h.url_for('ofi resource',
                                     format=file_format[u'formatname'],
                                     object_name=pkg_dict.get(u'object_name',
                                                              "__MISSING_OBJECT_NAME__"),
                                     qualified=True)

            resource_name = file_format[u'formatname']

            resource_meta.update(name=resource_name,
                                 url=resource_url,
                                 format=file_format[u'formatname'])

            try:
                resource = toolkit.get_action(u'resource_create')(context, resource_meta)
                added_resources.append(resource)

            except ValidationError as e:
                error = True
                errors.update(e.error_dict)
                failed_resources.append({
                    u'resource': resource_meta,
                    u'error_msg': _('ValidationError - resource_create'),
                    u'errors': e.error_dict
                })

    if error:
        results.update(_err_dict(_('Adding OFI resources failed.'),
                                 errors=errors,
                                 file_formats=file_formats,
                                 failed_resources=failed_resources,
                                 added_resources=added_resources))
        return results

    # Updates the dataset to be active and not a draft
    if u'object_name' in pkg_dict and pkg_dict['object_name']:
        pkg_dict = toolkit.get_action(u'package_show')(context, {'id': ofi_vars[u'package_id']})

        pkg_dict.update({
            u'state': u'active'
        })
        pkg_dict = toolkit.get_action(u'package_update')(context, pkg_dict)

    results.update(success=True,
                   added_resources=added_resources,
                   failed_resources=failed_resources)

    return results


@toolkit.side_effect_free
@ofi_logic.check_access
@ofi_logic.setup_ofi_action(u'/security/productAllowedByFeatureType/')
def check_object_name(context, ofi_vars, ofi_resp):
    """
    Checks to see if the object_name is accessible for the user.
    """
    success = True if ofi_resp.status_code == 200 else False
    content_type = ofi_resp.headers.get(u'content-type').split(';')[0]

    if content_type == 'text/html':
        success = False
        # not sure yet, but if the content is the IDIR login page,
        # it will try to redirect the user to log into IDIR
        # if the page then displays 404, it's most likey the user isn't
        # logged onto the vpn
        content = ofi_resp.content
    else:
        content = ofi_resp.json()

    results = {
        u'success': success,
        u'content': content
    }

    return results


@ofi_logic.check_access
@ofi_logic.setup_ofi_action()
def remove_ofi_resources(context, ofi_vars, ofi_resp):
    """
    Removes OFI resources from the dataset.
    """
    pkg_dict = toolkit.get_action(u'package_show')(context, {'id': ofi_vars[u'package_id']})

    resources_to_keep = []
    for resource in pkg_dict[u'resources']:
        if u'ofi' not in resource or resource[u'ofi'] is False:
            resources_to_keep.append(resource)

    pkg_dict[u'resources'] = resources_to_keep

    results = {}

    try:
        package_id = toolkit.get_action(u'package_update')(context, pkg_dict)
        results.update(success=True,
                       package_id=package_id)

    except (NotFound, ValidationError) as e:
        results.update(_err_dict(_(e)))

    return results


@toolkit.side_effect_free
@ofi_logic.check_access
@ofi_logic.setup_ofi_action()
def edit_ofi_resources(context, ofi_vars, ofi_resp):
    """
    Edits the OFI resources that are in the dataset.

    When requesting with GET it provides the first OFI resource in the results
    to use as a basis for the edit form in the OFI Manager.

    POST will edit the ofi resources in the dataset.
    """
    pkg_dict = toolkit.get_action(u'package_show')(context, {'id': ofi_vars[u'package_id']})

    results = {}

    # get all ofi resources in the dataset
    ofi_resources = [i for i in pkg_dict[u'resources'] if u'ofi' in i and i[u'ofi']]

    if toolkit.request.method == 'GET':
        # get the first ofi resource, it doesn't matter which type it is
        is_ofi_res = ofi_resources[0] or False

        # just the format names from the ofi api call
        # TODO: maybe store both the format name and id in the resource meta data?
        file_formats = [i[u'format'] for i in ofi_resources if u'format' in i]

        if is_ofi_res:
            results.update({
                u'success': True,
                u'render_form': True,
                u'ofi_resource': is_ofi_res,
                u'file_formats': file_formats
            })
        else:
            results.update(_err_dict(_('OFI resource not found.')))
            return results
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
            updated_resources = [i for i in updated_dataset[u'resources']
                                 if u'ofi' in i and i[u'ofi']]

            results.update({
                u'success': True,
                u'updated': True,
                u'updated_resources': updated_resources
            })
        except (NotFound, ValidationError) as e:
            results.update(_err_dict(_(e.error_summary),
                           updated=False,
                           errors=e.error_dict))

    return results


@toolkit.side_effect_free
@ofi_logic.check_access
@ofi_logic.setup_ofi_action(u'/security/productAllowedByFeatureType/')
def get_max_aoi(context, ofi_vars, ofi_resp):
    """
    Gets the max area of interest for an object name.

    The list is stored in a resource in catalogue (prod)

    A query is maded using the datastore api to get the max aoi.

    A user check is made for the object_name before getting the max aoi.
    """
    results = {}

    content_type = ofi_resp.headers.get(u'content-type').split(';')[0]

    if ofi_resp.status_code == 200 and content_type == 'application/json':
        resp_dict = ofi_resp.json()
        if u'allowed' in resp_dict:
            if resp_dict[u'allowed'] is False:
                eas_login = edc_h.get_eas_login_url() or '/user/login'

                not_allowed_msg = ('This is a dataset with restricted access. '
                                   'To place an order for download please '
                                   '<a href=\"%s\" style=\"text-decoration: underline; color: #1A5A96\">login</a> first. '
                                   'If you are logged in and still cannot place an order, '
                                   'please email the listed dataset \'Contact\' to request access.') % eas_login
                results.update(_err_dict(not_allowed_msg,
                                         user_allowed=resp_dict[u'allowed'],
                                         content=resp_dict))
                return results
            else:
                results.update({
                    u'content': resp_dict,
                    u'user_allowed': resp_dict[u'allowed']
                })
    elif content_type == 'text/html':
        api_url = ofi_vars[u'api_url'] if u'api_url' in ofi_vars else ''
        results.update(_err_dict(_('Please log in with your IDIR credentials'),
                                 idir_req=True, idir_login=_(ofi_resp.text)))
        return results
    else:
        results.update(_err_dict(_(ofi_resp.text)))
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

        if u'success' in resp_dict and resp_dict[u'success']:
            if records_found > 0:
                results.update({
                    u'success': True,
                    u'datastore_response': search_results
                })
            else:
                results.update({
                    u'msg': _('datastore_search didn\'t find any records with given object_name'),
                    u'records_found': records_found,
                    u'datastore_response': search_results,
                    u'no_records': True
                })
        else:
            results.update(_err_dict(_('Datastore_search failed.'),
                                     datastore_response=resp_dict,
                                     datastore_fail=True))
    else:
        results.update(_err_dict(_('No object_name'),
                                 no_object_name=True))

    return results


@ofi_logic.check_access
@ofi_logic.setup_ofi_action()
def ofi_create_order(context, ofi_vars, ofi_resp):
    """
    Places an order to DWDS

    The first call places the order to DWDS.
    If the order was a public call, a json object is returned.

    If the order is a secure order, then the first call response from DWDS
    is a UUID, a second call is then made to get the order status using
    the UUID from the first call.
    """
    from string import Template
    from validate_email import validate_email

    results = {}

    aoi_data = ofi_vars.get('aoi_params', {})

    if not aoi_data:
        results.update(_err_dict(_('Missing aoi parameters.'), missing_aoi=True))
        return results

    if u'consent' in aoi_data:
        if toolkit.asbool(aoi_data[u'consent']) is False:
            results.update(_get_consent_error(u'You must agree to the terms before placing an order.'))
            return results
    else:
        results.update(_get_consent_error(u'Consent agreement missing.'))
        return results

    if not validate_email(aoi_data.get(u'emailAddress', '')):
        results.update(_err_dict(_(u'Email address is invalid.'), invalid_email=True))
        return results

    projection_id = aoi_data.get('projection')
    if not projection_id:
        results.update(_err_dict(_(u'Missing CRS Type (map projection).'), missing_crsType=True))
        return results

    # Beginning of create order for ofi resource
    aoi = aoi_data.get(u'aoi', [])

    # if no aoi coords, then assume that the user wants the whole province
    # aoi param to dwds call will be undefined and aoiType = '0' for No Area of Interest Applied
    aoi_doc = None
    aoi_type = u'0'

    if aoi:
        # flipping coordinate values to y,x because that's what's required for submittion
        # otherwise the coordinates appeared mirrored on the global map
        aoi_coordinates = [str(item.get(u'lng', 0.0)) + ',' + str(item.get(u'lat', 0.0)) for item in aoi]
        coordinates = ' '.join(aoi_coordinates)

        aoi_str = u'''
        <?xml version=\"1.0\" encoding=\"UTF-8\" ?>
        <areaOfInterest xmlns:gml=\"http://www.opengis.net/gml\">
            <gml:Polygon xmlns:gml=\"urn:gml\" srsName=\"EPSG:4326\">
                <gml:outerBoundaryIs>
                    <gml:LinearRing>
                        <gml:coordinates>$coordinates</gml:coordinates>
                    </gml:LinearRing>
                </gml:outerBoundaryIs>
            </gml:Polygon>
        </areaOfInterest>'''

        aoi_template = Template(aoi_str)
        aoi_doc = aoi_template.safe_substitute(coordinates=coordinates)
        aoi_type = u'1'

    data_dict = {
        u'aoi': aoi_doc,
        u'emailAddress': aoi_data.get(u'emailAddress'),
        u'featureItems': aoi_data.get(u'featureItems'),
        u'formatType': _get_format_id(aoi_data.get(u'format')),
        u'useAOIBounds': u'0',
        u'aoiType': aoi_type,
        u'clippingMethodType': u'0',
        u'crsType': projection_id,
        u'prepackagedItems': u'',
        u'aoiName': None
    }

    log.debug(u'OFI create order data - %s', pformat(data_dict))

    if u'auth_user_obj' in context and context[u'auth_user_obj']:
        # if this url has secure in the path, need to fix it because it's not correct for secure create order calls
        url = edc_h._build_ofi_url(False) + u'/order/createOrderFilteredSM'
        call_type = 'secure'
    else:
        url = ofi_vars[u'ofi_url'] + u'/order/createOrderFiltered'
        call_type = 'public'

    resp = reqs.request(u'post', url, json=data_dict, cookies=ofi_vars[u'cookies'])

    log.debug(u'OFI create order call type - %s', call_type)
    log.debug(u'OFI create order call url - %s', url)
    log.debug(u'OFI create order response headers - %s', pformat(resp.headers))

    results.update({
        u'order_sent': data_dict,
        u'api_url': url
    })

    def _ofi_order_response(resp_dict):
        """
        Helper function for dealing with ofi create order response
        """
        order_resp = {}
        if u'Status' in resp_dict:
            if resp_dict[u'Status'] == u'SUCCESS':
                order_resp.update({
                    u'order_id': resp_dict[u'Value'],
                    u'order_response': resp_dict
                })
            else:
                order_resp.update(_err_dict(_(resp_dict[u'Description']),
                                  order_response=resp_dict, order_failed=True))

        return order_resp

    if resp.status_code != 200:
        msg = _('OFI public create order failed - %s') % ofi_vars[u'ofi_url']
        results.update(_err_dict(msg,
                                 order_response=resp.text, order_status=resp.status_code))
        return results

    content_type = resp.headers.get(u'content-type').split(';')[0]

    # public order
    if content_type == 'application/json':
        results.update(_ofi_order_response(resp.json()))

    # secured order for logged in users
    elif content_type == 'text/plain':
        # assuming the response text is the uuid
        ofi_uuid = resp.text

        # need to have a secure url for this call, because that's what's required
        sm_url = edc_h._build_ofi_url(True) + u'/order/createOrderFiltered/' + ofi_uuid
        sm_cookie = {
            u'SMSESSION': resp.cookies.get(u'SMSESSION', '')
        }

        # call
        sm_resp = reqs.get(sm_url, cookies=sm_cookie)

        log.debug(u'OFI SiteMinner api uuid - %s', ofi_uuid)
        log.debug(u'OFI SiteMinner api url - %s', sm_url)
        log.debug(u'OFI SiteMinner api headers - %s', pformat(sm_resp.headers))

        sm_content_type = sm_resp.headers.get(u'content-type').split(';')[0]

        if sm_resp.status_code != 200:
            msg = _('OFI secure create order failed - %s ') % sm_url
            results.update(_err_dict(msg,
                                     sm_url=sm_url, sm_failed=True, sm_uuid=ofi_uuid))
            return results

        if sm_content_type == 'application/json':
            results.update(_ofi_order_response(sm_resp.json()))
        else:
            results.update(_err_dict(_('OFI secure create order returned unexpected response.'),
                                     sm_url=sm_url, sm_failed=True, sm_uuid=ofi_uuid, sm_resp=sm_resp.text))

    else:
        results.update(_err_dict(_('Bad request from initial ofi create order.'),
                                 order_response=resp.text, order_type=content_type))

    return results


def _get_consent_error(msg):
    consent_agreement = ('The information on this form is collected under the authority of Sections 26(c) and 27(1)(c) '
                         'of the Freedom of Information and Protection of Privacy Act [RSBC 1996 c.165], and will help '
                         'us to assess and respond to your enquiry. '
                         'By consenting to submit this form you are confirming that you are authorized to provide '
                         'information of individuals/organizations/businesses for the purpose of your enquiry.')

    return _err_dict(msg, no_consent=True, consent_agreement=consent_agreement)


def _err_dict(error_msg, **kw):
    """
    Basic error dictionary, added arguments that are included,
    will be added to the error_dict.
    Saves setup time for returning an error dictionary.

    **kw args are key/value pairs in the error dictionary
    """
    error_dict = {
        u'success': False,
        u'error': True,
        u'error_msg': error_msg,
    }

    error_dict.update(kw)

    return error_dict


def _get_format_id(format_name):
    """
    Getting the file format ID by format name.
    """
    file_formats = toolkit.get_action('file_formats')({}, {})

    format_id = None

    for file_format in file_formats:
        if file_format[u'formatname'] == format_name:
            format_id = str(file_format[u'formatID'])
            break

    return format_id
