#export package number of each parent org. This does this is a round about since http://catalogue.data.gov.bc.ca/api/3/action/organization_list_related?all_fields=1 doesn't show the record total for parent organizations

import ckanapi
import requests
import json
import csv

from sys import argv

script, env, api_key, rec_id = argv

domain ='https://' + env + '.data.gov.bc.ca'
url = domain + '/api/3/action/organization_list'

request = requests.get(url)
all_orgs= request.json()["result"]

o_list = {}

# with open('packages_per_org.json', 'w') as outfile:
for o in all_orgs:
	org = requests.get('https://catalogue.data.gov.bc.ca/api/3/action/organization_show?id='+o).json()["result"]
	# print org
	if org['groups'] != [] :
		# print org['groups'][0]['name']
		if org['groups'][0]['name'] not in o_list:
			o_list[org['groups'][0]['name']] = len(org['packages'])
		else:
			o_list[org['groups'][0]['name']] += len(org['packages'])
		# print org['groups'][0]['name']
		

print o_list
	# json.dump(o_list, outfile)
#upload to package
demo = ckanapi.RemoteCKAN(domain, api_key)
action='resource_update'
rec = demo.action.package_show(id = rec_id)

with open('packagesperorg' + '.csv', 'wb') as f:
	writer = csv.writer(f)
	writer.writerow(['organization','record_number'])
	for key, value in o_list.iteritems():
		if value >=1:
			writer.writerow([key,value])



for res in rec['resources']:
	if res['url'].split('/')[-1] == 'packagesperorg.csv':
		demo.call_action(action,
	              {'package_id': rec['id'],'resource_storage_location':res['resource_storage_location'],"edc_resource_type": res['edc_resource_type'],"format": res['format'],"resource_update_cycle": res["resource_update_cycle"],"resource_storage_access_method": res["resource_storage_access_method"],"name":res["name"],"id":res['id']},
	                files={'upload': open(res['url'].split('/')[-1])})


