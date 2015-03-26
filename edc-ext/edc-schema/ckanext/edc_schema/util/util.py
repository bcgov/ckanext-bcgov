import urllib2
import urllib
import json
import pprint

import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckan.common import  c

import ckan.logic as logic

from ckanext.edc_schema.util.helpers import get_record_type_label
from sqlalchemy import and_

ValidationError = logic.ValidationError

from pylons import config

site_url = config.get('ckan.site_url')
api_key = config.get('ckan.api_key')



def edc_package_create(edc_record):
    '''
    Creates a dataset. Used in package controller to duplicate a dataset.
    '''
    data_string = urllib.quote(json.dumps(edc_record))

    pkg_dict = None
    errors = None
    try:
        request = urllib2.Request(site_url + '/api/3/action/package_create')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        response_dict = json.loads(response.read())
        if response_dict['success'] == True :
            pkg_dict = response_dict['result']
        else:
            errors = response_dict['error']
    except Exception, e:
        print str(e)
        pass
    return (pkg_dict, errors)




def edc_type_label(item):
    rec_type = item['display_name']
    return get_record_type_label(rec_type)

def add_admin(member, site_url, api_key):
    ''' adds a user as admin of an organization'''

    data_string = urllib.quote(json.dumps(member))

    member_dict = None
    errors = None
    try:
        request = urllib2.Request(site_url + '/api/3/action/organization_member_create')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        # Use the json module to load CKAN's response into a dictionary.
        response_dict = json.loads(response.read())
        if response_dict['success'] == True :
            member_dict = response_dict
        else:
            errors = response_dict['error']
    except Exception, e:
        print str(e)
        pass
    return (member_dict, errors)

def get_edc_tags(vocab_id):
    '''
    Returns the list of tags for a given vocabulary.
    '''
    tags = []
    try:
        tags = toolkit.get_action('tag_list')(
                data_dict={'vocabulary_id': vocab_id})
    except toolkit.ObjectNotFound:
        return []

    return tags

def get_org_name(org_id):
    '''
    Returns the organization title with the given id
    '''
    data_string = urllib.quote(json.dumps({'id': org_id, 'include_datasets': False}))
    try:
        request = urllib2.Request(site_url + '/api/3/action/organization_show')
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        org_dict = response_dict['result']
    except:
        org_dict = []

    if org_dict :
        return org_dict['title']
    return None


def get_username(id):
    '''
    Returns the user name for the given id.
    '''
    
    try:
        user = toolkit.get_action('user_show')(data_dict={'id': id})
        return user['name']
    except toolkit.ObjectNotFound:
        return None

def get_user_toporgs(user_id, role=None):
    '''
    Returns the list of orgs that the given user belongs to and has the given role('admin', 'member', 'editor', ...)
    '''

    orgs = []
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}
    org_model = context['model']
    sub_orgs = []

    #Get the list of all first level organizations.
    all_orgs = org_model.Group.get_top_level_groups(type="organization")


    for org in all_orgs:
        members = []
        try:
            member_dict = {'id': org.id, 'object_type': 'user', 'capacity': role}
            #Get the list of id's of all admins of the organization
            members = [member[0] for member in toolkit.get_action('member_list')(data_dict=member_dict)]
        except toolkit.ObjectNotFound:
            members = []

        #Add the org if user is a member of at least one suborg.
        group = org_model.Group.get(org.id)
        suborgs = group.get_children_groups(type = 'organization')

        #If the user id in the list of org's admins then add the org to the final list.
        if user_id in members or c.userobj.sysadmin :
            orgs.append(org)
            for suborg in suborgs :
                sub_orgs.append(suborg)
        else :
            found = False
            for suborg in suborgs :
                members = []
                try:
                    member_dict = {'id': suborg.id, 'object_type': 'user', 'capacity': role}
                    #Get the list of id's of all admins of the organization
                    members = [member[0] for member in toolkit.get_action('member_list')(data_dict=member_dict)]
                except toolkit.ObjectNotFound:
                    members = []

                #If the user id in the list of org's admins then add the org to the final list.
                if user_id in members:
                    sub_orgs.append(suborg)
                    found = True
            if found :
                orgs.append(org)



    return (orgs, sub_orgs)

