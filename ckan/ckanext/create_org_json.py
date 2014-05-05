#!/usr/bin/env python
import urllib2
import urllib
import json
import pprint


orgs_data = json.load(urllib2.urlopen('http://apps.gov.bc.ca/pub/odc/v2/orgs.json'))
orgs = orgs_data['organizations']

sub_orgs_data = json.load(urllib2.urlopen('http://apps.gov.bc.ca/pub/odc/v2/orgs/suborgs.json'))
sub_orgs = sub_orgs_data['organizations']

org_json_file = open("./data/organizations.json", "w")

org_list = []
for org in orgs :
    for org_name, org_title in org.iteritems() :
        org_dict = {'name' : org_name.replace('_', '-'), 'title' : org_title }
        
        branches = (value for sub_org in sub_orgs for key, value in sub_org.iteritems() if key == org_name).next()
        
        branch_list = []
        for branch in branches :
            for branch_name, branch_title in branch.iteritems() :
                branch_dict = {'name': branch_name.replace('_','-'), 'title' : branch_title }
                branch_list.append(branch_dict)
        org_dict.update({'branches' : branch_list})
        org_list.append(org_dict)
        
org_json_file.write(json.dumps(org_list))
org_json_file.close()

        