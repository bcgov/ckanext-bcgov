# Copyright  2015, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license

import re
import os
import csv
import sys
import json
import urllib2
import urllib
import pprint

from base import (create_org, site_url, api_key)


def get_orgs_data():
    '''
    Creates a dictionary of organizations from the input csv file.
    This data dictionary is used to import organizations.
    '''

    orgs_filename = "./data/org_suborg_sector_mapping_forEDC.csv"

    #Check if the organization data file exists.
    if not os.path.exists(orgs_filename):
        print 'File {0} does not exist'.format(orgs_filename)
        sys.exit(1)

    reader = csv.reader(open(orgs_filename, 'r'), skipinitialspace=True)
    row_num = -1
    data_dict = {}
    #For each row in csv file
    for row in reader:
        #Skip the header row
        row_num += 1
        if row_num == 0:
            continue
        print str(row_num).rjust(4), ' ------> ', row[1].ljust(85), ' ', row[
            2].ljust(70), ' ', row[3].ljust(20)

        #Get the org title, sub-org title and the sector
        org = row[1]
        sub_org = row[2]
        sector = row[3]

        #Create sub-org dictionary
        sub_org_data = {'sub_org': sub_org, 'sector': sector}

        #Add the new sub-org to the list of sub-organizations of the current org
        sub_org_list = []

        #Check if the org is already in the dictionary and obtain the current list of sub_orgs.
        if org in data_dict:
            sub_org_list = data_dict[org]
        if sub_org_data not in sub_org_list:
            sub_org_list.append(sub_org_data)

        #Add/update the org data to/in the data dictionary
        data_dict[org] = sub_org_list

    pprint.pprint(data_dict)

    return data_dict


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

    for org_obj in orgs_list:
        pprint.pprint(org_obj)
        #For each organization get the name and title and create the organization
        (org_name, org_title) = org_obj.items()[0]
        org_dict = {'name': org_name.replace('_', '-'), 'title': org_title}
        org = create_org(org_dict)

        #Get the list of sub-organizations for this organization
        suborgs_list = []
        for suborg_item in suborgs_data:
            if org_name in suborg_item:
                suborgs_list = suborg_item[org_name]
                break

        #Create the sub-organizations
        for suborg_obj in suborgs_list:
            (suborg_name, suborg_title) = suborg_obj.items()[0]
            suborg_dict = {
                'name': suborg_name.replace('_', '-'),
                'title': suborg_title,
                'sector': 'Health-Test'
            }
            suborg = create_org(suborg_dict)

            #Add this sub-organization as a child of the organization
            member_dict = {
                'id': suborg['id'],
                'object': org['id'],
                'object_type': 'group',
                'capacity': 'admin'
            }
            data_string = urllib.quote(json.dumps(member_dict))
            try:
                request = urllib2.Request(
                    site_url + '/api/3/action/member_create')
                request.add_header('Authorization', api_key)
                response = urllib2.urlopen(request, data_string)
                assert response.code == 200

                response_dict = json.loads(response.read())
                assert response_dict['success'] is True

            except Exception:
                pass


def convert_title_to_name(title):
    '''
    Constructs a valid name from the given title.
    The name must be purely lower case alphanumeric(ascii) characters and these symbols: -_    
    '''
    name = re.sub('[^0-9a-zA-Z]+', ' ', title)
    name = ' '.join(name.split())
    name = name.lower().strip().replace(' ', '-')
    return name


def create_orgs():
    '''
    Imports the list of ODSI-Discovery organizations and sub-organizations into ckan
    and creates the organization hierarchy.
    '''

    data_dict = get_orgs_data()

    for org_title in data_dict:
        org_name = convert_title_to_name(org_title)
        org_dict = {'name': org_name, 'title': org_title}
        org = create_org(org_dict)

        #Get the list of sub-organizations
        sub_org_list = data_dict[org_title]

        for sub_org_item in sub_org_list:
            sub_org_title = sub_org_item.get('sub_org')
            sub_org_sector = sub_org_item.get('sector')
            sub_org_name = convert_title_to_name(sub_org_title)
            suborg_dict = {
                'name': sub_org_name,
                'title': sub_org_title,
                'sector': sub_org_sector
            }
            sub_org = create_org(suborg_dict)

            if not sub_org: continue
            '''
            Creating organization hierarchy :
                Add this sub-organization as a child of the organization.
            '''
            member_dict = {
                'id': sub_org['id'],
                'object': org['id'],
                'object_type': 'group',
                'capacity': 'admin'
            }
            data_string = urllib.quote(json.dumps(member_dict))
            try:
                request = urllib2.Request(
                    site_url + '/api/3/action/member_create')
                request.add_header('Authorization', api_key)
                response = urllib2.urlopen(request, data_string)
                assert response.code == 200

                response_dict = json.loads(response.read())
                assert response_dict['success'] is True

            except Exception:
                pass


create_orgs()
#create_odsi_orgs()
