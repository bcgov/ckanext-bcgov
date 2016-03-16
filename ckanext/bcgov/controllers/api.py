# Copyright  2015, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license

from ckan.controllers.api import ApiController

import os.path
import logging
import cgi
import glob
import urllib
import pprint
import json

from paste.util.multidict import MultiDict

import ckan.model as model
import ckan.lib.dictization.model_dictize as model_dictize

import ckan.logic as logic
import ckan.lib.navl.dictization_functions

from ckan.common import _, c, request, response
from ckanext.bcgov.util.util import (get_all_orgs,
                                          get_organization_branches,
                                          get_parent_orgs)

log = logging.getLogger('ckanext.edc_schema')

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

#By default package_list returns only the last 10 modified records
default_limit = 100000000
default_offset = 0

class EDCApiController(ApiController):

    _actions = {}



    def i18n_js_translations(self, lang):
        ''' translation strings for front end '''
        ckan_path = os.path.join(os.path.dirname(__file__), '..')
        source = os.path.abspath(os.path.join(ckan_path, 'public',
                                 'base', 'i18n', '%s.js' % lang))
        # FIXME: cache everything forever?
        response.headers['Content-Type'] = CONTENT_TYPES['html']
        response.headers['Cache-Control'] = 'public, max-age=31536000'
        response.headers['Pragma'] = 'cache'
        response.headers['Expires'] = 'Wed, 01 Jan 2020 07:00:00 GMT'
        response.headers['Last-Modified']  = 'Tue, 01 Jan 2013 16:00:00 GMT'
        if not os.path.exists(source):
            return '{}'
        f = open(source, 'r')
        return(f)


    def _get_package_list(self, context, ver=None):
        '''
        Returns a list of site packages depending on the user.
        The public users could only see published public records.
        Each user can only see private records of his/her own organization
        '''
        # FIXME: override with IActions plugin instead
        from ckan.lib.search import SearchError

        help_str = "Return a list of the names of the site's datasets (packages).\n\n    " + \
                    ":param limit: if given, the list of datasets will be broken into pages of\n" + \
                    "        at most ``limit`` datasets per page and only one page will be returned\n" + \
                    "        at a time (optional)\n    :type limit: int\n    :param offset: when ``limit`` " + \
                    "is given, the offset to start returning packages from\n    :type offset: int\n\n" + \
                    "    :rtype: list of strings\n\n    "

        return_dict = {"help": help_str}

        #Get request parameters (number of records to be returned and the starting package)
        try:
            limit = int(request.params.get('limit', default_limit))
        except ValueError:
            limit = default_limit
        try:
            offset = int(request.params.get('offset', default_offset))
        except ValueError:
            offset = 0

        try :
            data_dict = {
                         'q' : '',
                         'fq' : '',
                         'start' : offset,
                         'rows' : limit,
                         'sort' : 'views_total desc'
                        }
            #Use package_search to filter the list
            query = get_action('package_search')(context, data_dict)
        except SearchError, se :
            print 'Search error', str(se)
            return self._finish_bad_request()

        result = []
        for pkg in query['results']:
            result.append(pkg['name'])

        return_dict['success'] = True
        return_dict['result'] = result
        return self._finish_ok(return_dict)


    def _get_package_list_with_resources(self, context, ver):
        '''
        Returns a list of site packages depending on the user.
        The public users could only see published public records.
        Each user can only see private records of his/her own organization
        '''
        # FIXME: override with IActions plugin instead
        from ckan.lib.search import SearchError

        help_str = "Returns a list of the names of top 10 most viewed datasets (packages).\n\n    " + \
                    ":param limit: if given, the list of datasets will be broken into pages of\n" + \
                    "        at most ``limit`` datasets per page and only one page will be returned\n" + \
                    "        at a time (optional)\n    :type limit: int\n    :param offset: when ``limit`` " + \
                    "is given, the offset to start\n        returning packages from\n    :type offset: int\n\n" + \
                    "    :rtype: list of strings\n\n    "

        return_dict = {"help": help_str}

        #Get request parameters (number of records to be returned and the starting package)
        try:
            limit = int(request.params.get('limit', default_limit))
        except ValueError:
            limit = default_limit

        try:
            offset = int(request.params.get('offset', default_offset))
        except ValueError:
            offset = 0

        try :
            data_dict = {
                         'q' : '',
                         'fq' : '',
                         'start' : offset,
                         'rows' : limit,
                         'sort' : 'views_total desc'
                        }

            #Use package_search to filter the list
            query = get_action('package_search')(context, data_dict)
        except SearchError, se :
            print 'Search error', str(se)
            return self._finish_bad_request()

        return_dict['success'] = True
        return_dict['result'] = query['results']
        return self._finish_ok(return_dict)


    def _package_show(self, context, pkg_id):
        '''
        Returns record's data with the given id only if the user is allowed to view the record.
        '''
        # FIXME: use IAuth plugin for authorization check and
        # use IPackageController to fill in extra values
        # then remove this method

        help_str = "Shows the package info with the given id. Param : id"

        return_dict = {"help": help_str}
        try :
            pkg = get_action('package_show')(context, {'id' : pkg_id})

            #add the top-level org to the organization
            #'organization, branch'
#            orgs = get_all_orgs()
            org = model.Group.get(pkg['org'])
#            org=orgs[pkg['org']]
            branch = model.Group.get(pkg['sub_org'])
