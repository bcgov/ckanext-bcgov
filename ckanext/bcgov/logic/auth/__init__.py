# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
import ckan.model as model

 
def get_user_org_roles(user_id) :
    '''
    Returns a dictionary of (org_id, role) for all the organizations that the given user_id is a member of.
    '''

    if not user_id :
    	return {}
    	
    member_query = model.Session.query(model.Member.group_id, model.Member.capacity) \
                   .filter(model.Member.table_name == 'user') \
                   .filter(model.Member.state == 'active') \
                   .filter(model.Member.table_id == user_id)

    return dict(member_query.all())
