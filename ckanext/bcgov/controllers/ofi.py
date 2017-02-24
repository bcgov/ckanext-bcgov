# Copyright 2016, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license
#
# Highway Three Solutions Inc.
# Author: Jared Smith <github@jrods>

from ckan.controllers.api import ApiController

import logging
from pprint import pformat, pprint

# import ckan
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import ckanext.bcgov.util.helpers as edc_h

try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config

# shortcuts
_ = toolkit._

log = logging.getLogger(u'ckanext.bcgov.controllers.ofi')


class EDCOfiController(ApiController):
    def __init__(self):
        self.config = edc_h.get_ofi_config()

    def action(self, call_action, ver=None):
        """
        OFI API endpoint

        REST interface for call_action funtions.
        """
        context = {
            u'model': model,
            u'session': model.Session,
            u'user': toolkit.c.user,
            u'api_version': ver,
            u'auth_user_obj': toolkit.c.userobj
        }

        data = {}

        try:
            action_func = toolkit.get_action(call_action)
            side_effect_free = getattr(action_func, 'side_effect_free', False)

            query_params = self._get_request_data(side_effect_free)

            pkg_id = query_params.get(u'package_id', '')

            data.update({
                u'package_id': pkg_id,
                u'object_name': query_params.get(u'object_name', ''),
                u'secure': query_params.get(u'secure', False)
            })
        except ValueError, e:
            return self._finish_bad_request(unicode(e))

        log.debug(u'OFI api config:\n %s \n', pformat(self.config))
        log.debug(u'OFI api context:\n %s\n', pformat(context))

        # Not ideal, but all cases involve calling the action_func,
        #  which could throw a NotAuthorized exception
        try:
            if call_action == 'populate_dataset':
                data.update({
                    u'ofi_resource_info': query_params.get(u'ofi_resource_info', {})
                })

                context.update({
                    'allow_state_change': True
                })

                populate_results = action_func(context, data)

                if 'error' in populate_results and populate_results['error']:
                    failed_render = toolkit.render('ofi/snippets/geo_resource_form.html', extra_vars=populate_results)
                    return self._finish(400, failed_render, 'html')

                return toolkit.render('ofi/snippets/populate_success.html', extra_vars=populate_results)

            elif call_action == 'geo_resource_form':
                return action_func(context, data)

            elif call_action == 'file_formats':
                return self._finish_ok(action_func(context, data))

            elif call_action == 'crs_types':
                return self._finish_ok(action_func(context, data))

            elif call_action == 'get_max_aoi':
                max_aoi = action_func(context, data)

                if u'error' in max_aoi and max_aoi[u'error']:
                    render = toolkit.render('ofi/mow/errors.html', extra_vars=max_aoi)
                    return self._finish(200, render, 'html')

                return self._finish_ok(max_aoi)

            elif call_action == 'ofi_create_order':
                # expecting params to be in the 'aoi_params' obj
                data.update(query_params)

                create_order = action_func(context, data)

                if u'error' in create_order and create_order[u'error']:
                    return self._finish(400, create_order, 'json')

                return self._finish_ok(create_order)

            elif call_action == 'remove_ofi_resources':
                remove_results = action_func(context, data)

                if 'error' in remove_results and remove_results[u'error']:
                    return self._finish_bad_request(_(remove_results[u'error_msg']))

                return self._finish_ok(remove_results)

            elif call_action == 'edit_ofi_resources':
                data.update({
                    u'ofi_resource_info': query_params.get(u'ofi_resource_info', {})
                })

                edit_resources = action_func(context, data)

                if 'error' in edit_resources and edit_resources[u'error']:
                    return self._finish_bad_request(_(edit_resources[u'error_msg']))

                elif 'render_form' in edit_resources and edit_resources[u'render_form']:
                    return toolkit.render('ofi/snippets/geo_resource_form.html', extra_vars=edit_resources)

                elif 'updated' in edit_resources:
                    if edit_resources[u'updated']:
                        return toolkit.render('ofi/snippets/populate_success.html', extra_vars=edit_resources)
                    else:
                        return toolkit.render('ofi/snippets/populate_failed.html', extra_vars=edit_resources)

                else:
                    return self._finish_bad_request(_('Something went wrong with editing ofi resources.'))

            else:
                return self._finish_not_found(_('OFI API Controller action not found: %s') % call_action)

        except toolkit.NotAuthorized, e:
            return self._finish_not_authz(_('Not authorized to call %s') % call_action)