def get_user_orgs(user_id, role=None):
    '''
    Returns the list of orgs and suborgs that the given user belongs to and has the given role('admin', 'member', 'editor', ...)
    '''
                
    orgs = []
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}
    org_model = context['model']

    #Get the list of all first level organizations.
    all_orgs = org_model.Group.get_top_level_groups(type="organization")

    
    
    for org in all_orgs:
        members = []
        try:
            member_dict = {'id': org.id, 'object_type': 'user', 'capacity': role}
            #Get the list of id's of all admins of the organization
            members = [member[0] for member in toolkit.get_action('member_list')(data_dict=member_dict)]
        except toolkit.ObjectNotFound:
            members = []

        #Add the org if user is a member of at least one suborg.
        group = org_model.Group.get(org.id)
        suborgs = group.get_children_groups(type = 'organization')
        
        #If the user id in the list of org's admins then add the org to the final list.
        if user_id in members:
            orgs.append(org)
            for suborg in suborgs :
                orgs.append(suborg)
        else :
            for suborg in suborgs :
                members = []
                try:
                    member_dict = {'id': suborg.id, 'object_type': 'user', 'capacity': role}
                    #Get the list of id's of all admins of the organization
                    members = [member[0] for member in toolkit.get_action('member_list')(data_dict=member_dict)]
                except toolkit.ObjectNotFound:
                    members = []

                #If the user id in the list of org's admins then add the org to the final list.
                if user_id in members:
                    orgs.append(suborg)
    
    return orgs

def get_user_role_orgs(user_id, sysadmin):
    '''
        Returns the list of all  organizations that the given user is a member of.
        The organizations are splitted in three lists depending of the user role.
        
        Modified by Khalegh Mamakani on March 5 2015.
            -Replaced organization_list and member_list calls with sqlAlchemy queries
             to get the list faster
    '''
    
    if not user_id :
        return ([], [], [])
    
    #Get the list of all organizations (only org id's)
    
    org_query = model.Session.query(model.Group.id).filter(model.Group.type == 'organization')
    
    admin_orgs = [org[0] for org in org_query.all()]
    if sysadmin :
        return (admin_orgs, [], [])
    
    member_query = model.Session.query(model.Member.group_id) \
                   .filter(model.Member.table_name == 'user') \
                   .filter(model.Member.table_id == user_id)
                   
    admin_orgs = member_query.filter(model.Member.capacity == 'admin').distinct(model.Member.group_id).all()
    editor_orgs = member_query.filter(model.Member.capacity == 'editor').distinct(model.Member.group_id).all()
    member_orgs = member_query.filter(model.Member.capacity == 'member').distinct(model.Member.group_id).all()

    admin_orgs = [org[0] for org in admin_orgs]
    editor_orgs = [org[0] for org in editor_orgs]
    member_orgs = [org[0] for org in member_orgs]

    return (admin_orgs, editor_orgs, member_orgs)


def get_user_orgs_id(user_id, role=None):
    user_orgs = get_user_orgs(user_id, role)
    return [org.id for org in user_orgs]

def get_organization_branches(org_id):
    '''
    Get the list of branches for the organization with the given id.
    '''    
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}
    org_model = context['model']

    #Get the list of all children of the organization with the given id
    group = org_model.Group.get(org_id)
    branches = group.get_children_groups(type = 'organization')

    #should only return branches the user is a member of
    return branches
    
def get_parent_orgs(org_id):
    '''
    returns the parent organization(s) of the organization with the given id.
    '''
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}
    org_model = context['model']

    #Get the list of all parents of the organization with the given id
    group = org_model.Group.get(org_id)
    parents = group.get_parent_groups(type = 'organization')

    
    return parents    
    

def get_org_admins(org_id):
    '''
    Returns the list of admins of the given organization
    '''
    try:
        member_dict = {'id': org_id, 'object_type': 'user', 'capacity': 'admin'}
        #Get the list of id's of all admins of the organization
        members = [member[0] for member in toolkit.get_action('member_list')(data_dict=member_dict)]
    except toolkit.ObjectNotFound:
        members = []
    return members


