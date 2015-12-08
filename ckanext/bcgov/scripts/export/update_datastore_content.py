import ckanapi
# import ckanapi_exporter.exporter as exporter
api_key='4ad7e53a-5bac-443e-9d5c-bc1a3407b7fb' # cat

# api_key='2d9d8897-64a9-4399-abd3-f23afc3d4e14' 
domain='http://cat.data.gov.bc.ca'

action='resource_update'
demo = ckanapi.RemoteCKAN(domain,
   api_key)

rec = demo.action.package_show(id='')

types = ['Geographic.csv', 'Dataset.csv', 'Application.csv', 'WebService.csv']

for t in types:
    for res in rec['resources']:
        if t == res['url'].split('/')[-1]:
            print res['name']
            demo.call_action(action,
              {'package_id': rec['id'],'resource_storage_location':"EDC Data Store","edc_resource_type": res['edc_resource_type'],"format": res['format'],"resource_update_cycle": res["resource_update_cycle"],"resource_storage_access_method": res["resource_storage_access_method"],"name":res["name"],"id":res['id']},
                files={'upload': open(res['url'].split('/')[-1])})
