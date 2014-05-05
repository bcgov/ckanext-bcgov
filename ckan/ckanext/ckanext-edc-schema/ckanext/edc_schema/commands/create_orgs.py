import os
import sys
import json
import urllib2
import urllib

from ckanext.edc_schema.commands.base import (default_org_file,
                                              site_url,
                                              api_key,
                                              create_org)

def create_orgs(org_file=None):
        
    if not org_file:
        org_file = default_org_file
              
    if not os.path.exists(org_file):
        print 'File {0} does not exists'.format(org_file)
        sys.exit(1)
                                 
    #Read the organizations json file
    with open(org_file) as json_file:
        orgs = json.loads(json_file.read())
                      
    #Create each organization and all of its branches if it is not in the list of available organizations
    for org_item in orgs:
        branches = org_item['branches']
            
        org = create_org({ 'name': org_item['name'], 'title': org_item['title'] })
        print org['title']
                                         
        for branch in branches:
            sub_org = create_org({ 'name': branch['name'], 'title': branch['title'] })
            
                #Add the sub_org as a member of the org
            member_dict = { 'id': sub_org['id'], 'object' : org['id'], 'object_type' : 'group', 'capacity' : 'admin' }
            data_string =  urllib.quote(json.dumps(member_dict))
            try :
                request = urllib2.Request(site_url + '/api/3/action/member_create')
                request.add_header('Authorization', api_key)
                response = urllib2.urlopen(request, data_string)
                assert response.code == 200
            
                response_dict = json.loads(response.read())
                assert response_dict['success'] is True

            except Exception:
                pass
        
        
create_orgs()