def get_org_users(org_id, role=None):
    '''
    Returns the list of admins of the given organization
    '''
    try:
        member_dict = {'id': org_id, 'object_type': 'user', 'capacity': role}
        #Get the list of id's of all admins of the organization
        members = [member[0] for member in toolkit.get_action('member_list')(data_dict=member_dict)]
    except toolkit.ObjectNotFound:
        members = []
    return members


def edc_state_activity_create(user_name, edc_record, old_state):

    activity_data = {'package' : edc_record}
    activity_info = {'user_id' : user_name,
                     'object_id' : edc_record['id'],
                     'activity_type' : 'changed package',
                     'data' : activity_data}

    data_string = urllib.quote(json.dumps(activity_info))
    request = urllib2.Request(site_url + '/api/3/action/activity_create')
    request.add_header('Authorization', api_key)

    try:
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True
        activity_result = response_dict['result']
    except:
        return False

    return True


def get_state_values(userobj, pkg):
    '''
    This methods creates a list of possible values for the state of given dataset
    based on the current state of dataset and the user that updates the dataset.
    :param user_id: The id of the current user.
    :param pkg : The given dataset.
    :returns: A list of possible values of the state of the dataset.
    '''
    states = []


    if not pkg or not pkg.has_key('id'):
        return ['DRAFT']

    id = pkg['id']
    org_id = pkg['owner_org']


    #Get the list of admins of the dataset
    member_data = {
                   'id' : org_id,
                   'object_type' : 'user',
                   'capacity' : 'admin'
                   }

    if org_id :
        admins = [admin[0] for admin in toolkit.get_action('member_list')(data_dict=member_data)]
    else :
        admins = []

    current_state = pkg['edc_state']

    if current_state == 'DRAFT':
        states = ['DRAFT', 'PENDING PUBLISH']
    elif current_state == 'REJECTED' :
        states = ['DRAFT', 'PENDING PUBLISH', 'REJECTED']
    elif current_state == 'PENDING PUBLISH':
        if userobj.id in admins or userobj.sysadmin :
            states = ['PENDING PUBLISH', 'PUBLISHED', 'REJECTED']
        else :
            states = ['DRAFT', 'PENDING PUBLISH']
    elif current_state == 'PUBLISHED' :
        if userobj.id in admins or userobj.sysadmin :
            states = ['PENDING PUBLISH', 'PUBLISHED', 'PENDING ARCHIVE']
        else :
            states = ['PUBLISHED', 'PENDING ARCHIVE']
    elif current_state == 'PENDING ARCHIVE' :
        if userobj.id in admins or userobj.sysadmin :
            states = ['PUBLISHED', 'PENDING ARCHIVE', 'ARCHIVED']
        else :
            states = ['PUBLISHED', 'PENDING ARCHIVE']
    elif current_state == 'ARCHIVED' :
        if userobj.id in admins or userobj.sysadmin:
            states = ['PENDING ARCHIVE', 'ARCHIVED']
        else :
            states = ['ARCHIVED']

    return states

def get_user_list():
    '''
    Returns the list of available users.
    '''
    request = urllib2.Request(site_url + '/api/3/action/user_list')
    request.add_header('Authorization', api_key)

    try:
        response = urllib2.urlopen(request)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True
        user_list = response_dict['result']
    except:
        return []
    return user_list

def get_all_orgs():
    '''
    Returns all user orgs as a dictionary with the id as the key
    and the value is a tuple of (name, title)
    '''
    orgs_dict = {}
 
#     data_string = urllib.quote(json.dumps({'all_fields': True}))
#     request = urllib2.Request(site_url + '/api/3/action/organization_list')
#     request.add_header('Authorization', api_key)
#     response = urllib2.urlopen(request, data_string)
#     response_dict = json.loads(response.read())
# 
#     for org in response_dict['result']:
#         orgs_dict[org['id']] = {'name': org['name'], 'title': org['title']}
    
    all_orgs = model.Group.all('organization')
    
    for org in all_orgs:
        orgs_dict[org['id']] = {'name': org.name, 'title': org.title }

    return orgs_dict
