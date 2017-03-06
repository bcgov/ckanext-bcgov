from pprint import pprint

import ckan.plugins.toolkit as toolkit

_ = toolkit._


def geo_resource_form(context, data_dict=None):
    user_obj = context.get('auth_user_obj')
    user_obj_checked = context.get('__auth_user_obj_checked', False)

    if user_obj and user_obj_checked:
        return {'success': True}

    return {'success': False, 'msg': _('Failed authorization.')}


def populate_dataset_with_ofi(context, data_dict=None):
    user_obj = context.get('auth_user_obj')
    user_obj_checked = context.get('__auth_user_obj_checked', False)

    if toolkit.check_access('package_create', context, data_dict):
        return {'success': True}

    return {'success': False, 'msg': _('Failed authorization.')}


def check_object_name(context, data_dict=None):
    user_obj = context.get('auth_user_obj')
    user_obj_checked = context.get('__auth_user_obj_checked', False)

    if user_obj and user_obj_checked:
        return {'success': True}

    return {'success': False, 'msg': _('Failed authorization.')}


def remove_ofi_resources(context, data_dict=None):
    user_obj = context.get('auth_user_obj')
    user_obj_checked = context.get('__auth_user_obj_checked', False)

    pkg_id = data_dict.get('package_id', '')

    if toolkit.check_access('package_delete', context, {'id': pkg_id}):
        if toolkit.check_access('package_update', context, {'id': pkg_id}):
            return {'success': True}

    return {'success': False, 'msg': _('Failed authorization.')}


def edit_ofi_resources(context, data_dict=None):
    user_obj = context.get('auth_user_obj')
    user_obj_checked = context.get('__auth_user_obj_checked', False)

    if toolkit.check_access('package_create', context, data_dict):
        return {'success': True}

    return {'success': False, 'msg': _('Failed authorization.')}


@toolkit.auth_allow_anonymous_access
def crs_types(context, data_dict=None):
    return {'success': True}


@toolkit.auth_allow_anonymous_access
def get_max_aoi(context, data_dict=None):
    return {'success': True}


@toolkit.auth_allow_anonymous_access
def ofi_create_order(context, data_dict=None):
    return {'success': True}


@toolkit.auth_allow-anonymous_access
def file_formats(context, data_dict=None):
    return {'success': True}
