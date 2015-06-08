# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
import os
import sys
import json
import urllib2
import urllib

from base import (create_org, site_url, api_key)

def create_org_members(id, members):
    
    for member in members :
        data_dict = {
                     'id' : id,
                     'username' : member[0],
                     'role': member[2]}
        data_string = json.dumps(data_dict)
        
        try :
            request = urllib2.Request(site_url + '/api/3/action/organization_member_create')
            request.add_header('Authorization', api_key)
            response = urllib2.urlopen(request, data_string)
            assert response.code == 200

            response_dict = json.loads(response.read())
            assert response_dict['success'] is True

        except Exception, e:
            pass                
    

#Get the json file for organization and sun-organizations (Ministry and branches)
orgs_dict = json.load(urllib2.urlopen('http://apps.gov.bc.ca/pub/odc/v2/orgs.json'))
suborgs_dict = json.load(urllib2.urlopen('http://apps.gov.bc.ca/pub/odc/v2/orgs/suborgs.json'))

org_filename = './data/orgs_list.json'
with open(org_filename, 'r') as org_file :
    loaded_orgs = json.loads(org_file.read())

    
#Take the list of organizations    
orgs_list = orgs_dict['organizations']
    
#Get the list branches for all organizations
suborgs_data = suborgs_dict['organizations']
    
for org_obj in orgs_list :
    #For each organization get the name and title and create the organization
    (org_raw_name, org_title) = org_obj.items()[0]
    org_name = org_raw_name.replace('_', '-')
    
    org_data = loaded_orgs[org_name]
    
    org_dict = {
                'name'  : org_name,
                'title' : org_title,
                'id' : org_data['id']
                }
    org = create_org(org_dict)
            
    create_org_members(org_data['id'], org_data['members'])
    
    #Get the list of sub-organizations for this organization
    suborgs_list = []
    for suborg_item in suborgs_data :
        if org_raw_name in suborg_item :
            suborgs_list = suborg_item[org_raw_name]
            break
        
    #Create the sub-organizations
    for suborg_obj in suborgs_list :
        (suborg_raw_name, suborg_title) = suborg_obj.items()[0]
        suborg_name = suborg_raw_name.replace('_', '-')
        
        suborg_data = loaded_orgs[suborg_name]
        
        suborg_dict = {
                           'name'  : suborg_name,
                           'title' : suborg_title,
                           'id' : suborg_data['id']
                           }
        suborg = create_org(suborg_dict)
        create_org_members(suborg_data['id'], suborg_data['members'])
            
        #Add this sub-organization as a child of the organization
        member_dict = { 'id': suborg_data['id'], 'object' : org_data['id'], 'object_type' : 'group', 'capacity' : 'admin' }
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
            

