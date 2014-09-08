import pprint
import ckan.model as model
from ckan.common import  c, _
from ckan.logic import get_action, NotFound
import ckan.lib.base as base
import re

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from routes.mapper import SubMapper
from collections import OrderedDict


from ckanext.edc_schema.util.util import (get_edc_tags,
                                          edc_type_label,
                                          get_state_values,
                                          get_username,
                                          get_user_orgs,
                                          get_user_role_orgs,
                                          get_user_orgs_id,
                                          get_user_toporgs,
                                          check_user_member_of_org,
                                          get_organization_branches,
                                          get_all_orgs
                                          )

from ckanext.edc_schema.util.helpers import (get_suborg_sectors,
                                             get_user_dataset_num,
                                             get_package_data,
                                             is_license_open,
                                             get_record_type_label,
                                             get_suborgs,
                                             edc_linked_gravatar,
                                             edc_gravatar,
                                             record_is_viewable
                                             )

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

def get_user_id():

    return c.userobj.id

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
            return org['name']
    return None

#Return the title of an organization with the given id
def get_organization_title(org_id):
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

def get_espg_id(espg_string):
  a = re.compile("_([0-9]+)")
  espg_id = a.findall(espg_string)
  return espg_id[0]

class SchemaPlugin(plugins.SingletonPlugin):

