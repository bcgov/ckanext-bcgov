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
# get_action = toolkit.get_action
# NotAuthorized = logic.NotAuthorized
# NotFound = logic.NotFound
# ValidationError = logic.ValidationError

log = logging.getLogger(u'ckanext.bcgov.controllers.ofi')


class EDCOfiController(ApiController):
    def __init__(self):
        self.config = edc_h.get_ofi_config()

    def action(self, call_action, ver=None):
        '''
        API Entry
        TODO
        '''
        context = {
            u'model': model,
            u'session': model.Session,
            u'user': toolkit.c.user,
            u'api_version': ver,
            u'auth_user_obj': toolkit.c.userobj
        }

        data = {}

        try:
            toolkit.check_access(call_action, context, {})
            action_func = toolkit.get_action(call_action)
            side_effect_free = getattr(action_func, 'side_effect_free', False)

            query_params = self._get_request_data(side_effect_free)

            data.update({
                u'package_id': query_params.get(u'package_id', ''),
                u'object_name': query_params.get(u'object_name', ''),
                u'secure': query_params.get(u'secure', False)
            })
        except toolkit.NotAuthorized, e:
            return self._finish_not_authz(_('Not authorized to call %s') % call_action)
        except ValueError, e:
            return self._finish_bad_request(unicode(e))

        log.debug(u'OFI api config:\n %s \n', pformat(self.config))
        log.debug(u'OFI api context:\n %s\n', pformat(context))

        if call_action == 'populate_dataset':
            data.update({
                u'ofi_resource_info': query_params.get(u'ofi_resource_info', {})
            })

            populate_results = action_func(context, data)

            if 'error' in populate_results and populate_results['error']:
                return toolkit.render('ofi/snippets/populate_failed.html', extra_vars=populate_results)

            return toolkit.render('ofi/snippets/populate_success.html', extra_vars=populate_results)

        elif call_action == 'geo_resource_form':
            return action_func(context, data)
        elif call_action == 'file_formats':
            return self._finish_ok(action_func(context, {}))
        else:
            return base.abort(501, _('TODO in OFI API Controller: %s') % call_action)
