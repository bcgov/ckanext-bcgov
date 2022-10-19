import ckan.logic as logic
import ckan.plugins.toolkit as toolkit

from ckan.logic import NotFound

from ckanext.bcgov.util.helpers import record_is_viewable


@logic.auth_allow_anonymous_access
def group_show(context, data_dict=None):

  try:
    group = toolkit.get_action('group_show')(
      { 'ignore_auth': True },
      { 'id': data_dict['id'] })
  except NotFound:
    return { 'success': True } # allow access to 404 pages


  # allow access to this api call if:
  #  - the user is logged in (private groups are available for all logged in users); or
  #  - there's no group to show; or
  #  - there is a group but it's not set to private

  if context.get('auth_user_obj') or \
      not group or \
      not group.get('private'):
    return { 'success': True }

  else:
    return { 'success': False }


@logic.auth_allow_anonymous_access
def package_show(context: Context, data_dict: DataDict) -> AuthResult:
    user = context.get('user')
    user_object = context.get('auth_user_obj')
    package = get_package_object(context, data_dict)
    authorized = record_is_viewable(package, user_object)

    if not authorized:
        return {
            'success': False,
            'msg': _('User %s not authorized to read package %s') % (user, package.id)}
    else:
        return {'success': True}
