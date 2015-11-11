# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
import logging
from ckan.controllers.user import UserController
from ckan.common import OrderedDict,_,g, request
import ckan.lib.base as base
import ckan.model as model
import ckan.logic as logic
import ckan.lib.helpers as h
from urllib import urlencode
from ckan.logic import get_action
import ckan.lib.maintain as maintain
import ckan.plugins.toolkit as toolkit

from ckanext.bcgov.util.util import (get_user_orgs, get_user_toporgs)

c = toolkit.c

render = base.render
abort = base.abort
redirect = base.redirect

check_access = logic.check_access
NotAuthorized = logic.NotAuthorized
render = base.render

log = logging.getLogger('ckanext.edc_schema')


def _encode_params(params):
    return [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
            for k, v in params]


class EDCUserController(UserController):
            
    def dashboard_unpublished(self):
        
        user_id = c.userobj.id
        fq = ' +edc_state:("DRAFT" OR "PENDING PUBLISH" OR "REJECTED")'
            #Get the list of organizations that this user is the admin
        if not c.userobj.sysadmin :            
            user_orgs = ['"' + org.id + '"' for org in get_user_orgs(user_id, 'admin')]
            user_orgs += ['"' + org.id + '"' for org in get_user_orgs(user_id, 'editor')]  
            if len(user_orgs) > 0 :      
                fq += ' +owner_org:(' + ' OR '.join(user_orgs) + ')'
        self._user_datasets('dashboard_unpublished', c.userobj.id, fq)
        return render('user/dashboard_unpublished.html')
    
    def dashboard_datasets(self):
        fq = ' +author:("%s")' % (c.userobj.id)
        self._user_datasets('dashboard_datasets', c.userobj.id, fq)
        return render('user/dashboard_datasets.html')
    
    def read(self, id=None):
        if c.userobj and c.userobj.sysadmin == True:
            fq = ''
        else:
            fq = ' +(edc_state:("PUBLISHED" OR "PENDING ARCHIVE")'
            if c.userobj:
                user_id = c.userobj.id
                user_orgs = ['"' + org.id + '"' for org in get_user_orgs(user_id, 'admin')]
                user_orgs += ['"' + org.id + '"' for org in get_user_orgs(user_id, 'editor')]
                if len(user_orgs) > 0:
                    fq += ' OR owner_org:(' + ' OR '.join(user_orgs) + ')'
            fq += ')'
        self._user_datasets('read',id, fq)
        return render('user/read.html')
 
    def _user_datasets(self, action, id=None, filter_query=None):
        from ckan.lib.search import SearchError
                 
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        user_dict = {'id': id,
                     'user_obj': c.userobj}

        # unicode format (decoded from utf8)
        q = c.q = request.params.get('q', u'')
#        q += ' author:"%s"' %c.userobj.id
        
        context['return_query'] = True
        
        try:
            page = int(request.params.get('page', 1))
        except ValueError, e:
            abort(400, ('"page" parameter must be an integer'))

        limit = g.datasets_per_page

        # most search operations should reset the page counter:
        params_nopage = [(k, v) for k, v in request.params.items()
                         if k != 'page']

        sort_by = request.params.get('sort', None)
        
        def search_url(params):
            if action == 'read':
                url = h.url_for(controller='user', action=action, id=id)
            else:
                url = h.url_for(controller='user', action=action)                

            params = [(k, v.encode('utf-8') if isinstance(v, basestring)
                       else str(v)) for k, v in params]
            return url + u'?' + urlencode(params)
        
        def drill_down_url(alternative_url=None, **by):
            return h.add_url_param(alternative_url=alternative_url,
                                   controller='user', action=action,
                                   extras=dict(id=c.userobj.id),
                                   new_params=by)

        c.drill_down_url = drill_down_url

        def remove_field(key, value=None, replace=None):
            return h.remove_url_param(key, value=value, replace=replace,
                                      controller='user', action=action,
                                      extras=dict(id=c.userobj.id))

        c.remove_field = remove_field

        def pager_url(q=None, page=None):
            params = list(params_nopage)
            params.append(('page', page))
            return search_url(params)

        try:
            c.fields = []
            search_extras = {}
            for (param, value) in request.params.items():
                if param not in ['q', 'page', 'sort'] \
                        and len(value) and not param.startswith('_'):
                    if not param.startswith('ext_'):
                        c.fields.append((param, value))
                        q += ' %s:"%s"' % (param, value)
                    else:
                        search_extras[param] = value

            facets = OrderedDict()

            default_facet_titles = {
                    'organization': _('Organizations'),
                    'edc_state': _('States'),
                    'tags': _('Tags'),
                    'res_format': _('Formats'),
                    }

            for facet in default_facet_titles:
                facets[facet] = default_facet_titles[facet]


            c.facet_titles = facets
            
            fq = filter_query or '' 
            
            
            data_dict = {
                'q': q,
                'fq': fq.strip(),
                'facet.field': facets.keys(),
                'rows': limit,
                'start': (page - 1) * limit,
                'sort': sort_by,
                'extras': search_extras
            }
            
            query = get_action('package_search')(context, data_dict)
            
            c.page = h.Page(
                collection=query['results'],
                page=page,
                url=pager_url,
                item_count=query['count'],
                items_per_page=limit
            )
            user_dict['package_count'] = query['count']
            c.facets = query['facets']
            maintain.deprecate_context_item('facets',
                                            'Use `c.search_facets` instead.')
                                            
            c.search_facets = query['search_facets']
            c.search_facets_limits = {}
            for facet in c.facets.keys():
                limit = int(request.params.get('_%s_limit' % facet,
                                                g.facets_default_number))
                c.search_facets_limits[facet] = limit
            c.page.items = query['results']
                                            
            c.sort_by_selected = sort_by
                        
        except SearchError, se:
            log.error('User search error: %r', se.args)
            c.query_error = True
            c.facets = {}
            c.page = h.Page(collection=[])

        self._setup_template_variables(context, user_dict)
        

    def dashboard_organizations(self):
        context = {'model': model, 'session': model.Session,
                   'for_view': True, 'user': c.user or c.author,
                   'auth_user_obj': c.userobj}
        
        data_dict = {'user_obj': c.userobj}
        self._setup_template_variables(context, data_dict)
        (user_orgs, usr_suborgs) = get_user_toporgs(c.userobj.id) 
        
        facets = OrderedDict()

        #Add the organization facet to get the number of records for each organization
        facets['organization'] = _('Organizations')

        data_dict = {
                'facet.field': facets.keys(),
        }

        query = get_action('package_search')(context, data_dict)
        c.org_pkg_count = query['facets'].get('organization')
        c.top_orgs_items = user_orgs
        c.suborgs_items = usr_suborgs
        
               
        return render('user/dashboard_organizations.html')