#            branch=orgs[pkg['sub_org']]
#            org_title = org['title']
#            branch_title = branch['title']
            org_title = ''
            branch_title = ''
            if org :
                org_title = org.title
            if branch :
                branch_title = branch.title

            if pkg['organization']:
                pkg['organization']['full_title'] = org_title + ', ' + branch_title

            from ckanext.bcgov.util.helpers import record_is_viewable

            if not record_is_viewable(pkg, c.userobj) :
                return_dict['success'] = False
                return_dict['error'] = {'__type': 'Authorization Error', 'message': _('Access denied')}
                return self._finish(403, return_dict, content_type='json')
            return_dict['success'] = True
            return_dict['result'] = pkg
        except NotFound, e:
            return_dict['error'] = {'__type': 'Not Found Error',
                                    'message': _('Not found')}
            if hasattr(e, 'extra_msg'):
                return_dict['error']['message'] += ': %s' % e.extra_msg
            return_dict['success'] = False
            return self._finish(404, return_dict, content_type='json')
        except ValidationError, e:
            error_dict = e.error_dict
            error_dict['__type'] = 'Validation Error'
            return_dict['error'] = error_dict
            return_dict['success'] = False
            # CS nasty_string ignore
            log.error('Validation error: %r' % str(e.error_dict))
            return self._finish(200, return_dict, content_type='json')

        return self._finish_ok(return_dict)

    def organization_list_related(self, ver=None):
        '''
        Returns the list of organizations including parent_of and child_of relationships.
        '''
        # FIXME: use IActions plugin instead
        from ckan.lib.search import SearchError

        help_str =  "Return a list of the names of the site's organizations.\n\n" + \
                    ":param order_by: the field to sort the list by, must be ``'name'`` or \n" + \
                    " ``'packages'`` (optional, default: ``'name'``) Deprecated use sort. \n" + \
                    ":type order_by: string \n" + \
                    ":param sort: sorting of the search results.  Optional.  Default:\n" + \
                    "'name asc' string of field name and sort-order. The allowed fields are \n" + \
                    "'name' and 'packages' \n" + \
                    ":type sort: string \n" + \
                    ":param organizations: a list of names of the groups to return, if given only \n" + \
                    "groups whose names are in this list will be returned (optional) \n" + \
                    ":type organizations: list of strings \n" + \
                    ":param all_fields: return full group dictionaries instead of  just names \n" + \
                    "(optional, default: ``False``) \n" + \
                    ":type all_fields: boolean \n" + \
                    ":rtype: list of strings \n"

        return_dict = {"help": help_str}

        data_dict = self._get_request_data(try_url_params=True)
        all_fields = data_dict.get('all_fields', False)
        order_by = data_dict.get('order_by', 'name')
        sort = data_dict.get('sort', 'name asc')
        organizations = data_dict.get('organizations', [])



        context = {'model': model, 'session': model.Session, 'user': c.user,
                   'api_version': ver, 'auth_user_obj': c.userobj}

        org_list = get_action('organization_list')(context, data_dict)

        if (all_fields):

            #add the child orgs to the response:
            for org in org_list:
                children = []
                branches = get_organization_branches(org['id'])
                group_list = model_dictize.group_list_dictize(branches, context)
                for branch in group_list:
                    d = {}
                    d['title'] = branch['title']
                    children.append(d)

                org['parent_of'] = children

                parents = []
                branches = get_parent_orgs(org['id'])
                group_list = model_dictize.group_list_dictize(branches, context)
                for branch in group_list:
                    d = {}
                    d['title'] = branch['title']
                    parents.append(d)
                org['child_of'] = parents

        return_dict['success'] = True
        return_dict['result'] = org_list
        return self._finish_ok(return_dict)

    def _get_recently_changed_packages_activity_list(self, context, ver):
        # FIXME: use IAuth plugin instead
        if c.userobj and c.userobj.sysadmin == True:
            return super(EDCApiController, self).action('recently_changed_packages_activity_list', ver)
        else:
            return_dict = {}
            return_dict['success'] = False
            error_dict = {"mesage" : "Access denied." }
            error_dict['__type'] = 'Authorization Error'
            return_dict['error'] = error_dict
            return self._finish(200, return_dict, content_type='json')

    def _get_vocabulary_list(self, context, ver):
        # FIXME: use IAuth plugin instead
        if c.userobj and c.userobj.sysadmin == True:
            return super(EDCApiController, self).action('vocabulary_list', ver)
        else :
            return_dict = {}
            return_dict['success'] = False
            error_dict = {"mesage" : "Access denied." }
            error_dict['__type'] = 'Authorization Error'
            return_dict['error'] = error_dict
            return self._finish(200, return_dict, content_type='json')


    def action(self, logic_function, ver=None):
        # FIXME: remove this method when functions called below are removed

        try:
            function = get_action(logic_function)
        except KeyError:
            return self._finish_bad_request(_('Action name not known: %s') % logic_function)

        try:
            side_effect_free = getattr(function, 'side_effect_free', False)
            request_data = self._get_request_data(try_url_params=side_effect_free)
        except ValueError, inst:
            log.error('Bad request data: %s' % inst)
            return self._finish_bad_request(_('JSON Error: %s') % inst)


        context = {'model': model, 'session': model.Session, 'user': c.user,
                   'api_version': ver, 'auth_user_obj': c.userobj}

        if logic_function == 'package_show':
            return self._package_show(context, request_data['id'])
        elif logic_function == 'package_list':
            return self._get_package_list(context, ver)
        elif logic_function == 'current_package_list_with_resources' :
            return self._get_package_list_with_resources(context, ver)
        elif logic_function == 'recently_changed_packages_activity_list' :
            return self._get_recently_changed_packages_activity_list(context, ver)
        elif logic_function == 'vocabulary_list' :
            return self._get_vocabulary_list(context, ver)
        else :
            return super(EDCApiController, self).action(logic_function, ver)
