import ckanapi
# import ckanapi_exporter.exporter as exporter
# from sys import argv
def update_resource(env,res_id,api_key):
	domain='https://'+env+'.data.gov.bc.ca'
	# script, ak = argv

	action='resource_update'
	demo = ckanapi.RemoteCKAN(domain, api_key)
	print res_id
	rec = demo.action.package_show(id=res_id)

	types = ['Geographic.csv', 'Dataset.csv', 'Application.csv', 'WebService.csv']

	for t in types:
	    for res in rec['resources']:
	        if t == res['url'].split('/')[-1]:
	            print res['name']
	            demo.call_action(action,
	              {'package_id': rec['id'],'resource_storage_location':"EDC Data Store","edc_resource_type": res['edc_resource_type'],"format": res['format'],"resource_update_cycle": res["resource_update_cycle"],"resource_storage_access_method": res["resource_storage_access_method"],"name":res["name"],"id":res['id']},
	                files={'upload': open(res['url'].split('/')[-1])})

if __name__ == "__main__":
    update_resource(env,res_id,api_key)