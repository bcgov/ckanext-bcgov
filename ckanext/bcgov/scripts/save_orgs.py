# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
import json
import urllib2
import urllib

import pprint


from base import (site_url, api_key) 

org_filename = './data/orgs_list.json'

data_string = json.dumps({'all_fields' : True})

org_list = []

try :
    request = urllib2.Request(site_url + '/api/3/action/organization_list')
    request.add_header('Authorization', api_key)
    response = urllib2.urlopen(request, data_string)
    assert response.code == 200

    response_dict = json.loads(response.read())
    assert response_dict['success'] is True

    org_list = response_dict['result']
#    pprint.pprint(user_list)
except Exception, e:
    pass

#Create a dictionary of org_name : org_id
#We need this dictionary to get the id of each org when creating organizations
orgs_dict = {}

for org in org_list :
    
    members = []
    data_dict = {'id' : org['id'], 'object_type' : 'user'}
    data_string = urllib.quote(json.dumps(data_dict))
    try :
        request = urllib2.Request(site_url + '/api/3/action/member_list')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        members = response_dict['result']
#        pprint.pprint(user_list)
    except Exception, e:
        pass
    org_dict = {'id' : org['id'], 'members' : members}
    orgs_dict[org['name']] = org_dict
    
with open(org_filename, 'w') as org_file :
    org_file.write(json.dumps(orgs_dict))
