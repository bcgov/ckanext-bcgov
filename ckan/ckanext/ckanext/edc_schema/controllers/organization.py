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

import pprint

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
log = logging.getLogger(__name__)

class EDCOrganizationController(OrganizationController):
    
    def index(self):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'with_private': False}

        q = c.q = request.params.get('q', '')
        data_dict = {'all_fields': True, 'q': q}
        sort_by = c.sort_by_selected = request.params.get('sort')
        if sort_by:
            data_dict['sort'] = sort_by
        try:
            self._check_access('site_read', context)
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

        # pass user info to context as needed to view private datasets of
        # orgs correctly
        if c.userobj:
            context['user_id'] = c.userobj.id
            context['user_is_admin'] = c.userobj.sysadmin

        all_orgs = self._action('organization_list')(context, data_dict)
        org_model = context['model']
        #Get the list of all groups of type "organization" that have no parents.             
        top_level_orgs = [org.id for org in org_model.Group.get_top_level_groups(type="organization")]
                
        results = [org for org in all_orgs if org['id'] in top_level_orgs]    

        c.page = h.Page(
            collection=results,
            page=request.params.get('page', 1),
            url=h.pager_url,
            items_per_page=21
        )
        return render('organization/index.html')
        
    def _read(self, id, limit):
        ''' This is common code used by both read and bulk_process'''
        group_type = self._get_group_type(id.split('@')[0])
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'schema': self._db_to_form_schema(group_type=group_type),
                   'for_view': True, 'extras_as_string': True}

        q = c.q = request.params.get('q', '')
        q += ' owner_org:"%s"' % c.group_dict.get('id')

        c.description_formatted = h.render_markdown(c.group_dict.get('description'))

        context['return_query'] = True

        try:
            page = int(request.params.get('page', 1))
        except ValueError, e:
            abort(400, ('"page" parameter must be an integer'))

        # most search operations should reset the page counter:
        params_nopage = [(k, v) for k, v in request.params.items()
                         if k != 'page']
        #sort_by = request.params.get('sort', 'name asc')
        sort_by = request.params.get('sort', None)
        
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
                url = self._url_for(controller='group', action='read', id=id)
            params = [(k, v.encode('utf-8') if isinstance(v, basestring)
                       else str(v)) for k, v in params]
            return url + u'?' + urlencode(params)

        def drill_down_url(**by):
            return h.add_url_param(alternative_url=None,
                                   controller='group', action='read',
                                   extras=dict(id=c.group_dict.get('name')),
                                   new_params=by)

        c.drill_down_url = drill_down_url

        def remove_field(key, value=None, replace=None):
            return h.remove_url_param(key, value=value, replace=replace,
                                      controller='group', action='read',
                                      extras=dict(id=c.group_dict.get('name')))

        c.remove_field = remove_field

        def pager_url(q=None, page=None):
            params = list(params_nopage)
            params.append(('page', page))
            return search_url(params)

        try:
            c.fields = []
            search_extras = {}
            for (param, value) in request.params.items():
                if not param in ['q', 'page', 'sort'] \
                        and len(value) and not param.startswith('_'):
                    if not param.startswith('ext_'):
                        c.fields.append((param, value))
                        q += ' %s: "%s"' % (param, value)
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
                                    'res_format': _('Formats')
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
