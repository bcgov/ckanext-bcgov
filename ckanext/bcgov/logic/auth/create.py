import ckan.model as model
from ckan.common import  c

import ckan.logic as logic
import ckan.authz as authz
import ckan.logic.auth as logic_auth

from ckan.logic.auth.create import _check_group_auth

from ckan.common import _

import pprint

@logic.auth_allow_anonymous_access
def package_create(context, data_dict=None):
    user = context['user']

    user_object = context.get('auth_user_obj')

    #Sysadmin user has all the previliges 
    if user_object and user_object.sysadmin :
        {'success': True}

    #Do not authorize anonymous users
    if authz.auth_is_anon_user(context):
        return {'success': False, 'msg': _('User %s not authorized to create packages') % user}
    
    #Check if the user has the editor or admin role in some org/suborg
    check1 = all(authz.check_config_permission(p) for p in (
        'create_dataset_if_not_in_organization',
        'create_unowned_dataset',
        )) or authz.has_user_permission_for_some_org(
        user, 'create_dataset')

    if not check1:
        return {'success': False, 'msg': _('User %s not authorized to create packages') % user}

    check2 = _check_group_auth(context,data_dict)
    if not check2:
        return {'success': False, 'msg': _('User %s not authorized to edit these groups') % user}

    # If an organization is given are we able to add a dataset to it?
    data_dict = data_dict or {}
    org_id = data_dict.get('owner_org')
    if org_id and not authz.has_user_permission_for_group_or_org(
            org_id, user, 'create_dataset'):
        return {'success': False, 'msg': _('User %s not authorized to add dataset to this organization') % user}

    return {'success': True}

