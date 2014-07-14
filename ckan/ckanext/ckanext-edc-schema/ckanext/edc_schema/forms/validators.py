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
#           errKey = key[0] + '__' + str(key[1]) + '__' + key[2];
            errors[key].append(_('Missing value'))
            raise StopOnError

def license_not_empty(key, data, errors, content):

    value = data.get(key)

#    print value

    if(value == '0'):
        errors[key].append(_('License is not specified'))

def valid_email(key, data, errors, context):
    
    from validate_email import validate_email
        
    #Get the number of the key components
    key_length = len(key)

    #Check if the record is deleted in case of having a three field key (contacts, email, deleted)
    if key_length == 3:
        #Construct the delete key
        delete_key = (key[0], key[1], 'delete')
        delete_value = data.get(delete_key)
        if delete_value == '1':
            return

    contact_email = data.get(key)
    
    if (validate_email(contact_email)) :
        return
        
#     if len(email) > 7 :
#         if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
#             return

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
    
    date_value = data[key]
    if not date_value :
        return
    try:
        datetime.datetime.strptime(date_value, '%Y-%m-%d')
        
        #Check if this the published date
        if len(key) == 3 and key[0] == 'dates' :
            type_key = (key[0], key[1], 'type')
        
            date_type = data[type_key]
                    
            if date_type and date_type == '003':
                data['publish_date'] = date_value + 'T23:59:59Z'
#         if 'publish_date' in data:
#             print data['publish_date']
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
        if (key[0] == _('retention_expiry_date') or key[0] == _('source_data_path')):
            errors[key].append(_('Missing value. This field cannot be empty.'))
    else:
        ignore_missing(key, data, errors, context)


def get_org_sector(key, data, errors, context):
    '''
    This validator gets the value of sector based on the given values for org and suborg fields.
    '''
    from ckanext.edc_schema.plugin import get_organization_title
    from ckanext.edc_schema.util.helpers import get_suborg_sectors
    
    
    if key[0] != 'sector' :
        return
    
    org_key = ('org',)
    sub_org_key = ('sub_org',)
    if org_key in data and sub_org_key in data :
        org_title = get_organization_title(data[org_key])
        sub_org_title = get_organization_title(data[sub_org_key])
        
        sector = get_suborg_sectors(org_title, sub_org_title)
        if sector != [] :
            data[key] = sector[0]


def check_branch(key, data, errors, context):
    
    ignore_missing(key, data, errors, context)
    return
 
    from ckanext.edc_schema.util.util import get_organization_branches
    
    org_key = ('org',)
    
    org_id = None
    if org_key in data:
        org_id = data[org_key]
    
    #Check if the organization has any branches
    branches = get_organization_branches(org_id)
    
    if len(branches) > 0 :
        value = data.get(key)
        if not value or value is missing:
            errors[key].append(_('Missing value'))
            raise StopOnError



def duplicate_pkg(key, data, errors, context):
    '''
    Forces the user to change the name and title of a duplicated record.
    '''
    name_key = ('name',)
    title_key = ('title',)
    
    pkg_name = data[name_key]
    pkg_title = data[title_key]
    
    #Check if the duplicate title has not been changed
    if key[0] == 'title' and pkg_title.startswith('#Duplicate#') :
        errors[title_key].append(_('The duplicated title must be changed.'))
    
    #Check if the duplicated name has not been changed.
    if key[0] == 'name' and pkg_name.startswith('__duplicate__') :
        errors[name_key].append(_('A new name must be given for the duplicated record.'))
