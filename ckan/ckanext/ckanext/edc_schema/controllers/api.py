from ckan.controllers.api import ApiController

import os.path
import logging
import cgi
import datetime
import glob
import urllib

from webob.multidict import UnicodeMultiDict
from paste.util.multidict import MultiDict

import ckan.model as model
import ckan.logic as logic
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.search as search
import ckan.lib.navl.dictization_functions
import ckan.lib.jsonp as jsonp
import ckan.lib.munge as munge

from ckan.common import _, c, request, response


log = logging.getLogger(__name__)

# shortcuts
get_action = logic.get_action
NotAuthorized = logic.NotAuthorized
NotFound = logic.NotFound
ValidationError = logic.ValidationError
DataError = ckan.lib.navl.dictization_functions.DataError

IGNORE_FIELDS = ['q']
CONTENT_TYPES = {
    'text': 'text/plain;charset=utf-8',
    'html': 'text/html;charset=utf-8',
    'json': 'application/json;charset=utf-8',
}


class EDCApiController(ApiController):

    _actions = {}

    

    def i18n_js_translations(self, lang):
        ''' translation strings for front end '''
        ckan_path = os.path.join(os.path.dirname(__file__), '..')
        source = os.path.abspath(os.path.join(ckan_path, 'public',
                                 'base', 'i18n', '%s.js' % lang))
        response.headers['Content-Type'] = CONTENT_TYPES['html']
        response.headers['Cache-Control'] = 'public, max-age=31536000'
        response.headers['Pragma'] = 'cache'
        response.headers['Expires'] = 'Wed, 01 Jan 2020 07:00:00 GMT'
        response.headers['Last-Modified']  = 'Tue, 01 Jan 2013 16:00:00 GMT'    
        if not os.path.exists(source):
            return '{}'
        f = open(source, 'r')
        return(f)

   