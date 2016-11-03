# Copyright 2016, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license
#
# Highway Three Solutions Inc.
# Author: Jared Smith <github@jrods>

from ckan.controllers.api import ApiController

import cgi
import logging
import requests as reqs
from pprint import pformat, pprint
import urlparse

# import ckan
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import ckanext.bcgov.util.helpers as edc_h

from ckan.common import _, c, request, response

try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config

# shortcuts
get_action = logic.get_action
NotAuthorized = logic.NotAuthorized
NotFound = logic.NotFound
ValidationError = logic.ValidationError

log = logging.getLogger(u'ckanext.bcgov.controllers.ofi')


class EDCOfiController(ApiController):
    def __init__(self):
        self.config = edc_h.get_ofi_config()

    def action(self, call_action, object_name=None, ver=None):
        '''
        API Entry
        TODO
        '''
        context = {
            u'model': model,
            u'session': model.Session,
            u'user': c.user,
            u'api_version': ver,
            u'auth_user_obj': c.userobj
        }

        try:
            function = get_action(call_action)
        except KeyError:
            return self._finish_bad_request(_('Action name not known: %s') % call_action)

        side_effect_free = getattr(function, 'side_effect_free', False)

        log.debug(u'OFI api config:\n %s \n', pformat(self.config))
        log.debug(u'OFI api context:\n %s\n', pformat(context))

        return base.abort(501, _('TODO in OFI API Controller: %s') % call_action)

    def _call_action_show(self):
        action_map = {
            u'info': 'OFI ckan api call_actions',
            u'call_action': {
                u'check_object_name': {
                    u'about': u'Api call to OFI to check Object availability.',
                    u'url': h.url_for('ofi api', call_action='check_object_name'),
                    u'params': {
                        u'object_name': u'',
                        u'secure': u''
                    }
                },
                u'file_formats': {
                    u'about': u'List of available file formats.',
                    u'url': h.url_for('ofi api', call_action='file_formats')
                },
                u'create_order': {
                    u'about': u'TODO: Create an order to OFI',
                    u'url': h.url_for('ofi api', call_action='create_order'),
                    u'params': {
                        u'test': u''
                    }
                }
            }
        }
        return self._finish_ok(action_map)
