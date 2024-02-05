# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
import json
import urllib.request, urllib.error, urllib.parse

from .base import (site_url, api_key)


def delete_vocabs():

    print('Deleting all vocabularies ....')
    # Get the list of all vocabs

    vocabs_list = []
    try:
        request = urllib.request.Request(site_url + '/api/3/action/vocabulary_list')
        response = urllib.request.urlopen(request)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        vocabs_list = response_dict['result']
    except Exception:
        pass

    for vocab in vocabs_list:
        try:
            # Deleting all tags of the current vocab
            for tag in vocab.get('tags'):
                data_string = urllib.parse.quote(json.dumps({'id' : tag['id'], 'vocabulary_id': vocab['id']}))
                request = urllib.request.Request(site_url + '/api/3/action/tag_delete')
                request.add_header('Authorization', api_key)
                response = urllib.request.urlopen(request, data_string)
                assert response.code == 200
                response_dict = json.loads(response.read())
                assert response_dict['success'] is True

            # Deleting the vocabulary
            data_string = urllib.parse.quote(json.dumps({'id': vocab['id']}))
            request = urllib.request.Request(site_url + '/api/3/action/vocabulary_delete')
            request.add_header('Authorization', api_key)
            response = urllib.request.urlopen(request, data_string)
            assert response.code == 200
            response_dict = json.loads(response.read())
            assert response_dict['success'] is True

        except Exception:
            pass

    print('Done.')

delete_vocabs()