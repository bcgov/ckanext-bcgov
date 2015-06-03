# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
import os
import json
import urllib2
import urllib
import pprint

from ckanext.edc_schema.commands.base import site_url

REDIRECTION_FILE = './data//redirection_map.txt'
edc_site_url = site_url + "/"

#Get the list of all dataset through api

pkg_list = []
try :
    request = urllib2.Request(site_url + '/api/3/action/package_list')
    response = urllib2.urlopen(request)
    assert response.code == 200
            
    response_dict = json.loads(response.read())
    assert response_dict['success'] is True
    pkg_list = response_dict['result']
except Exception:
    pass

#Check if there are any records
if len(pkg_list) > 0 :
    
    #Create redirection mapping file
    map_file = open(REDIRECTION_FILE, 'w')    
    #For each record get the record details
    for pkg in pkg_list :
        pkg_dict = None
        try :
            pkg_string = urllib.quote(json.dumps({'id': pkg}))
            request = urllib2.Request(site_url + '/api/3/action/package_show')
            response = urllib2.urlopen(request, pkg_string)
            assert response.code == 200
        
            response_dict = json.loads(response.read())
            assert response_dict['success'] is True
            pkg_dict = response_dict['result']
        except Exception:
            pass
        
        if not pkg_dict :
            continue
        
        
        #Check if this is a discovery record
        if 'metastar_uid' in pkg_dict:
            recordUID = pkg_dict['metastar_uid']
        else:
            recordUID = None
            
        if recordUID :
            #Add the record mapping to the redirection file
            map_str = 'recordUID=' + recordUID + ' -> ' + edc_site_url + pkg_dict['id']
            map_file.write(map_str + '\n')
    
    #Close the redirection mapping file
else :
    print 'No Discovery records found in database'