#    plugins.implements(plugins.IAuthFunctions)

    plugins.implements(plugins.IConfigurer)

    plugins.implements(plugins.IRoutes, inherit=True)

    plugins.implements(plugins.ITemplateHelpers, inherit=False)

    plugins.implements(plugins.IPackageController, inherit=True)

    plugins.implements(plugins.IFacets, inherit=True)

    plugins.implements(plugins.IActions, inherit=True)


    def get_helpers(self):
        return {
                "dataset_type" : get_dataset_type,
                "user_id" : get_user_id,
                "edc_tags" : get_edc_tags,
                "edc_orgs" : get_organizations,
                "edc_org_branches" : get_organization_branches,
                "edc_org_title" : get_organization_title,
                "edc_org_name" : get_organization_name,
                "edc_type_label" : edc_type_label,
                "edc_state_values" : get_state_values,
                "edc_username": get_username,
                "get_sector" : get_suborg_sectors,
                "get_user_orgs" : get_user_orgs,
                "get_user_orgs_id" : get_user_orgs_id,
                "get_user_toporgs": get_user_toporgs,
                "check_user_member_of_org" : check_user_member_of_org,
                "get_suborg_sectors" : get_suborg_sectors,
                "get_user_dataset_num" : get_user_dataset_num,
                "get_edc_package" : get_package_data,
                "is_license_open" : is_license_open,
                "record_type_label" : get_record_type_label,
                "get_suborgs": get_suborgs,
                "edc_linked_gravatar": edc_linked_gravatar,
                "edc_gravatar": edc_gravatar,
                "record_is_viewable": record_is_viewable,
                "get_espg_id" : get_espg_id,
                "get_user_role_orgs" : get_user_role_orgs,
                "get_all_orgs" : get_all_orgs
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
        map.connect('/dataset/remove_file', controller=package_controller, action='remove_uploaded')
#        map.connect('/dataset/duplicate/{id}', controller=package_controller, action='duplicate')

        with SubMapper(map, controller=package_controller) as m:
            m.connect('add dataset', '/dataset/new', action='new')
            m.connect('dataset_edit', '/dataset/edit/{id}', action='edc_edit',ckan_icon='edit')
            m.connect('search', '/dataset', action='search', highlight_actions='index search')
            m.connect('dataset_read', '/dataset/{id}', action='read', ckan_icon='sitemap')
            m.connect('duplicate', '/dataset/duplicate/{id}', action='duplicate')
            m.connect('/dataset/{id}/resource/{resource_id}', action='resource_read')
            m.connect('/dataset/{id}/resource_delete/{resource_id}', action='resource_delete')
            m.connect('/authorization-error', action='auth_error')
            m.connect('resource_edit', '/dataset/{id}/resource_edit/{resource_id}', action='resource_edit', ckan_icon='edit')

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
            m.connect('organization_read', '/organization/{id}', action='read')
            m.connect('organization_about', '/organization/about/{id}',
                  action='about', ckan_icon='info-sign')
            m.connect('organization_read', '/organization/{id}', action='read',
                  ckan_icon='sitemap')
            m.connect('organization_edit', '/organization/edit/{id}',
                  action='edit', ckan_icon='edit')
            m.connect('organization_members', '/organization/members/{id}',
                  action='members', ckan_icon='group')
            m.connect('organization_bulk_process',
                  '/organization/bulk_process/{id}',
                  action='bulk_process', ckan_icon='sitemap')

        map.connect('sitemap','/sitemap.html', controller=site_map_controller, action='view')
        map.connect('sitemap','/sitemap.xml', controller=site_map_controller, action='read')

    # /api/util ver 1, 2, 3 or none
        with SubMapper(map, controller=api_controller, path_prefix='/api{ver:/1|/2|/3|}',
                   ver='/1') as m:

            m.connect('/i18n/{lang}', action='i18n_js_translations')
            m.connect('/')

        GET_POST = dict(method=['GET', 'POST'])

        # /api ver 3 or none
        #with SubMapper(map, controller=api_controller, path_prefix='/api{ver:/3|}', ver='/3') as m:
        m.connect('/action/{logic_function}', action='action', conditions=GET_POST)


        return map

    def after_map(self, map):
        return map;

#     #Check the datasaet upload image
#     def after_update(self, context, pkg_dict):
#         from ckanext.edc_schema.controllers.package import EDCPackageController
#
#         controller = EDCPackageController()
#         controller._check_file_upload(context, pkg_dict)


    def after_show(self, context, pkg_dict) :
        '''
        Checks if a new image has been uploaded or the image has been updated or removed
        and applies the proper changes to image_url field.
        The image_url should not contain the temp file name, either it is empty or it should
        have the same name as the dataset id.
        '''

        from ckanext.edc_schema.controllers.package import from_utc

        #Set the last modified date of the record.
        '''
        metadata_modified_time = from_utc(pkg_dict['metadata_modified'])
        revision_timestamp_time = from_utc(pkg_dict['revision_timestamp'])

        if (metadata_modified_time >= revision_timestamp_time):
            pkg_dict['last_modified_date'] = metadata_modified_time.strftime('%Y-%m-%d')
        else:
            pkg_dict['last_modified_date'] = revision_timestamp_time.strftime('%Y-%m-%d')
        '''

#         #Ignore changes if dataset doesn't have any image
#         if not 'image_url' in pkg_dict or not 'image_delete' in pkg_dict :
#             return
#
#
#         from pylons import config
#         import os
#         from ckanext.edc_schema.util.file_uploader import DEFAULT_UPLOAD_FILENAME
#
#         image_is_deleted = pkg_dict['image_delete']
#
#         if image_is_deleted == '0' :
#             #Get the upload directory path
#             upload_path = os.path.join(config.get('ckan.site_url'),'uploads', 'edc_files') + '/'
#
#             #Take the current image url
#             upload_url = pkg_dict['image_url']
#
#             #Get the image file name
#             uploaded_file = upload_url[len(upload_path):]
#
#             name, extension = os.path.splitext(uploaded_file)
#
#             #Check if this a temp file (A new file has been uploaded)
#             if name.startswith(DEFAULT_UPLOAD_FILENAME) :
#                 #change the image file name to the dataset id
#                 new_filename = upload_path + pkg_dict['id'] + extension
#                 pkg_dict['image_url'] = new_filename
#         else:
#             pkg_dict['image_url'] = ''
#

#     def after_delete(self, context, pkg_dict):
#         '''
#         Checks if there are any images named as dataste id in uploaded image directory
#         and removes them. This way we wont get a list orphan images wasting file store space.
#         '''
#         import os
#
#         from ckanext.edc_schema.util.file_uploader import (FileUploader, DEFAULT_UPLOAD_FILENAME)
#
#         pkg_image_name = pkg_dict['id']
#         temp_image_name = DEFAULT_UPLOAD_FILENAME + pkg_image_name
#
#         #Get the upload directory path
#         file_uploader =  FileUploader()
#         upload_path = file_uploader.storage_path
#
#         image_files_to_be_deleted = []
#
#         #Get a list of all files in upload directory that has the same name as dataset id
#         for filename in os.listdir(upload_path) :
#             name, extension = os.path.splitext(filename)
#             if name == pkg_image_name or name == temp_image_name :
#                 image_files_to_be_deleted.append(filename)
#
#         #Delete all files in the list
#         for filename in image_files_to_be_deleted:
#             filepath = os.path.join(upload_path, filename)
#             try :
#                 os.remove(filepath)
#             except OSError :
#                 pass

    def before_index(self, pkg_dict):
        '''
        Makes the sort by name case insensitive.
        Note that the search index must be rebuild for the first time to take changes into account.
        '''
        title = pkg_dict['title']
        if title:
            #Assign title to title_string with all characters switched to lower case.
            pkg_dict['title_string'] = title.lower()

        return pkg_dict


    def before_search(self, search_params):

        #Change the default sort order
        if search_params.get('sort') in (None, 'rank'):
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
            #pprint.pprint(user_name)

            #  There are no restrictions for sysadmin
            if c.userobj and c.userobj.sysadmin == True:
                fq += ' '
            else:
                if user_name != 'visitor':
                    fq += ' (+(edc_state:("PUBLISHED" OR "PENDING ARCHIVE") AND metadata_visibility:("Public"))'

                    #IDIR users can also see private records of their organizations
                    user_id = c.userobj.id
                    #Get the list of orgs that the user is an admin or editor of
                    user_orgs = ['"' + org.id + '"' for org in get_user_orgs(user_id, 'admin')]
                    user_orgs += ['"' + org.id + '"' for org in get_user_orgs(user_id, 'editor')]
                    if user_orgs != []:
                        fq += ' OR (' + 'owner_org:(' + ' OR '.join(user_orgs) + ') ))'
                    else:
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

    def dataset_facets(self, facet_dict, package_type):

        #Remove groups from the facet list
        if 'groups' in facet_dict :
            del facet_dict['groups']

        if 'tags' in facet_dict :
            del facet_dict['tags']

        if 'organization' in facet_dict:
            del facet_dict['organization']

        if 'license_id' in facet_dict:
            del facet_dict['license_id']

        if 'res_format' in facet_dict:
            del facet_dict['res_format']

        #Add dataset types and organization sectors to the facet list
        facet_dict['sector'] = _('Sectors')
        facet_dict['license_id'] = _('License')
        facet_dict['type'] = _('Dataset types')
        facet_dict['res_format'] = _('Format')
        facet_dict['organization'] = _('Organizations')

        context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}

        if c.userobj and c.userobj.sysadmin:
          facet_dict['edc_state'] = _('States')

        return facet_dict


    def get_actions(self):
        import ckanext.edc_schema.logic.action as edc_action
        return {'edc_package_update' : edc_action.edc_package_update,
                'package_update' : edc_action.package_update,
                'post_comment' : edc_action.post_disqus_comment }

#     def get_auth_functions(self):
#
#         import ckanext.edc_schema.util.auth as edc_auth
#
#         auth_dict = {
#                       'user_show' : edc_auth.user_show,
#                       'user_list' : edc_auth.user_list
#                       }
#         return auth_dict
