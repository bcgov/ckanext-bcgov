# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
'''
This script import current users from an environment and
Save it to a json file.
This information can be used later to create the users on the same 
or another environment.
'''

import json
import urllib2
import urllib

from base import (site_url, api_key) 

import pprint

#ckan.logic.action.create.organization_member_create(context, data_dict)

#1) Get the list of all users

user_list = []
try :
    request = urllib2.Request(site_url + '/api/3/action/user_list')
    request.add_header('Authorization', api_key)
    response = urllib2.urlopen(request)
    assert response.code == 200

    response_dict = json.loads(response.read())
    assert response_dict['success'] is True

    user_list = response_dict['result']
#    pprint.pprint(user_list)
except Exception, e:
    pass


#2) For each user find the list organizations and the user role in each org

user_file = open('./data/users_list.json', 'w')
user_file.write(json.dumps(user_list))
user_file.close()
