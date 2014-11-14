import csv
import json
import urllib
import urllib2

print 'Getting list of packages... '
site_url = 'http://cat.data.gov.bc.ca'
data_string = urllib.quote(json.dumps({'all_fields': True, 'limit': 100}))
try:
    request = urllib2.Request(site_url + '/api/search/package')
    response = urllib2.urlopen(request, data_string)
    assert response.code == 200

    # Use the json module to load CKAN's response into a dictionary.
    response_dict = json.loads(response.read())
        # package_create returns the created package as its result.
    result = response_dict['results']
except:
    result = []

if result == [] :
    print 'No packages were found.'
    exit()

print 'Writing the packages data to package_list.csv.'
    
'''
Creating the csv file and adding the header row
'''
csv_file = open("package_list.csv", 'wb')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['dataset_type','edc_state','record_publish_date','record_create_date','name','odsi_uid','metastar_uid'])

'''
Adding the selected fields to the csv file for all packages. 
'''
for pkg in result:
    '''
    Fetch extra fields from package extras dictionary
    '''
    extras = pkg.get('extras', [])
    dataset_type = pkg.get('dataset_type')
    edc_state = extras.get('edc_state')
    record_publish_date = extras.get('record_publish_date')
    record_create_date = extras.get('record_create_date')
    name = pkg.get('name')
    odsi_uid = extras.get('odsi_uid')
    metastar_uid = extras.get('metastar_uid')
    
    '''
    Add the selected fields a s new row to csv file
    '''
    csv_row = [dataset_type, edc_state, record_publish_date,
               record_create_date, name, odsi_uid, metastar_uid]
    
    csv_writer.writerow(csv_row)
    

print 'Done.'
csv_file.close()