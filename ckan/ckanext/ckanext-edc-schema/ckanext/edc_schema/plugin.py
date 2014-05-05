import ckan.model as model
from ckan.common import  c
from ckan.logic import get_action, NotFound
import ckan.lib.base as base

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from routes.mapper import SubMapper

import pylons.config as config

import pprint

from ckanext.edc_schema.util.util import (get_edc_tags, 
                                          get_edc_tag_name, 
                                          edc_format_label,
                                          get_state_values,
                                          get_username)

from ckanext.edc_schema.util.helpers import resource_preview

abort = base.abort


def is_list(value):
    return isinstance(value, list)



#----------------------------------------------------------------------------------#
#                                                                                  #
# Helper functions for extracting vocabulary tags.                                 #
# These helper functions are used in forms to get the list of tags for a specific  #
# vocabulary.                                                                      #
#                                                                                  #
#----------------------------------------------------------------------------------#
    
def get_dataset_type(id):
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}
    try:
        pkg_dict = get_action('package_show')(context, {'id': id})
        return pkg_dict['type']
    except NotFound:
        abort(404, _('The dataset {id} could not be found.').format(id=id))


def get_organizations():
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}    
    org_model = context['model']
    #Get the list of all groups of type "organization" that have no parents.             
    top_level_orgs = org_model.Group.get_top_level_groups(type="organization")
    
    return top_level_orgs

#Return the name of an organization with the given id
def get_organization_name(org_id):
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}    
    
    try:
        orgs = get_action('organization_list')(context, {'all_fields': True})
    except NotFound:
        orgs = []
    for org in orgs:

        if org['id'] == org_id:
            return org['title']
    return None

def get_organization_branches(org_id):
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}    
    org_model = context['model']
    
    #Get the list of all children of the organization with the given id             
    group = org_model.Group.get(org_id)
    branches = group.get_children_groups(type = 'organization')
    
    return branches
    

class SchemaPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    
    plugins.implements(plugins.IRoutes, inherit=True)
    
    plugins.implements(plugins.ITemplateHelpers, inherit=False)
                
    def get_helpers(self):
        return {
                "dataset_type" : get_dataset_type,
                "edc_tags" : get_edc_tags,
                "edc_tag_name" : get_edc_tag_name,
                "edc_orgs" : get_organizations,
                "edc_org_branches" : get_organization_branches,
                "edc_org_name" : get_organization_name,
                "edc_format_label" : edc_format_label,
                "edc_state_values" : get_state_values,
                "edc_username": get_username,
                "edc_preview" : resource_preview
                }
    
    
    def update_config(self, config):
        toolkit.add_public_directory(config, 'public')
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_resource('fanstatic', 'edc_resource')
        
            
    #Customizing action mapping    
    def before_map(self, map):
        
        package_controller = 'ckanext.edc_schema.controllers.package:EDCPackageController'
        user_controller = 'ckanext.edc_schema.controllers.user:EDCUserController'
        org_controller = 'ckanext.edc_schema.controllers.organization:EDCOrganizationController'
        site_map_controller = 'ckanext.edc_schema.controllers.site_map:GsaSitemapController'
        api_controller = 'ckanext.edc_schema.controllers.api:EDCApiController'
        
        map.redirect('/', '/dataset')
        map.connect('/dataset/add', controller=package_controller, action='typeSelect')
#        map.connect('home', '/', controller=package_controller, action='search')
        map.connect('/dataset/upload_file', controller=package_controller, action='upload')
        
        with SubMapper(map, controller=package_controller) as m:
            m.connect('dataset_edit', '/dataset/edit/{id}', action='edc_edit',ckan_icon='edit')
            m.connect('search', '/dataset', action='search',
                  highlight_actions='index search')
            m.connect('dataset_read', '/dataset/{id}', action='read',
                  ckan_icon='sitemap') 
#map.connect('/dataset/new', controller='ckanext.edc_schema.controllers.package:EDCPackageController', action='new')
#        map.connect('/dataset/new_resource/{id}', controller='ckanext.edc_schema.controllers.package:EDCPackageController', action='new_resource')
            
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
            m.connect('organization_read', '/organization/{id}', action='read')
            m.connect('organizations_index', '/organization', action='index')
        
        map.connect('sitemap','/sitemap.html', controller=site_map_controller, action='view')
        map.connect('sitemap','/sitemap.xml', controller=site_map_controller, action='read')
    
    # /api/util ver 1, 2 or none
        with SubMapper(map, controller=api_controller, path_prefix='/api{ver:/1|/2|}',
                   ver='/1') as m:
       
            m.connect('/i18n/{lang}', action='i18n_js_translations')    
        
        return map

    def after_map(self, map):
        return map;
    
        
