import ckan.logic as logic
import ckan.plugins.toolkit as toolkit

@logic.auth_allow_anonymous_access
def group_show(context, data_dict=None):

  group = toolkit.get_action('group_show')(
    { 'ignore_auth': True },
    { 'id': data_dict['id'] })

  # allow access to this api call if:
  #  - the user is logged in (private groups are available for all logged in users); or
  #  - there's no group to show; or
  #  - there is a group but it's not set to private

  if context.get('auth_user_obj') or \
      not group or \
      not group.get('private'):
    return {
      'success': True
    }

  else:
    return {
      'success': False
    }