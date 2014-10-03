import os
import sys
import json
import urllib2
import urllib
import pprint

from base import (
                  create_org, 
                  site_url,
                  api_key
                )


def create_odsi_orgs():
    
    orgs_filename = './data/orgs.json'
    suborgs_filename = './data/suborgs.json'
    
    if not os.path.exists(orgs_filename):
        print 'File {0} does not exist'.format(orgs_filename)
        sys.exit(1)
    if not os.path.exists(suborgs_filename):
        print 'File {0} does not exist'.format(suborgs_filename)
        sys.exit(1)
        
    
    #Get the json file for organization and sun-organizations (Ministry and branches)
#    orgs_dict = json.load(urllib2.urlopen('http://apps.gov.bc.ca/pub/odc/v2/orgs.json'))
#    suborgs_dict = json.load(urllib2.urlopen('http://apps.gov.bc.ca/pub/odc/v2/orgs/suborgs.json'))
    
    with open(orgs_filename) as org_file:
        orgs_dict = json.loads(org_file.read())

    with open(suborgs_filename) as suborg_file:
        suborgs_dict = json.loads(suborg_file.read())
        
    #Take the list of organizations    
    orgs_list = orgs_dict['organizations']
    
    #Get the list branches for all organizations
    suborgs_data = suborgs_dict['organizations']
    
    for org_obj in orgs_list :
        pprint.pprint(org_obj)
        #For each organization get the name and title and create the organization
        (org_name, org_title) = org_obj.items()[0]
        org_dict = {
                    'name'  : org_name.replace('_', '-'),
                    'title' : org_title
                    }
        org = create_org(org_dict)
            
        #Get the list of sub-organizations for this organization
        suborgs_list = []
        for suborg_item in suborgs_data :
            if org_name in suborg_item :
                suborgs_list = suborg_item[org_name]
                break
        
        #Create the sub-organizations
        for suborg_obj in suborgs_list :
            (suborg_name, suborg_title) = suborg_obj.items()[0]
            suborg_dict = {
                           'name'  : suborg_name.replace('_', '-'),
                           'title' : suborg_title
                           }
            suborg = create_org(suborg_dict)
            
            #Add this sub-organization as a child of the organization
            member_dict = { 'id': suborg['id'], 'object' : org['id'], 'object_type' : 'group', 'capacity' : 'admin' }
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
            
        

create_odsi_orgs()
