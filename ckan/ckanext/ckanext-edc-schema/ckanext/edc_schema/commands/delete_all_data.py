
from ckanext.edc_schema.commands.base import (site_url,
                                              api_key)
import urllib2
import urllib
import json
import pprint
import sys

#Get the list of all data

print "Deleting records ..."
try:
    request = urllib2.Request(site_url + '/api/3/action/package_list?limit=100000')
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
    data_string = urllib.quote(json.dumps({'id': pkg}))
    try:
        request = urllib2.Request(site_url + '/api/3/action/package_delete')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200
        
        response_dict = json.loads(response.read())
        assert response_dict['success'] is True
        print '.'
    except Exception:
        pass




# from ckanext.edc_schema.commands.base import (site_url,
#                                               api_key)
# import urllib2
# import urllib
# import json
# import pprint
# 
# #Get the list of all data
# 
# 
# try:
#     request = urllib2.Request(site_url + '/api/3/action/current_package_list_with_resources')
#     response = urllib2.urlopen(request)
#     assert response.code == 200
# 
#     # Use the json module to load CKAN's response into a dictionary.
#     response_dict = json.loads(response.read())
# #   pprint.pprint(response_dict)
# #   assert response_dict['success'] is True
# 
#     #package_create returns the created package as its result.
#     data_list = response_dict['result']
#     for pkg in data_list:
#         pprint.pprint(pkg)
# except Exception, e:
#     pass
# 
# # 
# for pkg in data_list :
#     
#     data_string = urllib.quote(json.dumps({'id': pkg['name']}))
#     try:
#         request = urllib2.Request(site_url + '/api/3/action/package_delete')
#         request.add_header('Authorization', api_key)
#         response = urllib2.urlopen(request, data_string)
#         assert response.code == 200
#          
#         response_dict = json.loads(response.read())
#         assert response_dict['success'] is True
#     except Exception:
#         pass
#      
#     for resource in pkg['resources'] :
#          
#         data_string = urllib.quote(json.dumps({'id': resource['id']}))
#         try:
#             request = urllib2.Request(site_url + '/api/3/action/resource_delete')
#             request.add_header('Authorization', api_key)
#             response = urllib2.urlopen(request, data_string)
#             assert response.code == 200
#          
#             response_dict = json.loads(response.read())
#             assert response_dict['success'] is True
#         except Exception:
#             pass
    