import os
import sys
import json

import urllib2
import urllib

import pprint
import logging


site_url = 'http://delivery.apps.gov.bc.ca/pub/edc'
api_key = '400816c7-5be1-4d06-b878-1e6a3abad2b9'
#site_url = 'http://edc.highwaythreesolutions.com/'
#api_key = '1c4203c7-f54b-4424-9024-a66d700f3418'
#site_url = 'http://localhost:5000'
#api_key = 'cfb2cac5-4528-4c64-a2ac-271fddffb20b'

default_data_dir = os.path.dirname(os.path.abspath(__file__))
default_org_file =   default_data_dir + '/../../../data/orgs.json'
default_vocab_file = default_data_dir + '/../../../data/edc-vocabs.json'



def create_tag(vocab, tag):
    tag_dict = {'name': tag['id'] + '__' + tag['name'],
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


def create_vocab(vocab_name, tags):
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
        print "Error---------------> ", str(e)
        return None

    if not vocab:
        return None

    for tag in tags:
        create_tag(vocab, tag)

    return vocab


def create_org(org_dict):

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
            print "Error---------------> ", str(e)
            pprint.pprint(response_dict)
            pass
    return org


def edc_package_create(edc_record):
    import ckan.logic as logic

#    package_info = None

    data_string = urllib.quote(json.dumps(edc_record))

    try:
        request = urllib2.Request(site_url + '/api/3/action/package_create')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        # Use the json module to load CKAN's response into a dictionary.
        response_dict = json.loads(response.read())
#        pprint.pprint(response_dict)
#        assert response_dict['success'] is True

        #package_create returns the created package as its result.
#        package_info = response_dict['result']
    except Exception, e:
        pass
    return response_dict


