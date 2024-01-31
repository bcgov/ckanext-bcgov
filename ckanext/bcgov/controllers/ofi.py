# Copyright 2016, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license
#
# Highway Three Solutions Inc.
# Author: Jared Smith <github@jrods>

import logging
from pprint import pformat


# from ckan.controllers.api import ApiController
import ckan.views.api as api
# TODO: Change api to appropriate variable

# from requests.exceptions import ConnectionError

# import ckan
# import ckan.lib.base as base
# import ckan.lib.helpers as h
import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckantoolkit import config
import ckanext.bcgov.util.helpers as edc_h
# TODO: Remove blurpint import here after testing
from flask import Blueprint

from ckanext.bcgov.logic.ofi import OFIServiceError

# try:
#     # CKAN 2.7 and later
#     from ckan.common import config
# except ImportError:
#     # CKAN 2.6 and earlier
#     from pylons import config


# shortcuts
_ = toolkit._   
log = logging.getLogger('ckanext.bcgov.controllers.ofi')


# # class EDCOfiController(ApiController):
# def __init__(self):
#     self.config = edc_h.get_ofi_config()

# ofi_api_blueprint = Blueprint('ofi_api_blueprint', __name__)
# @ofi_api_blueprint.route('/api/ofi/<call_action>', methods=['GET', 'POST'])
def action(call_action, ver=None):
    """
    OFI API endpoint

    REST interface for call_action funtions.
    """
    context = {
        'model': model,
        'session': model.Session,
        'user': toolkit.c.user,
        'api_version': ver,
        'auth_user_obj': toolkit.c.userobj
    }

    data = {}
    config = edc_h.get_ofi_config()

    try:
        action_func = toolkit.get_action(call_action)
        side_effect_free = getattr(action_func, 'side_effect_free', False)

        # query_params = self._get_request_data(side_effect_free)
        query_params = api._get_request_data(side_effect_free)


        pkg_id = query_params.get('package_id', '')

        data.update({
            'package_id': pkg_id,
            'object_name': query_params.get('object_name', ''),
            'secure': query_params.get('secure', False)
        })
    except ValueError as e:
        # return api._finish_bad_request(str(e))
        return api._finish_bad_request(str(e))


    log.debug('OFI api config:\n %s \n', pformat(config))
    log.debug('OFI api context:\n %s\n', pformat(context))
    log.info('OFI action call: %s' % call_action)

    # Not ideal, but all cases involve calling the action_func,
    #  which could throw a NotAuthorized exception
    try:
        if call_action == 'populate_dataset_with_ofi':
            data.update({
                'force_populate': toolkit.asbool(query_params.get('force_populate', False)),
                'ofi_resource_info': query_params.get('ofi_resource_info', {})
            })

            context.update({
                'allow_state_change': True
            })

            populate_results = action_func(context, data)

            if str(toolkit.request.accept) == 'application/json':
                return api._finish(200, populate_results, 'json')
            else:
                if 'error' in populate_results and populate_results['error']:
                    failed_render = toolkit.render('ofi/snippets/geo_resource_form.html', extra_vars=populate_results)
                    return api._finish(400, failed_render, 'html')

                return toolkit.render('ofi/snippets/populate_success.html', extra_vars=populate_results)

        elif call_action == 'geo_resource_form':
            data.update(force_populate=toolkit.asbool(query_params.get('force_populate')))

            return action_func(context, data)

        elif call_action == 'file_formats':
            return api._finish_ok(action_func(context, data))

        elif call_action == 'crs_types':
            return api._finish_ok(action_func(context, data))

        elif call_action == 'get_max_aoi':
            max_aoi = action_func(context, data)

            if 'error' in max_aoi and max_aoi['error']:
                render = toolkit.render('ofi/mow/errors.html', extra_vars=max_aoi)
                return api._finish(200, render, 'html')

            return api._finish_ok(max_aoi)

        elif call_action == 'ofi_create_order':
            # expecting params to be in the 'aoi_params' obj
            data.update(query_params)

            create_order = action_func(context, data)

            if 'error' in create_order and create_order['error']:
                return api._finish(400, create_order, 'json')

            return api._finish_ok(create_order)

        elif call_action == 'remove_ofi_resources':
            remove_results = action_func(context, data)

            if 'error' in remove_results and remove_results['error']:
                return api._finish_bad_request(_(remove_results['error_msg']))

            return api._finish_ok(remove_results)

        elif call_action == 'edit_ofi_resources':
            data.update({
                'ofi_resource_info': query_params.get('ofi_resource_info', {})
            })

            edit_resources = action_func(context, data)

            if 'error' in edit_resources and edit_resources['error']:
                return api._finish_bad_request(_(edit_resources['error_msg']))

            elif 'render_form' in edit_resources and edit_resources['render_form']:
                return toolkit.render('ofi/snippets/geo_resource_form.html', extra_vars=edit_resources)

            elif 'updated' in edit_resources:
                if edit_resources['updated']:
                    return toolkit.render('ofi/snippets/populate_success.html', extra_vars=edit_resources)
                else:
                    return toolkit.render('ofi/snippets/populate_failed.html', extra_vars=edit_resources)

            else:
                return api._finish_bad_request(_('Something went wrong with editing ofi resources.'))

        else:
            # return self._finish_not_found(_('OFI API Controller action not found: %s') % call_action)
            return api._finish_bad_request(_('OFI API Controller action not found: %s') % call_action) #TODO: Ask John is this correct way as orig deleted


    except toolkit.NotAuthorized as e:
        # return self._finish_not_authz(_('Not authorized to call %s') % call_action)
        return api._finish_bad_request(_('Not authorized to call %s') % call_action) #TODO: Ask John is this correct way as orig deleted


    except OFIServiceError as e:
        error = {
            'success': False,
            'error': 'OFIServiceError',
            'error_msg': e.value if config.get('debug', False) else 'The data warehouse service is not available.'
        }
        return api._finish(500, error, content_type='json')
