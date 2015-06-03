# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 

import urllib2
import urllib
import json
import pprint
import sys

from base import (site_url, api_key)

records = []
records_filename = './data/records_with_html_errors.txt'
with open(records_filename) as records_file :
    records = records_file.read().splitlines()


print 'Fixing description for records containing [HTML_REMOVED] ...'
count = 0  

for record in records :
    pkg_id = record.strip()
    data_string = urllib.quote(json.dumps({'id': pkg_id}))
    try:
        request = urllib2.Request(site_url + '/api/3/action/package_show')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200
         
        response_dict = json.loads(response.read())
        assert response_dict['success'] is True
        pkg_dict = response_dict['result']
    except Exception:
        print 'Record with name %s not found.' %(pkg_id)
        continue
    if pkg_dict :
        description = pkg_dict.get('notes')
        
        if not '&apos;' in description :
            print 'Nothing needs to be fixed in %s .' %(pkg_id)
            continue
        
        pkg_dict['notes'] = description.replace('&apos;', "'")
        
        data_string = urllib.quote(json.dumps(pkg_dict))
        try:
            request = urllib2.Request(site_url + '/api/3/action/package_update')
            request.add_header('Authorization', api_key)
            response = urllib2.urlopen(request, data_string)
            assert response.code == 200
         
            response_dict = json.loads(response.read())
            assert response_dict['success'] is True
            pkg_dict = response_dict['result']
            print '.'
            count += 1
        except Exception:
            'Exception raised when updating record with name %s ' %(pkg_id)
            pass

print count, ' records were updated.'        
