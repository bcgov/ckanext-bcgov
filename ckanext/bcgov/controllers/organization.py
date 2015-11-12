# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
from ckan.controllers.organization import OrganizationController
from ckan.common import OrderedDict, c, g, request, _
import ckan.lib.base as base
import logging

from urllib import urlencode
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.lib.search as search
import ckan.model as model
import ckan.lib.maintain as maintain

from ckanext.bcgov.util.helpers import get_suborgs

render = base.render
abort = base.abort

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
log = logging.getLogger('ckanext.edc_schema')

class EDCOrganizationController(OrganizationController):
    
    def index(self):
        # FIXME: index copied from GroupController and modified to
        # show only parent groups
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'with_private': False}

        data_dict = {'all_fields': False}
        try:
            self._check_access('site_read', context)
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

        # pass user info to context as needed to view private datasets of
        # orgs correctly
        if c.userobj:
            context['user_id'] = c.userobj.id
            context['user_is_admin'] = c.userobj.sysadmin

        search_result = self._action('organization_list')(context, data_dict)
        
        org_model = context['model']
        
        #Get the list of all groups of type "organization" that have no parents.             
        top_level_orgs = org_model.Group.get_top_level_groups(type="organization")
        top_results = [org for org in top_level_orgs if org.name in search_result ]
        
        facets = OrderedDict()

        facets['organization'] = _('Organizations')

        data_dict = {
                'facet.field': facets.keys(),
        }

        query = get_action('package_search')(context, data_dict)
        c.org_pkg_count = query['facets'].get('organization')
        
        c.top_orgs_items = top_results
        return render('organization/index.html')
        
    def _read(self, id, limit):
        # FIXME: copied and modified from GroupController to collect
        # sub organizations, create c.fields_grouped and hard-code
        # search facets
        ''' This is common code used by both read and bulk_process'''
        
        group_type = self._get_group_type(id.split('@')[0])
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'schema': self._db_to_form_schema(group_type=group_type),
                   'for_view': True, 'extras_as_string': True}

        # Get the subgorgs of this org
        org_id = c.group_dict.get('id')
        
        q = c.q = request.params.get('q', '')

        # XXX: unfortunate hack, copy sort default behaviour from
        # before_search because we're using the q parameter below
        # even when no text query was submitted
        if not q and request.params.get('sort') in (None, 'rank'):
            sort_by = 'record_publish_date desc, metadata_modified desc'
        else:
            sort_by = request.params.get('sort', None)


        suborgs = ['"' + org + '"' for org in get_suborgs(org_id)]
        if suborgs != []:
            q += ' owner_org:("' + org_id + '" OR ' + ' OR '.join(suborgs) + ')'
        else :
            q += ' owner_org:"%s"' % org_id
        
        c.description_formatted = h.render_markdown(c.group_dict.get('description'))

        context['return_query'] = True

        try:
            page = int(request.params.get('page', 1))
        except ValueError, e:
            abort(400, ('"page" parameter must be an integer'))

        # most search operations should reset the page counter:
        params_nopage = [(k, v) for k, v in request.params.items()
                         if k != 'page']

        def search_url(params):
            if group_type == 'organization':
                if c.action == 'bulk_process':
                    url = self._url_for(controller='organization',
                                        action='bulk_process',
                                        id=id)
                else:
                    url = self._url_for(controller='organization',
                                        action='read',
                                        id=id)
            else:
                url = self._url_for(controller='organization', action='read', id=id)
            params = [(k, v.encode('utf-8') if isinstance(v, basestring)
                       else str(v)) for k, v in params]
            return url + u'?' + urlencode(params)

        def drill_down_url(**by):
            return h.add_url_param(alternative_url=None,
                                   controller='organization', action='read',
                                   extras=dict(id=c.group_dict.get('name')),
                                   new_params=by)

        c.drill_down_url = drill_down_url

        def remove_field(key, value=None, replace=None):
            return h.remove_url_param(key, value=value, replace=replace,
                                      controller='organization', action='read',
                                      extras=dict(id=c.group_dict.get('name')))

        c.remove_field = remove_field

        def pager_url(q=None, page=None):
            params = list(params_nopage)
            params.append(('page', page))
            return search_url(params)

        try:
            c.fields = []
            search_extras = {}
            c.fields_grouped = {}
            for (param, value) in request.params.items():
                if not param in ['q', 'page', 'sort'] \
                        and len(value) and not param.startswith('_'):
                    if not param.startswith('ext_'):
                        c.fields.append((param, value))
                        q += ' %s: "%s"' % (param, value)
                        if param not in c.fields_grouped:
                            c.fields_grouped[param] = [value]
                        else:
                            c.fields_grouped[param].append(value)
                    else:
                        search_extras[param] = value

            fq = 'capacity:"public"'
            user_member_of_orgs = [org['id'] for org
                                   in h.organizations_available('read')]

            if (c.group and c.group.id in user_member_of_orgs):
                fq = ''
                context['ignore_capacity_check'] = True

            facets = OrderedDict()

            default_facet_titles = {'organization': _('Organizations'),
                                    'edc_state': _('States'),
                                    'tags': _('Tags'),
                                    'res_format': _('Formats'),
                                    'license_id': _('Licenses'),
                                    'type' : _('Dataset types')
                                    }


            for facet in default_facet_titles:
                facets[facet] = default_facet_titles[facet]

            c.facet_titles = facets

            data_dict = {
                'q': q,
                'fq': fq,
                'facet.field': facets.keys(),
                'rows': limit,
                'sort': sort_by,
                'start': (page - 1) * limit,
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

            c.group_dict['package_count'] = query['count']
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

        except search.SearchError, se:
            log.error('Group search error: %r', se.args)
            c.query_error = True
            c.facets = {}
            c.page = h.Page(collection=[])

        self._setup_template_variables(context, {'id':id},
            group_type=group_type)


    def member_new(self, id):
        # FIXME: heavily customized version of GroupController.member_new
        # that is tied to our particular auth mechanism and permissions
        # This would be better in the idir extension
        import ckan.lib.navl.dictization_functions as dict_fns
        import ckan.new_authz as new_authz
        
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}

        errors = {}
        try:
            group_type = 'organization'
            c.roles = self._action('member_roles_list')(context, {'group_type': group_type})
            if request.method == 'POST':
                data_dict = clean_dict(dict_fns.unflatten(
                    tuplize_dict(parse_params(request.params))))
                data_dict['id'] = id
                
                idir_account = data_dict.get('idir')
                if idir_account:
                    
                    '''
                    Check if the account has only alphanumeric characters
                    '''
                    import re

                    name_match = re.compile('[a-z0-9_\-]*$')
                    if not name_match.match(idir_account) :
                        c.group_dict = self._action('organization_show')(context, {'id' : data_dict['id']})
                        errors['idir'] = _('must be purely lower case alphanumeric (ascii) characters and these symbols: -_')
                        
                        vars = {'data': data_dict, 'errors': errors}
                        return render('organization/member_new.html', extra_vars=vars)
                    
                    try:
                        user_dict = get_action('user_show')(context, {'id': idir_account.lower(), 'include_datasets': False})
                    except NotFound:
                        user_dict = {}
                    
                    if not user_dict :
                        user_data_dict = {
                                          'name': idir_account.lower(),
                                          'email': 'data@gov.bc.ca',
                                          'password' : 't35tu53r'
                        }
                        del data_dict['idir']
                        
                        user_dict = self._action('user_create')(context,
                            user_data_dict)
                     
                    data_dict['username'] = user_dict['name']
                    data_dict['role'] = data_dict.get('role', 'editor')
 
                c.group_dict = self._action('group_member_create')(context, data_dict)
                self._redirect_to(controller='group', action='members', id=id)
            else:
                user = request.params.get('user')
                if user:
                    c.user_dict = get_action('user_show')(context, {'id': user})
                    c.user_role = new_authz.users_role_for_group_or_org(id, user) or 'member'
                else:
                    c.user_role = 'member'
                c.group_dict = self._action('group_show')(context, {'id': id})
        except NotAuthorized:
            abort(401, _('Unauthorized to add member to group %s') % '')
        except NotFound:
            abort(404, _('Group not found'))
        except ValidationError, e:
            h.flash_error(e.error_summary)
        return render('organization/member_new.html', extra_vars={'errors': errors})


    def about(self, id):
        c.group_dict = self._get_group_dict(id)
        group_type = c.group_dict['type']
         
 
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'with_private': False}
 
        if c.userobj:
            context['user_id'] = c.userobj.id
            context['user_is_admin'] = c.userobj.sysadmin
 
        #Search_result list contains all orgs matched with search criteria including orgs and suborgs.
        data_dict = {'all_fields': True}
        search_result = self._action('organization_list')(context, data_dict)
         
        org_pkg_count_dict = {}
        for org in search_result :
            org_pkg_count_dict[org['id']] = org['packages']
             
        c.org_pkg_count = org_pkg_count_dict
         
        c.group_dict['package_count'] = len(c.group_dict.get('packages', []))
        self._setup_template_variables(context, {'id': id},
                                       group_type=group_type)
        return render(self._about_template(group_type))
