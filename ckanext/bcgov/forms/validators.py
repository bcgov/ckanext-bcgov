# Copyright  2015, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license

import re

import ckan.lib.navl.dictization_functions as df
from ckan.common import _

missing = df.missing
StopOnError = df.StopOnError
Invalid = df.Invalid

from ckan.lib.navl.validators import ignore_missing

from ckan.logic.validators import url_validator

import logging

log = logging.getLogger('ckanext.edc_schema')

def float_validator(key, data, errors, content):
    value = data.get(key, 0.0)

    if isinstance(value, int) :
        return float(value)

    if isinstance(value, float):
        return value
    try:
        if value.strip() == '':
            return None
        return float(value)
    except (AttributeError, ValueError), e:
        return None


def latitude_validator(key, data, errors, context):
    '''
    Checks if the given latitude value is a valid positive float number.
    '''

    value = float_validator(key, data, errors, context)

    if not value or value < 0.0 :
        errors[key].append("A positive float value must be given.")
        raise StopOnError

def longitude_validator(key, data, errors, context):
    '''
    Checks if the given longitude value is a valid negative float number.
    '''

    value = float_validator(key, data, errors, context)

    if not value or value > 0.0 :
        errors[key].append("A negative float value must be given.")
        raise StopOnError

def check_empty(key, data, errors, context):
    '''
    This method checks if the field with given key has some value.
    The field belongs to a record of related fields with a delete
    field. If the value of delete field is 0 then record is active
    and should be validated. If the value of delete field is 1, it
    means that the record has been deleted and it won't be validated
    Validation takes place only the record has not been deleted in
    form by user.
    '''
    #Construct the delete key
    delete_key = (key[0], key[1], 'delete')

    #Check the value of delete field
    delete_value = data.get(delete_key)

    #Validate the fields only if the record is not deleted (value of delete field is 0).
    if (delete_value == '0'):
        value = data.get(key)
        if not value or value is missing:
            errors[key].append(_('Missing value'))
            raise StopOnError

def license_not_empty(key, data, errors, content):

    value = data.get(key)

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

    errors[key].append(_('Invalid email address'))


def valid_url(key, data, errors, context):
    '''
     Checks if the url provided is valid.
    '''
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

    except ValueError:
        errors[key].append('Invalid date format/value')
    pass

def check_resource_status(key, data, errors, context):
    '''
    This method checks the value of fields that are depended on resource_status.
    '''
    #Get the current value of resource status
    resource_status_key = (_('resource_status'),)
    if resource_status_key in data :
        resource_status = data[resource_status_key]

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
    from ckanext.bcgov.util.helpers import get_suborg_sector


    if key[0] != 'sector' :
        return

    sub_org_key = ('sub_org',)
    if sub_org_key in data and data[sub_org_key]:
        sector = get_suborg_sector(data[sub_org_key])
        data[key] = sector


def check_branch(key, data, errors, context):

    ignore_missing(key, data, errors, context)
    return

    from ckanext.bcgov.util.util import get_organization_branches

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

def check_dashes(key, data, errors, context):
    ''' make sure dashes have space after them '''
    #Get the package title
    title = data[key]

    dashes = re.findall(r'\s+(?:-+\w+)+',title)

    if len(dashes) > 0:
        errors[key].append('Non-hyphenated dashes in Title must be followed by a space. Please change the title.')

    multiple_dashes = re.findall(r'\s+(?:-{2,})+',title)
    if len(multiple_dashes) > 0:
        errors[key].append('Multiple consecutive dashes are not allowed in Titles. Please change the title.')

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


def check_duplicates(key, data, errors, context):
    '''
    Checks if there are any packages with same title
    '''
    #Get the package title
    title = data[key]

    #Search for packages with the same title
    from ckan.logic import get_action
    from ckan.lib.search import SearchError
    try :
        data_dict = {
                     'q' : '"' + title + '"'
                     }

        #Use package_search to filter the list
        results = get_action('package_autocomplete')(context, data_dict)
    #    results = query['result']

        count = 0
        for record in results :
            record_title = record['title'].lower()
            if title.lower() == record_title :
                result_name = record['name']
                count = 1
                break
        #If this the same record that we are editing ignore the only record in search result
        id_key = ('name',)
        if count == 1 and id_key in data :
            if  result_name == data[id_key] :
                return
        if count > 0 :
            errors[key].append('Record title must be unique. Please change the title.')
            raise StopOnError
    except SearchError, se :
        return

def check_extension(key, data, errors, context):
    import os
    url_type_key = (key[0], key[1], 'url_type')

    url_type = data.get(url_type_key)

    if url_type != 'upload' :
        return
#    valid_formats = []
    res_url = data.get(key)
    if not res_url :
        errors[key].appned('Resource file/url is missing')
        raise StopOnError
    if res_url :
        res_format = os.path.splitext(res_url)[1]
        if not res_format :
            errors[key].append('Unknown resource extension. Please provide a file with a valid extension')
            raise StopOnError
