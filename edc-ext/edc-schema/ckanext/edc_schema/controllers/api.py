from ckan.controllers.api import ApiController

import os.path
import logging
import cgi
import datetime
import glob
import urllib
import pprint

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
from ckanext.edc_schema.util.util import get_all_orgs

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

#By default package_list will return only the last 10 modified records
default_limit = 10
default_offset = 0

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
    
    
    def __get_search_filter(self):
        
        user_name = c.user or 'visitor'
    
        from ckanext.edc_schema.util.util import get_user_orgs
            
        fq =  request.params.get('fq', '') 
        
        #Filter private and unpublished records for anonymous users
        if c.userobj and c.userobj.sysadmin == True:
            fq += ''
        else :
            fq += ' +(edc_state:("PUBLISHED" OR "PENDING ARCHIVE") AND metadata_visibility:("Public"))'
            if user_name != 'visitor':
                #IDIR users can also see private records of their organizations
                user_id = c.userobj.id
                #Get the list of orgs that the user is a memeber of
                user_orgs = ['"' + org.id + '"' for org in get_user_orgs(user_id)]
                if user_orgs != []:
                    fq += ' OR (' + 'owner_org:(' + ' OR '.join(user_orgs) + ') )'
        
        return fq

    
    def __package_search(self, context, ver):
        '''
        Searches for packages satisfying a given search criteria.
        '''
        from ckan.lib.search import SearchError
                        
        help_str = "Searches for packages satisfying a given search criteria.\n" + \
                    "This action accepts solr search query parameters (details below), and\n    " + \
                    "returns a dictionary of results, including dictized datasets that match\n    " + \
                    "the search criteria and a search count\n\n" +\
                    "**Solr Parameters:**\n\n    This action accepts a *subset* of solr's search query parameters:\n\n\n    " + \
                    ":param q: the solr query.  Optional.  Default: ``\"*:*\"``\n    :type q: string\n    " + \
                    ":param sort: sorting of the search results.  Optional.  Default:\n        ``'relevance asc, metadata_modified desc'``.  " + \
                    "As per the solr\n        documentation, this is a comma-separated string of field names and\n        " +\
                    "sort-orderings.\n    :type sort: string\n    " + \
                    ":param rows: the number of matching rows to return.\n    :type rows: int\n    " + \
                    ":param start: the offset in the complete result for where the set of\n        " + \
                    "returned datasets should begin.\n    :type start: int\n\n    " + \
                    "**Results:**\n\n    The result of this action is a dict with the following keys:\n\n    " + \
                    ":rtype: A dictionary with the following keys\n    " + \
                    ":param count: the number of results found.  Note, this is the total number\n        " + \
                    "of results found, not the total number of results returned (which is\n        " + \
                    "affected by limit and row parameters used in the input).\n    :type count: int\n    " + \
                    ":param results: ordered list of datasets matching the query, where the\n        " + \
                    "ordering defined by the sort parameter used in the query.\n    " + \
                    ":type results: list of dictized datasets."
            
        return_dict = {"help": help_str}
            
        #Compute the filter query depending on the user name.            
#        fq =  self.__get_search_filter() 
        
        #Get request parameters (search query, number of records to be returned and the starting package)
        q = request.params.get('q', '')
        fq =  request.params.get('fq', '') 
        
    
        try:
            limit = int(request.params.get('rows', default_limit))
        except ValueError:
            limit = default_limit
                
        try:
            offset = int(request.params.get('start', default_offset))
        except ValueError:
            offset = 0
            
        sort = request.params.get('sort', 'metadata_modified desc')
            
        try :
            data_dict = {
                         'q' : q,
                         'fq' : fq,
                         'start' : offset,
                         'rows' : limit,
                         'sort' : sort
                        }
             
            #Use package_search to filter the list
            query = get_action('package_search')(context, data_dict)
            
        except SearchError, se :
            print 'Search error', str(se)
            return self._finish_bad_request()
        
        
        response_dict = {}
        response_dict['count'] = query['count']
        response_dict['sort'] = query['sort']
        response_dict['results'] = query['results']
                
        return_dict['success'] = True
        return_dict['result'] = response_dict
        return self._finish_ok(return_dict)

        
    
    def __get_package_list(self, context, ver=None):
        '''
        Returns a list of site packages depending on the user.
        The public users could only see published public records.
        Each user can only see private records of his/her own organization
        '''
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
            
        result = []
        for pkg in query['results']:
            result.append(pkg['name'])
                
        return_dict['success'] = True
        return_dict['result'] = result
        return self._finish_ok(return_dict)


    def __get_package_list_with_resources(self, context, ver):
        '''
        Returns a list of site packages depending on the user.
        The public users could only see published public records.
        Each user can only see private records of his/her own organization
        '''
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


    def __package_show(self, context, pkg_id):
        '''
        Returns record's data with the given id only if the user is allowed to view the record.
        '''
        
        help_str = "Shows the package info with the given id. Param : id"
        
        return_dict = {"help": help_str}
        try :
            pkg = get_action('package_show')(context, {'id' : pkg_id})
            pprint.pprint('pkg:')
            pprint.pprint(pkg)
            #add the top-level org to the organization
            #'organization, branch'
            orgs = get_all_orgs()
            org=orgs[pkg['org']]
            branch=orgs[pkg['sub_org']]
            org_title = org['title']
            branch_title = branch['title']
            pkg['organization']['full_title'] = org_title + ', ' + branch_title
            pprint.pprint('org:')
            pprint.pprint(pkg['organization']['title'])
            
            from ckanext.edc_schema.util.helpers import record_is_viewable
            
            username = c.user or 'visitor'
            if not record_is_viewable(pkg, c.userobj) :
                return_dict['success'] = False
                return_dict['error'] = {'__type': 'Authorization Error', 'message': _('Access denied')}
                return self._finish(403, return_dict, content_type='json')
            return_dict['success'] = True
            return_dict['result'] = pkg
        except NotFound, e:
            return_dict['error'] = {'__type': 'Not Found Error',
                                    'message': _('Not found')}
            if e.extra_msg:
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
        

    def action(self, logic_function, ver=None):
        import ckanext.edc_schema.logic.action as edc_action
        
        #ToDo :
        #Create a list of logic_functions that need to be restricted to anonymous users
        restricted_functions = [
                                'package_list',
                                'package_show',
                                'package_search',
                                'package_autocomplete',
                                'current_package_list_with_resources'
                                ]

        #Need to apply the restriction rules to each one of the restricted functions.
        #Check if the logic function is known
        try:
            function = get_action(logic_function)
        except KeyError:
            return self._finish_bad_request(_('Action name not known: %s') % logic_function)

        try:
            side_effect_free = getattr(function, 'side_effect_free', False)
            request_data = self._get_request_data(try_url_params=
                                                  side_effect_free)            
        except ValueError, inst:
            log.error('Bad request data: %s' % inst)
            return self._finish_bad_request(
                _('JSON Error: %s') % inst)
        
                
        context = {'model': model, 'session': model.Session, 'user': c.user,
                   'api_version': ver, 'auth_user_obj': c.userobj}
   
        #Check if the logic function is package_list then return the proper list of packages
        if logic_function == 'package_show':
            return self.__package_show(context, request_data['id'])
        elif logic_function == 'package_list':
            return self.__get_package_list(context, ver)
        elif logic_function == 'current_package_list_with_resources' :
            return self.__get_package_list_with_resources(context, ver)
        elif logic_function == 'package_search':
            return self.__package_search(context, ver)
        else :
            return super(EDCApiController, self).action(logic_function, ver)
        