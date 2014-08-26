
#Implementation of custom action authenticators
# import ckan.plugins as p
# 
# 
# @p.toolkit.auth_allow_anonymous_access
# def user_show(context, data_dict):
#     import ckan.logic.auth.get as get_auth  
#     user_obj = context['auth_user_obj']
#     
#     if not user_obj :
#         return {'success' : False, 'msg' : 'You are not authorized to view this information'}
#     else :
#         return  get_auth.user_show(context, data_dict)
# 
#     
# @p.toolkit.auth_allow_anonymous_access
# def user_list(context, data_dict):
#     import ckan.logic.auth.get as get_auth
# 
#     user_obj = context['auth_user_obj']
#     
#     if not user_obj :
#         return {'success' : False, 'msg' : 'You are not authorized to view this information'}
#     else :
#         return  get_auth.user_list(context, data_dict)
    