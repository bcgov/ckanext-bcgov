# Copyright  2015, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license

from ckan.common import  c, _

import pylons.config as config
import ckan.lib.base as base
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from routes.mapper import SubMapper

from ckanext.bcgov.util.util import (get_edc_tags,
                                          edc_type_label,
                                          get_state_values,
                                          get_username,
                                          get_user_orgs,
                                          get_orgs_user_can_edit,
                                          get_user_orgs_id,
                                          get_user_toporgs,
                                          get_organization_branches
                                          )

from ckanext.bcgov.util.helpers import (get_suborg_sector,
                                             get_user_dataset_num,
                                             get_package_data,
                                             is_license_open,
                                             get_record_type_label,
                                             get_suborgs,
                                             record_is_viewable,
                                             get_facets_selected,
                                             get_facets_unselected,
                                             get_sectors_list,
                                             get_dataset_type,
                                             get_organizations,
                                             get_organization_title,
                                             get_espg_id,
                                             get_edc_org,
                                             get_iso_topic_values,
                                             get_eas_login_url,
                                             get_fqdn,
                                             get_environment_name,
                                             get_version,
                                             get_bcgov_commit_id,
                                             resource_prefix,
                                             get_org_parent,
                                             size_or_link,
                                             remove_user_link,
                                             get_ofi_config,
                                             get_ofi_resources
                                             )

abort = base.abort


