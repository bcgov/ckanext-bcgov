# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
import ckan.plugins.toolkit as toolkit
from ckan.logic import get_action, NotFound

def get_tag_name(vocab_id, tag_id):
    '''Returns the name of a tag for a given vocabulary and tag id.
       Each EDC tag is a combination of three digits as tag id and tag name which are separated  by '__'
    '''
    try:
        #First get the list of all tags for the given vocabulary.
        tags = toolkit.get_action('tag_list')(
                data_dict={'vocabulary_id': vocab_id})
        #For each tag extract the 3-digit tag id and compare it with the given tag id.
        for tag in tags :
            if (tag[:3] == tag_id) :
                return tag[5:]
        #No tags exist with the given tag id.
        return None
    except toolkit.ObjectNotFound:
        #No vocabulary exist with the given vocabulary id.
        return None
    