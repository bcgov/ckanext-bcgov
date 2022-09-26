# Copyright  2015, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license

from ckan.common import c, _

import logging
import re
import ckan.lib.base as base
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultGroupForm

import ckanext.bcgov.forms.converters as converters
cnvrt_to_ext = converters.convert_to_extras;
cnvrt_from_ext = converters.convert_from_extras;
from ckan.lib.navl.validators import (ignore_missing)

# from paste.deploy.converters import asbool
from routes.mapper import SubMapper


import ckan.logic as logic


from ckanext.bcgov.util.util import (
    get_edc_tags,
    edc_type_label,
    get_state_values,
    get_username,
    get_user_orgs,
    get_orgs_user_can_edit,
    get_user_orgs_id,
    get_user_toporgs,
    get_organization_branches,
    can_view_resource,
    get_package_tracking,
    get_resource_tracking)

from ckanext.bcgov.util.helpers import (
    get_suborg_sector,
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
    get_orgs_form,
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
    display_pacific_time,
    sort_vocab_list,
    debug_full_info_as_list,
    remove_user_link,
    get_dashboard_config,
    get_ofi_config,
    get_ofi_resources,
    get_non_ofi_resources,
    get_pow_config,
    log_this)

abort = base.abort

log = logging.getLogger('ckanext.bcgov')
filter_query_regex = re.compile(r'([^:]+:"[^"]+"\s?)')


class SchemaPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=False)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IFacets, inherit=True)
    plugins.implements(plugins.IActions, inherit=True)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IResourceController, inherit=True)

    def get_helpers(self):
        return {
            "dataset_type": get_dataset_type,
            "edc_tags": get_edc_tags,
            "edc_orgs": get_organizations,
            "edc_orgs_form": get_orgs_form,
            "edc_org_branches": get_organization_branches,
            "edc_org_title": get_organization_title,
            "edc_type_label": edc_type_label,
            "edc_state_values": get_state_values,
            "edc_username": get_username,
            "get_sector": get_suborg_sector,
            "get_user_orgs": get_user_orgs,
            "get_user_orgs_id": get_user_orgs_id,
            "get_user_toporgs": get_user_toporgs,
            "get_suborg_sector": get_suborg_sector,
            "get_user_dataset_num": get_user_dataset_num,
            "get_edc_package": get_package_data,
            "is_license_open": is_license_open,
            "record_type_label": get_record_type_label,
            "get_suborgs": get_suborgs,
            "record_is_viewable": record_is_viewable,
            "get_espg_id": get_espg_id,
            "orgs_user_can_edit": get_orgs_user_can_edit,
            "get_facets_selected": get_facets_selected,
            "get_facets_unselected": get_facets_unselected,
            "get_sectors_list": get_sectors_list,
            "get_edc_org": get_edc_org,
            "get_iso_topic_values": get_iso_topic_values,
            "get_eas_login_url": get_eas_login_url,
            "get_fqdn": get_fqdn,
            "get_environment_name": get_environment_name,
            "get_version": get_version,
            "get_bcgov_commit_id": get_bcgov_commit_id,
            "googleanalytics_resource_prefix": resource_prefix,
            "get_parent_org": get_org_parent,
            "size_or_link": size_or_link,
            "display_pacific_time": display_pacific_time,
            "sort_vocab_list": sort_vocab_list,
            "debug_full_info_as_list": debug_full_info_as_list,
            "remove_user_link": remove_user_link,
            "get_dashboard_config": get_dashboard_config,
            "get_ofi_config": get_ofi_config,
            "get_ofi_resources": get_ofi_resources,
            "get_non_ofi_resources": get_non_ofi_resources,
            "can_view_resource": can_view_resource,
            "get_pow_config": get_pow_config,
            "get_package_tracking": get_package_tracking,
            "get_resource_tracking": get_resource_tracking,
            "log": log_this
        }

    # Customizing action mapping
    def before_map(self, map):
        from routes.mapper import SubMapper

        site_map_controller = 'ckanext.bcgov.controllers.site_map:GsaSitemapController'
        ofi_controller = 'ckanext.bcgov.controllers.ofi:EDCOfiController'

        GET_POST = dict(method=['GET', 'POST'])

        # map.connect('package_index', '/', controller=package_controller, action='index')

        map.connect('sitemap', '/sitemap.html', controller=site_map_controller, action='view')
        map.connect('sitemap', '/sitemap.xml', controller=site_map_controller, action='read')

        map.connect('ofi api', '/api/ofi/{call_action}', controller=ofi_controller, action='action', conditions=GET_POST)
        map.connect('ofi resource', '/api/ofi/{format}/{object_name}', action='action')

        return map

    def after_map(self, map):
        return map

    # def before_index(self, pkg_dict):
    #     """
    #     Makes the sort by name case insensitive.
    #     Note that the search index must be rebuild for the first time in order for the changes to take affect.
    #     """
    #     title = pkg_dict['title']
    #     if title:
    #         # Assign title to title_string with all characters switched to lower case.
    #         pkg_dict['title_string'] = title.lower()

    #     res_format = pkg_dict.get('res_format', [])
    #     if 'other' in res_format:
    #         # custom download (other) supports a number of formats
    #         res_format.remove('other')
    #         res_format.extend(['shp', 'fgdb', 'e00'])

    #     return pkg_dict


    # IPackageController
    # def before_search(self, search_params):

    #     if not search_params.get('defType', ''):
    #         search_params['defType'] = 'edismax' # use edismax if query type unspecified
        
    #     if c.userobj and c.userobj.sysadmin is True:
    #         return search_params
        
    #     permission_fq_arr = ['publish_state:("PUBLISHED" OR "PENDING ARCHIVE")']
        
    #     user_orgs = get_orgs_user_can_edit(c.userobj)
    #     for org in user_orgs:
    #         permission_fq_arr.append('owner_org:(' + org + ')')

    #     permission_fq = '(' + " OR ".join(permission_fq_arr) + ')'
                
    #     search_params['fq_list'] = [permission_fq]
    #     if c.userobj is not None:
    #         search_params['fq_list'].append('metadata_visibility:(Public OR IDIR)')
    #     else:
    #         search_params['fq_list'].append('metadata_visibility:(Public)')

    #     #TODO: investigate if this is needed it checks capacity public but currently all records are reporting public capacity
    #     search_params['include_private'] = False
            

    #     log.debug("Before Search {0}".format(search_params))
        return search_params


    # IPackageController
    # def after_search(self, search_results, data_dict=None):

    #     """

    #     Filters private groups out of unauthenticated search

    #     """

    #     from ckanext.bcgov.util.util import can_access_group

    #     # filter simplified { group: count } facets
    #     facets = search_results.get("facets")
    #     results = search_results.get("results")
    #     if facets and facets.get("groups"):
    #         for group in facets["groups"].keys():
    #             if not can_access_group(group):
    #                 del facets["groups"][group]

    #     # filtered full facet info
    #     full_facets = search_results.get("search_facets").get(u"groups")
    #     if full_facets:
    #         full_facets["items"] = [group for group in full_facets["items"]
    #                                 if can_access_group(group["name"])]

    #     # remove private groups from individual search results
    #     for result in results:
    #         if result.get("groups"):
    #             result["groups"] = [group for group in result["groups"]
    #                                 if can_access_group(group["id"])]

    #     return search_results


    # IPackageController
    # def after_show(self, context, pkg_dict):
    #     from ckanext.bcgov.util.util import can_access_group
    #     if pkg_dict.get("groups"):
    #         pkg_dict["groups"] = [group for group in pkg_dict["groups"]
    #                               if can_access_group(group["id"])]



    # IPackageController
    # def before_view(self, pkg_dict):
    #     # CITZEDC808
    #     if not record_is_viewable(pkg_dict, c.userobj):
    #         abort(401, _('Unauthorized to read package %s') % pkg_dict.get("title"))

    #     return pkg_dict

    # def after_update(self, context, pkg_dict):
        # If there are no resources added, redirect to the "add resource" page after saving
        # if len(pkg_dict.get('resources', [])) == 0:
        #    toolkit.redirect_to(controller='package', action='new_resource', id=pkg_dict['id'])

    def dataset_facets(self, facet_dict, package_type):
        """
        Customizes search facet list.
        """

        from collections import OrderedDict
        facet_dict = OrderedDict()
        # Add dataset types and organization sectors to the facet list
        facet_dict['license_id'] = _('License')
        facet_dict['sector'] = _('Sectors')
        facet_dict['res_format'] = _('Format')
        facet_dict['organization'] = _('Organizations')
        facet_dict['download_audience'] = _('Download permission')

        if c.userobj and c.userobj.sysadmin:
            facet_dict['publish_state'] = _('States')

        return facet_dict

    def group_facets(self, facet_dict, group_type, package_type):
        """
        Use the same facets for filtering datasets within group pages
        """
        return self.dataset_facets(facet_dict, package_type)

    def get_actions(self):
        import ckanext.bcgov.logic.action as edc_action
        # import ckanext.bcgov.logic.get as edc_get
        from ckanext.bcgov.logic.ofi import call_action as ofi
        return {
            'organization_list': edc_action.organization_list,
            'group_list': edc_action.group_list,
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
            'ofi_create_order': ofi.ofi_create_order,
            'tag_autocomplete_by_vocab': edc_action.tag_autocomplete_by_vocab,
            'member_list': edc_action.member_list,
            'whoami': edc_action.whoami,
            'update_resource_refresh_timestamp': edc_action.update_resource_refresh_timestamp,
            'organization_list_related': edc_action.organization_list_related
        }

    def get_auth_functions(self):
        from ckanext.bcgov.logic.auth.get import group_show
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
            'ofi_create_order': ofi.ofi_create_order,
            'group_show': group_show
        }

    # IResourceController
    def before_create(self, context, resource):
        # preventative fix for #386 - make sure facet format types are always lowercase;
        resource['format'] = resource.get('format', '').lower()
