# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
import os
import sys
import json
import urllib2
import urllib

from base import (default_vocab_file,
                  create_vocab,
                  create_tag,
                  site_url,
                  api_key)

def create_vocabs(vocab_file=None):
        
    vocab_file = default_vocab_file
    available_vocabs = []
         
    if not os.path.exists(vocab_file):
        print 'File {0} does not exists'.format(vocab_file)
        sys.exit(1)
             
    #Read vocabularies json file
    with open(vocab_file) as json_file:
        vocabs = json.loads(json_file.read())
        
    try:
        request = urllib2.Request(site_url + '/api/3/action/vocabulary_list')
        request.add_header('Authorization', api_key)
        response = urllib2.urlopen(request)
        assert response.code == 200
            
        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        available_vocabs = response_dict['result']
    except Exception:
        pass 
        
    available_vocab_names = [vocab['name'] for vocab in available_vocabs]
        #for each vocabulary defined in json file
    
    for vocab_item in vocabs :
        vocab_name = vocab_item['name']
        vocab_tags = vocab_item['tags']
            #check if the vocabulary exists :
        if not vocab_name in available_vocab_names:
                #Create the vocabulary 
                create_vocab(vocab_name, vocab_tags)
        else:
            print 'Vocabulary {0} already exists, checking for new tags ...'.format(vocab_name)
            data_string = urllib.quote(json.dumps({'id': vocab_name}))
            try:
                request = urllib2.Request(site_url + '/api/3/action/vocabulary_show')
                request.add_header('Authorization', api_key)
                response = urllib2.urlopen(request, data_string)
                assert response.code == 200
            
                response_dict = json.loads(response.read())
                assert response_dict['success'] is True

                vocab = response_dict['result']
            except Exception:
                pass 
                    
            if vocab: 
                available_tags = [tag['display_name'] for tag in vocab['tags']]
                #Add each tag that is not in the list of available tags
                for tag in vocab_tags:
                    if not tag in available_tags:
                        create_tag(vocab, tag)

create_vocabs()