class SchemaPlugin(plugins.SingletonPlugin):

    plugins.implements(plugins.IConfigurer)

    plugins.implements(plugins.IRoutes, inherit=True)

    plugins.implements(plugins.ITemplateHelpers, inherit=False)

    plugins.implements(plugins.IPackageController, inherit=True)

    plugins.implements(plugins.IFacets, inherit=True)

    plugins.implements(plugins.IActions, inherit=True)

    plugins.implements(plugins.IAuthFunctions)

    def get_helpers(self):
        return {
                "dataset_type" : get_dataset_type,
                "edc_tags" : get_edc_tags,
                "edc_orgs" : get_organizations,
                "edc_org_branches" : get_organization_branches,
                "edc_org_title" : get_organization_title,
                "edc_type_label" : edc_type_label,
                "edc_state_values" : get_state_values,
                "edc_username": get_username,
                "get_sector" : get_suborg_sector,
                "get_user_orgs" : get_user_orgs,
                "get_user_orgs_id" : get_user_orgs_id,
                "get_user_toporgs": get_user_toporgs,
                "get_suborg_sector" : get_suborg_sector,
                "get_user_dataset_num" : get_user_dataset_num,
                "get_edc_package" : get_package_data,
                "is_license_open" : is_license_open,
                "record_type_label" : get_record_type_label,
                "get_suborgs": get_suborgs,
                "record_is_viewable": record_is_viewable,
                "get_espg_id" : get_espg_id,
                "orgs_user_can_edit" : get_orgs_user_can_edit,
                "get_facets_selected": get_facets_selected,
                "get_facets_unselected" : get_facets_unselected,
                "get_sectors_list": get_sectors_list,
                "get_edc_org" : get_edc_org,
                "get_iso_topic_values" : get_iso_topic_values,
                "get_eas_login_url": get_eas_login_url,
                "get_fqdn": get_fqdn,
                "get_environment_name": get_environment_name,
                "get_version": get_version,
                "get_bcgov_commit_id": get_bcgov_commit_id,
                "googleanalytics_resource_prefix": resource_prefix,
                "get_parent_org": get_org_parent,
                "size_or_link": size_or_link,
                "remove_user_link": remove_user_link,
                "get_ofi_config": get_ofi_config,
                "get_ofi_resources": get_ofi_resources
                }

    def update_config(self, config):
        toolkit.add_public_directory(config, 'public')
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_resource('fanstatic', 'edc_resource')
        toolkit.add_resource('public/scripts', 'theme_scripts')

    #Customizing action mapping
    def before_map(self, map):
        from routes.mapper import SubMapper

        package_controller = 'ckanext.bcgov.controllers.package:EDCPackageController'
        user_controller = 'ckanext.bcgov.controllers.user:EDCUserController'
        org_controller = 'ckanext.bcgov.controllers.organization:EDCOrganizationController'
        site_map_controller = 'ckanext.bcgov.controllers.site_map:GsaSitemapController'
        api_controller = 'ckanext.bcgov.controllers.api:EDCApiController'
        ofi_controller = 'ckanext.bcgov.controllers.ofi:EDCOfiController'

        GET_POST = dict(method=['GET', 'POST'])

        map.connect('package_index', '/', controller=package_controller, action='index')

        with SubMapper(map, controller=package_controller) as m:
            m.connect('/dataset/add', action='typeSelect')
            m.connect('add dataset', '/dataset/new', action='new')
            m.connect('add dataset type', '/{dataset_type}/new', action='new')
            m.connect('search', '/dataset', action='search', highlight_actions='index search')
            m.connect('dataset_read', '/dataset/{id}', action='read', ckan_icon='sitemap')
            m.connect('dataset type read', '/{dataset_type}/{id}', action='read', ckan_icon='sitemap')
            m.connect('duplicate', '/dataset/duplicate/{id}/{package_type}', action='duplicate')
            m.connect('/dataset/{id}/resource/{resource_id}', action='resource_read')
            m.connect('/dataset/{id}/resource_delete/{resource_id}', action='resource_delete')
            m.connect('/authorization-error', action='auth_error')
            m.connect('resource_edit', '/dataset/{id}/resource_edit/{resource_id}', action='resource_edit', ckan_icon='edit')
            m.connect('new_resource', '/dataset/new_resource/{id}', action='new_resource')
            m.connect('resources', '/dataset/resources/{id}', action='resources')

        with SubMapper(map, controller=user_controller) as m:
            m.connect('user_dashboard_unpublished', '/dashboard/unpublished',
                  action='dashboard_unpublished', ckan_icon='group')
            m.connect('/user/edit', action='edit')
            m.connect('/user/activity/{id}/{offset}', action='activity')
            m.connect('user_activity_stream', '/user/activity/{id}',
                  action='activity', ckan_icon='time')
            m.connect('user_dashboard', '/dashboard', action='dashboard',
                  ckan_icon='list')
            m.connect('user_dashboard_datasets', '/dashboard/datasets',
                  action='dashboard_datasets', ckan_icon='sitemap')
            m.connect('user_dashboard_organizations', '/dashboard/organizations',
                  action='dashboard_organizations', ckan_icon='building')
            m.connect('/dashboard/{offset}', action='dashboard')
            m.connect('user_follow', '/user/follow/{id}', action='follow')
            m.connect('/user/unfollow/{id}', action='unfollow')
            m.connect('user_followers', '/user/followers/{id:.*}',
                  action='followers', ckan_icon='group')
            m.connect('user_edit', '/user/edit/{id:.*}', action='edit',
                  ckan_icon='cog')
            m.connect('user_delete', '/user/delete/{id}', action='delete')
            m.connect('/user/reset/{id:.*}', action='perform_reset')
            m.connect('register', '/user/register', action='register')
            m.connect('login', '/user/login', action='login')
            m.connect('/user/_logout', action='logout')
            m.connect('/user/logged_in', action='logged_in')
            m.connect('/user/logged_out', action='logged_out')
            m.connect('/user/logged_out_redirect', action='logged_out_page')
            m.connect('/user/reset', action='request_reset')
            m.connect('/user/me', action='me')
            m.connect('/user/set_lang/{lang}', action='set_lang')
            m.connect('user_datasets', '/user/{id:.*}', action='read',
                  ckan_icon='sitemap')
            m.connect('user_index', '/user', action='index')

        with SubMapper(map, controller=org_controller) as m:
            m.connect('organizations_index', '/organization', action='index')
            m.connect('/organization/list', action='list')
            m.connect('/organization/new', action='new')
            m.connect('/organization/{action}/{id}',
                  requirements=dict(action='|'.join([
                      'delete',
                      'admins',
                      'member_new',
                      'member_delete',
                      'history'
                  ])))
            m.connect('organization_activity', '/organization/activity/{id}',
                   action='activity', ckan_icon='time')
            m.connect('organization_about', '/organization/about/{id}',
                  action='about', ckan_icon='info-sign')
            m.connect('organization_edit', '/organization/edit/{id}',
                   action='edit', ckan_icon='edit')
            m.connect('organization_members', '/organization/members/{id}',
                   action='members', ckan_icon='group')
            m.connect('organization_bulk_process',
                   '/organization/bulk_process/{id}',
                   action='bulk_process', ckan_icon='sitemap')
            m.connect('organization_read', '/organization/{id}',
                   action='read', ckan_icon='sitemap')

        map.connect('sitemap','/sitemap.html', controller=site_map_controller, action='view')
        map.connect('sitemap','/sitemap.xml', controller=site_map_controller, action='read')

        with SubMapper(map, controller=api_controller, path_prefix='/api{ver:/1|/2|/3|}',
          ver='/1') as m:
            m.connect('/i18n/{lang}', action='i18n_js_translations')
            m.connect('/')

        map.connect('ofi api', '/api/ofi/{call_action}', controller=ofi_controller, action='action', conditions=GET_POST)
        map.connect('ofi resource', '/api/ofi/{format}/{object_name}', action='action')

        m.connect('/action/organization_list_related', action='organization_list_related', conditions=GET_POST)
        m.connect('/action/{logic_function}', action='action', conditions=GET_POST)

        map.connect('/admin/trash', controller='admin', action='trash')
        map.connect('ckanadmin_trash', '/admin/trash', controller='admin',
                action='trash', ckan_icon='trash')

        return map

    def after_map(self, map):
        return map

    def before_index(self, pkg_dict):
        '''
        Makes the sort by name case insensitive.
        Note that the search index must be rebuild for the first time in order for the changes to take affect.
        '''
        title = pkg_dict['title']
        if title:
            #Assign title to title_string with all characters switched to lower case.
            pkg_dict['title_string'] = title.lower()

        res_format = pkg_dict.get('res_format', [])
        if 'other' in res_format:
            # custom download (other) supports a number of formats
            res_format.remove('other')
            res_format.extend(['shp', 'fgdb', 'e00'])

        return pkg_dict

    def before_search(self, search_params):
        '''
        Customizes package search and applies filters based on the dataset metadata-visibility
        and user roles.
        '''

        #Change the default sort order when no query passed
        if not search_params.get('q') and search_params.get('sort') in (None, 'rank'):
            search_params['sort'] = 'record_publish_date desc, metadata_modified desc'


        #Change the query filter depending on the user

        if 'fq' in search_params:
            fq = search_params['fq']
        else:
            fq = ''

        #need to append solr param q.op to force an AND query
        if 'q' in search_params:
            q = search_params['q']
            if q !='':
                q = '{!lucene q.op=AND}' + q
                search_params['q'] = q
        else:
            q = ''

        try :
            user_name = c.user or 'visitor'

            #  There are no restrictions for sysadmin
            if c.userobj and c.userobj.sysadmin == True:
                fq += ' '
            else:
                if user_name != 'visitor':
                    if 'edc_state' not in fq :
                        fq += ' +(edc_state:("PUBLISHED" OR "PENDING ARCHIVE")'

                        if 'owner_org' not in fq :
                            #IDIR users can also see private records of their organizations
                            user_id = c.userobj.id
                            #Get the list of orgs that the user is an admin or editor of
                            user_orgs = get_orgs_user_can_edit(c.userobj) #['"' + org + '"' for org in get_orgs_user_can_edit()]
                            #user_orgs = ['"' + org.get('id') + '"' for org in get_user_orgs(user_id, 'admin')]
                            #user_orgs += ['"' + org.get('id') + '"' for org in get_user_orgs(user_id, 'editor')]
                            if user_orgs != []:
                                fq += ' OR ' + 'owner_org:(' + ' OR '.join(user_orgs) + ')'

                        fq += ')'
                #Public user can only view public and published records
                else:
                    fq += ' +(edc_state:("PUBLISHED" OR "PENDING ARCHIVE") AND metadata_visibility:("Public"))'

        except Exception:
            if 'fq' in search_params:
                fq = search_params['fq']
            else:
                fq = ''
            fq += ' +edc_state:("PUBLISHED" OR "PENDING ARCHIVE") +metadata_visibility:("Public")'

        search_params['fq'] = fq

        return search_params

    def before_view(self, pkg_dict):
        # CITZEDC808
        if not record_is_viewable(pkg_dict, c.userobj):
            abort(401, _('Unauthorized to read package %s') % pkg_dict.get("title"))

        return pkg_dict

    #def after_update(self, context, pkg_dict):
        # If there are no resources added, redirect to the "add resource" page after saving
        #if len(pkg_dict.get('resources', [])) == 0:
        #    toolkit.redirect_to(controller='package', action='new_resource', id=pkg_dict['id'])

    def dataset_facets(self, facet_dict, package_type):
        '''
        Customizes search facet list.
        '''

        from collections import OrderedDict
        facet_dict = OrderedDict()
        #Add dataset types and organization sectors to the facet list
        facet_dict['license_id'] = _('License')
        facet_dict['sector'] = _('Sectors')
        facet_dict['type'] = _('Dataset types')
        facet_dict['res_format'] = _('Format')
        facet_dict['organization'] = _('Organizations')
        facet_dict['download_audience'] = _('Download permission')

        if c.userobj and c.userobj.sysadmin:
            facet_dict['edc_state'] = _('States')

        return facet_dict

    def group_facets(self, facet_dict, group_type, package_type):
        '''
        Use the same facets for filtering datasets within group pages
        '''
        return self.dataset_facets(facet_dict, package_type)

    def get_actions(self):
        import ckanext.bcgov.logic.action as edc_action
        from ckanext.bcgov.logic.ofi import call_action as ofi
        return {
            'edc_package_update': edc_action.edc_package_update,
            'edc_package_update_bcgw': edc_action.edc_package_update_bcgw,
            'package_update': edc_action.package_update,
            'package_autocomplete': edc_action.package_autocomplete,
            'check_object_name': ofi.check_object_name,
            'file_formats': ofi.file_formats,
            'crs_types': ofi.crs_types,
            'populate_dataset_with_ofi': ofi.populate_dataset_with_ofi,
            'geo_resource_form': ofi.geo_resource_form,
            'remove_ofi_resources': ofi.remove_ofi_resources,
            'edit_ofi_resources': ofi.edit_ofi_resources,
            'get_max_aoi': ofi.get_max_aoi,
            'ofi_create_order': ofi.ofi_create_order
        }

    def get_auth_functions(self):
        from ckanext.bcgov.logic.auth import create as edc_auth_create
        from ckanext.bcgov.logic.auth.ofi import call_action as ofi
        return {
            'package_create': edc_auth_create.package_create,
            'check_object_name': ofi.check_object_name,
            'file_formats': ofi.file_formats,
            'crs_types': ofi.crs_types,
            'populate_dataset_with_ofi': ofi.populate_dataset_with_ofi,
            'geo_resource_form': ofi.geo_resource_form,
            'remove_ofi_resources': ofi.remove_ofi_resources,
            'edit_ofi_resources': ofi.edit_ofi_resources,
            'get_max_aoi': ofi.get_max_aoi,
            'ofi_create_order': ofi.ofi_create_order
        }


