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
        

def create_odsi_orgs():
    
    import pprint
    
    #Get the json file for organization and sun-organizations (Ministry and branches)
    orgs_dict = json.load(urllib2.urlopen('http://apps.gov.bc.ca/pub/odc/v2/orgs.json'))
    suborgs_dict = json.load(urllib2.urlopen('http://apps.gov.bc.ca/pub/odc/v2/orgs/suborgs.json'))
    
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
