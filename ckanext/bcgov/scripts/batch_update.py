# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 

import urllib2
import urllib
import json
import pprint
import sys

from base import (site_url, api_key)

print "Updating records ..."
try:
    request = urllib2.Request(site_url + '/api/3/action/package_list?limit=1000000')
    request.add_header('Authorization', api_key)
    response = urllib2.urlopen(request)
    assert response.code == 200

    # Use the json module to load CKAN's response into a dictionary.
    response_dict = json.loads(response.read())
    assert response_dict['success'] is True

    #package_create returns the created package as its result.
    data_list = response_dict['result']
except Exception, e:
    pass

for pkg in data_list :
    pkg_dict = None
    data_string = urllib.quote(json.dumps({'id': pkg}))
    try:
        request = urllib2.Request(site_url + '/api/3/action/package_show')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200
        
        response_dict = json.loads(response.read())
        assert response_dict['success'] is True
        pkg_dict = response_dict['result']
    except Exception:
        pass
    
    data_string = urllib.quote(json.dumps(pkg_dict))
    try:
        request = urllib2.Request(site_url + '/api/3/action/package_update')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200
        
        response_dict = json.loads(response.read())
        assert response_dict['success'] is True
        pkg_dict = response_dict['result']
        pprint.pprint(pkg_dict)
    except Exception:
        pass
    