class EDCDisqusPlugin(plugins.SingletonPlugin):
    # Declare that this class implements IConfigurer.
    plugins.implements(plugins.IConfigurer)

    # Declare that this plugin will implement ITemplateHelpers.
    plugins.implements(plugins.ITemplateHelpers)

    plugins.implements(plugins.IRoutes, inherit=True)

    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        # 'templates' is the path to the templates dir, relative to this
        # plugin.py file.
        toolkit.add_template_directory(config, 'templates')


        # Add this plugin's public dir to CKAN's extra_public_paths, so
        # that CKAN will use this plugin's custom static files.
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('fanstatic', 'edc_resource')

    def before_map(self, map):

        disqus_controller = 'ckanext.bcgov.controllers.disqus:DisqusController'

        with SubMapper(map, controller=disqus_controller) as m:
            m.connect('/disqus/posts/create', action='disqusPostCreate')

        with SubMapper(map, controller=disqus_controller) as m:
            m.connect('/disqus/threads/get', action='disqusGetThread')

        with SubMapper(map, controller=disqus_controller) as m:
            m.connect('/disqus/posts/list', action='disqusGetPostsByThread')

        return map

    def comments_block(self):
        ''' Adds Disqus Comments to the page.'''
        # we need to create an identifier
        c = plugins.toolkit.c
        identifier = ''
        try:
            if c.current_package_id:
                identifier = c.current_package_id
            elif c.id:
                identifier = c.id
            else:
                # cannot make an identifier
                identifier = ''
        except:
            identifier = ''

        data = {'identifier' : identifier, 'site_url': config.get('ckan.site_url') }
        return plugins.toolkit.render_snippet('package/comments_block.html', data)

    def disqus_get_forum_name(self):
        return config.get('edcdisqus.forum_name') or 'bccatalogue'

    def get_helpers(self):
        return { 'comments_block' : self.comments_block, 'disqus_get_forum_name': self.disqus_get_forum_name }
