import re

import pprint

import ckan.lib.navl.dictization_functions as df
from ckan.common import _

from ckanext.edc_schema.util.util import (get_edc_tags, get_edc_tag_name)

missing = df.missing
StopOnError = df.StopOnError
Invalid = df.Invalid

from ckan.lib.navl.validators import ignore_missing

from ckan.logic.validators import url_validator

#+--------------------------------------------------------------------+
#|   This method checks if the field with given key has some value.   |
#|   The field belongs to a record of related fields with a delete    |
#|   field. If the value of delete field is 0 then record is active   |
#|   and should be validated. If the value of delete field is 1, it   |
#|   means that the record has been deleted and it won't be validated |
#|   Validation takes place only the record has not been deleted in   |
#|   form by user.                                                    |
#+--------------------------------------------------------------------+
def check_empty(key, data, errors, context):
    #Construct the delete key
    delete_key = (key[0], key[1], 'delete')

    #Check the value of delete field
    delete_value = data.get(delete_key)

    #Validate the fields only if the record is not deleted (value of delete field is 0).
    if (delete_value == '0'):
        value = data.get(key)
        if not value or value is missing:
#            errKey = key[0] + '__' + str(key[1]) + '__' + key[2];
            errors[key].append(_('Missing value'))
            raise StopOnError

def license_not_empty(key, data, errors, content):

    value = data.get(key)

    print value

    if(value == '0'):
        errors[key].append(_('License is not specified'))

def valid_email(key, data, errors, context):

    #Get the number of the key components
    key_length = len(key)

    #Check if the record is deleted in case of having a three field key (contacts, email, deleted)
    if key_length == 3:
        #Construct the delete key
        delete_key = (key[0], key[1], 'delete')
        delete_value = data.get(delete_key)
        if delete_value == '1':
            return

    email = data.get(key)
    if len(email) > 7 :
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return

    errors[key].append(_('Invalid email address'))


#+--------------------------------------------------------------------+
#|                   Check if the url provided is valid.              |
#+--------------------------------------------------------------------+
def valid_url(key, data, errors, context):
    from urlparse import urlparse

    url = data[key]

    urlObj = urlparse(url)

    if (urlObj.scheme == '' or urlObj.netloc == ''):
        errors[key].append(_('The url provided is invalid.'))

    pass

def validate_link(key, data, errors, context):
    link = data[key]
    if not link:
        return
    
    url_validator(key, data, errors, context)
    
def valid_date(key, data, errors, context):
    import datetime
#    print '------------------', key , '----------------------'
    date_value = data[key]
    if not date_value :
        return
    try:
        datetime.datetime.strptime(date_value, '%Y-%m-%d')
    except ValueError:
        errors[key].append('Invalid date format/value')
    pass

#+------------------------------------------------------------------------------------+
#|                                                                                    |
#| This method checks the value of fields that are depended on resource_status.       |
#|                                                                                    |
#+------------------------------------------------------------------------------------+

def check_resource_status(key, data, errors, context):
    #Get the current value of resource status
#    pprint.pprint(data)
    resource_status_key = (_('resource_status'),)
    resource_status_id = data[resource_status_key]
    resource_status = get_edc_tag_name('resource_status', resource_status_id)

    #Check if the field is empty when the value of resource_status is  obsolete and when the key is replacement_record).
    if (key[0] == _('replacement_record')):
        if (resource_status and resource_status == _('obsolete') and (not data[key])) :
            errors[key].append(_('The replacement record cannot be empty.'))
        else:
            ignore_missing(key, data, errors, context)
        return

    #Check if the field is empty when the value of resource_status is historicalArchive
    if (resource_status and resource_status == _('historicalArchive') and (not data[key])):
        errors[key].append(_('Missing value. This field cannot be empty.'))
    else:
        ignore_missing(key, data, errors, context)

