# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
import csv
import json
import urllib
import urllib2

import sys


def write_packages_to_file(pakages, csv_writer):
    '''
    Writes the given list of packages data to the csv file.
    '''
    
    for pkg in packages:
        '''
        Get selected fields of the package
        '''
        dataset_type = pkg.get('type')
        edc_state = pkg.get('edc_state')
        record_publish_date = pkg.get('record_publish_date')
        record_create_date = pkg.get('record_create_date')
        name = pkg.get('name')
        odsi_uid = pkg.get('odsi_uid')
        metastar_uid = pkg.get('metastar_uid')
    
        '''
        Add the selected fields as a new row to csv file
        '''
        csv_row = [dataset_type, edc_state, record_publish_date,
                   record_create_date, name, odsi_uid, metastar_uid]
    
        csv_writer.writerow(csv_row)

def get_package_chunk(data_dict, api_key):
    '''
    Gets a chunk of at most 1000 records from the search results, the offset is
    specified by the start parameter in data_dict.
    '''
    
    params = urllib.quote(json.dumps(data_dict))
    try:
        request = urllib2.Request(site_url + '/api/3/action/package_search')
        if api_key :
            request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, params)
        assert response.code == 200

        response_dict = json.loads(response.read())
    
        assert response_dict['success'] == True
        result = response_dict['result']
        if result :
            count = result['count']
            packages = result.get('results', [])
        else : 
            count = 0
            packages = []
    except Exception, e:
        print str(e)
        exit()
    
    return count, packages
    
#1) Get the input file name.
args = sys.argv
if len(args) < 2 :
    print 'Please provide a valid json file name that includes the site_url, api_key and request parameters as follows :'
    print '{\n\t"site_url" : "http://localhost:5000",\n\t"api_key" : "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",\n\t"params" : {A dictionary of request parameters}\n}'
    sys.exit()
request_filename = sys.argv[1]
    
#2) Get the site_url and request parameters
with open(request_filename, 'r') as req_file :
    data_dict = json.loads(req_file.read())

site_url = data_dict.get('site_url')
api_key = data_dict.get('api_key')
params_dict = data_dict.get('params', {})

limit = params_dict.get('rows', 100000000)
params_dict['rows'] = limit

print 'Searching for records... '

count, packages = get_package_chunk(params_dict, api_key)

if packages == [] :
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
Gets search results in chunks of 1000 records and
Adds the selected fields to the csv file for all packages, until there are no records to write. 
'''
write_packages_to_file(packages, csv_writer)    

max_to_write = min(count, limit)
print "Max num: ", max_to_write
start = 1000
remained = max_to_write - 1000
while remained > 0 :
    params_dict['start'] = start
    params_dict['rows'] = min(remained, 1000)
    count, packages = get_package_chunk(params_dict, api_key)
    write_packages_to_file(packages, csv_writer)    
    remained -= 1000
    start += 1000
    
 
print 'Done.'
csv_file.close()