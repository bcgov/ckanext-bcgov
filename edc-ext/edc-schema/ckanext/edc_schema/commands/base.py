import os
import sys
import json

import urllib2
import urllib

import pprint
import logging


site_url = 'http://edc.highwaythreesolutions.com/'
api_key = '77f620cb-e98b-4195-91a6-b0e50812d240'

#site_url = 'http://localhost:5000'
#api_key = 'ecc41117-7a38-470a-86ce-adbfac08a5a2'

env_name = 'local'

default_data_dir = os.path.dirname(os.path.abspath(__file__))
default_org_file =   default_data_dir + '/../../../data/orgs.json'
default_vocab_file = default_data_dir + '/../../../data/edc-vocabs.json'


def get_import_params():
    #Get import parameters first 
    import_dict = {}   
    print 'Please provide import parameters (Site url, admin user, api_key ). '
    import_dict['site_url'] = raw_input("Site url (http://localhost:5000): ") or 'http://localhost:5000'
    import_dict['admin_user'] = raw_input('Admin username : ')
    import_dict['api_key'] = raw_input('Admin api_key : ')
    
    return import_dict
    

def create_tag(vocab, tag, site_url, api_key):
    tag_dict = {'name': tag,
                'vocabulary_id': vocab['id']}
    data_string = urllib.quote(json.dumps(tag_dict))

    try:
        request = urllib2.Request(site_url + '/api/3/action/tag_create')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True
        new_tag = response_dict['result']
        print '\tTag {0} added to the vocabulary.'.format(new_tag['display_name'])
    except Exception:
        pass


def create_vocab(vocab_name, tags, site_url, api_key):
    data_string = urllib.quote(json.dumps({'name': vocab_name}))
    try:
        request = urllib2.Request(site_url + '/api/3/action/vocabulary_create')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        vocab = response_dict['result']
        print '{0} is added to the vocabularies'.format(vocab['name'])
    except Exception, e:
        print "Exception in creating vocabulary ", str(e)
        return None

    if not vocab:
        return None

    for tag in tags:
        create_tag(vocab, tag, site_url, api_key)

    return vocab


def create_org(org_dict, site_url, api_key):

    org = None
    data_string =  urllib.quote(json.dumps({'id' : org_dict['name'], 'include_datasets': False}))
    try :
        request = urllib2.Request(site_url + '/api/3/action/organization_show')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        org = response_dict['result']
    except Exception:
        pass

    if not org:
        data_string =  urllib.quote(json.dumps(org_dict))
        try :
            request = urllib2.Request(site_url + '/api/3/action/organization_create')
            request.add_header('Authorization', api_key)
            response = urllib2.urlopen(request, data_string)
            assert response.code == 200

            response_dict = json.loads(response.read())
            assert response_dict['success'] is True

            org = response_dict['result']
        except Exception, e:
            print "Exception in creating organiztion ", str(e)
            pass
    return org


def edc_package_create(edc_record, site_url, api_key):


    data_string = urllib.quote(json.dumps(edc_record))

    pkg_dict = None
    errors = None
    try:
        request = urllib2.Request(site_url + '/api/3/action/package_create')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        # Use the json module to load CKAN's response into a dictionary.
        response_dict = json.loads(response.read())
#        pprint.pprint(response_dict)
        if response_dict['success'] == True :
            pkg_dict = response_dict['result']
        else:
            errors = response_dict['error']
    except Exception, e:
        print str(e)
        pass
    return (pkg_dict, errors)


#Return the name of an organization with the given id
def get_organization_id(org_title, site_url, api_key):

    data_string = urllib.quote(json.dumps({'all_fields': True}))
    try:
        request = urllib2.Request(site_url + '/api/3/action/organization_list')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        # Use the json module to load CKAN's response into a dictionary.
        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        # package_create returns the created package as its result.
        orgs = response_dict['result']
    except:
        orgs = []

    for org in orgs:
        if org_title and org_title.startswith(org['title']) :
            return org['id']
    return None

def get_user_id(user_name, site_url, api_key):
    user_info = None
    data_string = urllib.quote(json.dumps({'id':user_name}))

    request = urllib2.Request(site_url + '/api/3/action/user_show')
    request.add_header('Authorization', api_key)
    try:
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        # Use the json module to load CKAN's response into a dictionary.
        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        # package_create returns the created package as its result.
        user_info = response_dict['result']

        return user_info['id']

    except Exception:
        return None

