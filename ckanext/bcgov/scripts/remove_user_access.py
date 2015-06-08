# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
'''
This script remove a given user (list of users) from all available organizations.
It is required to reconcile the users roles between Adam and CKAN.
CKAN roles should be revoked if they don't match with ADAM roles. 

Input: a json filename including site_url, api_key and list of users to be removed from organizations.

json file structure :

{
    'site_url' : 'http://localhost:5000',
     'api_key' : 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',
     user_list : [list of user names separated by commas]
 }
  
'''
import sys
import json
import urllib
import urllib2
import pprint


def remove_user_from_org(userid, orgid):
    '''
    Removes the user with id: userid from the organization: orgid.
    '''
    data_string = urllib.quote(json.dumps({'id': orgid, 'username': userid.lower() }))
    try:
        request = urllib2.Request(site_url + '/api/3/action/organization_member_delete')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        # Use the json module to load CKAN's response into a dictionary.
        response_dict = json.loads(response.read())
        assert response_dict['success'] is True
        print 'User name %s was removed from organization %s.\n' %(userid, orgid)

    except:
        print 'Error: user name %s was not removed from organization %s.' %(userid, orgid)
        pass
    return


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#1) Get the input file name.
args = sys.argv
if len(args) < 2 :
    print 'Please provide a valid json file name that includes the list of user names with the following structure :'
    print '{\n\t"site_url" : "http://localhost:5000",\n\t"api_key" : "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",\n\t"user_list" : [list of user names separated by commas]\n}'
    sys.exit()
user_filename = sys.argv[1]
    
#2) Get the site_url, api_key and list of users.
with open(user_filename, 'r') as user_file :
    data_dict = json.loads(user_file.read())

api_key = data_dict.get('api_key')
site_url = data_dict.get('site_url')
user_list = data_dict.get('user_list', [])


#3) Create the username to userid mapping for each user
#3.a) Get the user info for each user
name_id_map = {}

for username in user_list:
    data_string = urllib.quote(json.dumps({'id': username.lower() }))
    user_dict = {}
    try:
        request = urllib2.Request(site_url + '/api/3/action/user_show')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        # Use the json module to load CKAN's response into a dictionary.
        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        user_dict = response_dict['result']
    except:
        print 'Username %s does not exist.' % username
        pass
    
#3.b) Add the user id to the map
    
    name_id_map[username] = user_dict.get('id')
    

#4) For each user in the list remove the user from all organizations.

#4.a) Get the list of organizations :

all_orgs = []
data_string = urllib.quote(json.dumps({'all_fields': True }))
try:
    request = urllib2.Request(site_url + '/api/3/action/organization_list')
    response = urllib2.urlopen(request, data_string)
    assert response.code == 200

    # Use the json module to load CKAN's response into a dictionary.
    response_dict = json.loads(response.read())
    assert response_dict['success'] is True

    all_orgs = response_dict['result']
except:
    all_orgs = []
    

#4.b) For each org find the list of org members
for org in all_orgs :
    
    #Get the list of org members
    members = []
    try:
        member_dict = {'id': org.get('id'), 'object_type': 'user'}
        data_string = urllib.quote(json.dumps(member_dict))
        request = urllib2.Request(site_url + '/api/3/action/member_list')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        members = response_dict['result']
    except :
        pass
    
    #Create a list of member id's
    members = [member[0] for member in members]
    
#4.c) For each user in the list, remove the user from the org if it's in the org's member list.    
    for username in user_list :
        user_id = name_id_map.get(username)
        if user_id in members :
            print 'Removing user %s from organization %s' %(username, org.get('name'))
            remove_user_from_org(username, org.get('name'))
    