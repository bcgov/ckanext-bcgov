# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
import json
import urllib2
import urllib

import pprint



user_filename = './data/users_list.json'

from base import (site_url, api_key)

with open(user_filename, 'r') as user_file :
    user_list = json.loads(user_file.read())

for user in user_list :
    
    #Check if the user is not already added to the site
    user_result = None
    data_string = json.dumps({'id': user['id']})
    try :
        request = urllib2.Request(site_url + '/api/3/action/user_show')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        user_result = response_dict['result']
    except Exception, e:
        pass
    
    #Create the user if it's not found
    if not user_result :
        #Create the user
        data_dict = {'name' : user['name'],
                     'email' : user['email'],
                     'fullname' : user['fullname'],
                     'password' : 'r3db1rd',
                     'id' : user['id'],
                     'about' : user['about']}
        data_string = json.dumps(data_dict)
        try :
            request = urllib2.Request(site_url + '/api/3/action/user_create')
            request.add_header('Authorization', api_key)
            response = urllib2.urlopen(request, data_string)
            assert response.code == 200

            response_dict = json.loads(response.read())
            assert response_dict['success'] is True

            new_result = response_dict['result']
        except Exception, e:
            pass    