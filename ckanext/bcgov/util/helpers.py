# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
import pprint
import logging
import ckan.lib.helpers
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
from ckan.common import  (c, request)
from webhelpers.html import literal
import json
import urllib2
import ckan.lib.base as base
import pylons.config as config

import ckanext.bcgov
from ckanext.bcgov.version import version
from ckanext.bcgov.util.git import get_short_commit_id

NotFound = logic.NotFound
get_action = logic.get_action
snippet = ckan.lib.helpers.snippet
url_for = ckan.lib.helpers.url_for

log = logging.getLogger('ckanext.bcgov')

abort = base.abort


from ckan.lib.helpers import unselected_facet_items

def get_suborgs(org_id):
    '''
    Returns the list of suborganizations of the given organization
    '''
    context = {'model': model, 'session':model.Session, 'user':c.user}

    org_model = context['model']

    group = org_model.Group.get(org_id)
    branches = group.get_children_groups(type="organization")

    suborgs = [branch.id for branch in branches]

    return suborgs

def get_suborg_sector(sub_org_id):
    '''
    Returns the sector that the sub_org with the input sub_org id belongs to.
    '''
    context = {'model': model, 'session':model.Session, 'user':c.user}

    data_dict = {
                 'id' : sub_org_id,
                 'include_datasets' : False
                 }

    sub_org = get_action('organization_show')(context, data_dict)
    return sub_org.get('sector')


def get_user_dataset_num(userobj):
    from ckan.lib.base import model
    from ckan.lib.search import SearchError
    from ckanext.bcgov.util.util import get_user_orgs

    user_id = userobj.id

    #If this is the sysadmin user then return don't filter any dataset
    if userobj.sysadmin == True:
        fq = ''
    else :
        #Include only datsset created by this user or those from the orgs that the user has the admin role.
        fq = ' +(edc_state:("PUBLISHED" OR "PENDING ARCHIVE")'

        user_orgs = ['"' + org.id + '"' for org in get_user_orgs(user_id, 'admin')]
        user_orgs += ['"' + org.id + '"' for org in get_user_orgs(user_id, 'editor')]
        if len(user_orgs) > 0:
            fq += ' OR owner_org:(' + ' OR '.join(user_orgs) + ')'
        fq += ')'
    try:
        # package search
        context = {'model': model, 'session': model.Session,
                       'user': user_id}
        data_dict = {
                'q':'',
                'fq':fq,
                'facet':'false',
                'rows':0,
                'start':0,
        }
        query = toolkit.get_action('package_search')(context,data_dict)
        count = query['count']
    except SearchError, se:
        log.error('Search error: %s', se)
        count = 0

    return count

def get_index(seq, attr, value):
    return next(index for (index, d) in enumerate(seq) if d[attr] == value)

def record_is_viewable(pkg_dict, userobj):
    '''
    Checks if the user is authorized to view the dataset.
    Public users can only see published or pending archive records and only if the metadata-visibility is public.
    Government users who are not admins or editors can only see the published or pending  archive records.
    Editors and admins can see all the records of their organizations in addition to what government users can see.
    '''

    from ckanext.bcgov.util.util import get_user_orgs

    #Sysadmin can view all records
    if userobj and userobj.sysadmin == True :
        return True

    #Anonymous user (visitor) can only view published public records
    published_state = ['PUBLISHED', 'PENDING ARCHIVE']

    if pkg_dict['metadata_visibility'] == 'Public' and pkg_dict['edc_state'] in published_state:
        return True
    if userobj  :
        if pkg_dict['metadata_visibility'] == 'IDIR' and pkg_dict['edc_state'] in published_state:
            return True
        user_orgs = [org.id for org in get_user_orgs(userobj.id, 'editor') ]
        user_orgs += [org.id for org in get_user_orgs(userobj.id, 'admin') ]
        if pkg_dict['owner_org'] in user_orgs:
            return True
    return False


def get_package_data(pkg_id):

    pkg_data = []
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}

    try:
        pkg_data = toolkit.get_action('package_show')(context, {'id' : pkg_id})
    except NotFound:
        pass

    return pkg_data

def get_license_data(license_id):
    '''
    Returns the license information for the given license id.
    '''
    context = {'model': model, 'session': model.Session,
               'user': c.user, 'auth_user_obj': c.userobj}
    license_list = []
    try:
        license_list = toolkit.get_action('license_list')(context)
    except NotFound:
        pass

    #Check if liocense with the given id isin the licenses list
    for edc_license in license_list :
        if edc_license['id'] == license_id :
            return edc_license

    #License not found
    return None

def is_license_open(license_id):
    '''
    Checks if the license with given id is an open license.
    '''
    edc_license = get_license_data(license_id)

    if edc_license and edc_license['is_open'] == True :
        return True

    #License doesn't exist or it is not an open license
    return False

def get_record_type_label(rec_type):
    '''
    Used by search template as the label-function to show the proper dataset type.
    It maps the stored dataset type value to the more readable dataset type.
    '''
    type_dict = { 'Dataset' : 'Dataset', 'Geographic' : 'Geographic Dataset', 'Application' : 'Application', 'WebService' : 'Web Service / API'}

    if rec_type in type_dict :
        return type_dict[rec_type]
    return rec_type



###################################################
#
## JER - Aug. 15, 2014.
#    The two functions below are related to JIRA CITZEDC-296 - Turn off Gravatar
#    Greg had concerns about email being passed to Gravatar, but it turns out
#    that a hash of the email is being sent, so he is ok with that for now...
#    So these two functions are not being used.
#
###################################################

def edc_linked_gravatar(email_hash, size=100, default=None):
    return literal(
        '<a href="https://gravatar.com/" target="_blank" ' +
        'title="%s" alt="">' % _('Update your avatar at gravatar.com') +
        'monsterid</a>' % edc_gravatar(email_hash, size)
    )

def edc_gravatar(email_hash, size=100, default=None):
    return literal('''<img src="//gravatar.com/avatar/?s=%d&amp;d=monsterid"
        class="gravatar" width="%s" height="%s" />'''
                   % (size, size, size)
                   )


def get_facets_unselected(facet, limit=None):
    '''Return the list of unselected facet items for the given facet, sorted
    by count.

    Reads the complete list of facet items for the given facet from
    c.search_facets, and filters out the facet items that the user has already
    selected.

    Arguments:
    facet -- the name of the facet to filter.
    limit -- the max. number of facet items to return.
    exclude_active -- only return unselected facets.

    '''
    if not c.search_facets or \
            not c.search_facets.get(facet) or \
            not c.search_facets.get(facet).get('items'):
        return []
    facets = []
    for facet_item in c.search_facets.get(facet)['items']:
        if not len(facet_item['name'].strip()):
            continue
        if not (facet, facet_item['name']) in request.params.items():
            facets.append(dict(active=False, **facet_item))
    facets = sorted(facets, key=lambda item: item['count'], reverse=True)
    return facets

def get_facets_selected(facet):
    '''
    Returns the list of selected facet items for the given facet, sorted
    by count.
    '''
    if not c.search_facets or \
            not c.search_facets.get(facet) or \
            not c.search_facets.get(facet).get('items'):
        return []
    facets = []
    for facet_item in c.search_facets.get(facet)['items']:
        if not len(facet_item['name'].strip()):
            continue
        if (facet, facet_item['name']) in request.params.items():
            facets.append(dict(active=False, **facet_item))
    facets = sorted(facets, key=lambda item: item['count'], reverse=True)
    return facets


def get_sectors_list():
    '''
    Returns a list of sectors available in the file specified by sectors_file_url in ini file.
    The list of sectors are used when creating or editing a sub-organization
    in order to assign a new sector to the sub-organization.
    '''
    from pylons import config

    #Get the url for the sectors file.
    sectors_url = config.get('sectors_file_url', None)
    if sectors_url :
        try:
            response = urllib2.urlopen(sectors_url)
            response_body = response.read()
        except Exception, inst:
            msg = "Couldn't access to sectors url %r: %s" % (sectors_url, inst)
            raise Exception, msg
        try:
            sectors_data = json.loads(response_body)
        except Exception, inst:
            msg = "Couldn't read response from sectors %r: %s" % (response_body, inst)
            log.error("Couldn't read response from sectors %r: %s" % (response_body, inst))
            raise Exception, inst
        sectors_list = sectors_data.get('sectors', [])
    else :
        '''
        Return the default sectors list
        '''
        sectors_list = ["Natural Resources", "Service", "Transportation", "Education", "Economy", "Social Services", "Health and Safety", "Justice", "Finance" ]

    return sectors_list


def get_dataset_type(id):
    '''
    Returns the dataset type for the dataset with given package id
    '''
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}
    try:
        pkg_dict = get_action('package_show')(context, {'id': id})
        return pkg_dict['type']
    except NotFound:
        abort(404, _('The dataset {id} could not be found.').format(id=id))


def get_organizations():
    '''
    Returns the list of top-level organizations (Organizations that don't have any parent organizations).
    '''
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}
    org_model = context['model']
    #Get the list of all groups of type "organization" that have no parents.
    top_level_orgs = org_model.Group.get_top_level_groups(type="organization")

    return top_level_orgs

def get_org_title(id):
    org = model.Group.get(id)
    if org :
        return org.title
    return None

def get_edc_org(id):
    return model.Group.get(id)

def get_organization_title(org_id):
    '''
    Returns the title of an organization with the given organization id.
    '''
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}

    try:
        orgs = get_action('organization_list')(context, {'all_fields': True})
    except NotFound:
        orgs = []
    for org in orgs:

        if org['id'] == org_id:
            return org['title']
    return None


def get_espg_id(espg_string):
    import re
    a = re.compile("_([0-9]+)")
    espg_id = a.findall(espg_string)
    return espg_id[0]


def get_iso_topic_values(iso_topic_str):
    '''
    Converts the comma separated iso topic tokens into a list of iso topic values.
    '''
    iso_topic_values = []
    if iso_topic_str :
        iso_topic_values = [item.strip() for item in  iso_topic_str.split(',')]

    return iso_topic_values

def get_eas_login_url():
    '''Return the value of the eas login url config setting.



    '''
    value = config.get('edc.eas_url')

    return value

def get_fqdn():
    ''' Return the value of the edc_fdqn config setting '''

    value = config.get('edc.edc_fqdn')

    return value

def get_environment_name():
    ''' Return the value of the environment_name config setting '''
    # we seem to be using major_version for our environment name
    return config.get('edc.environment_name') or config.get('edc.major_version')

def get_version():
    ''' Return the value of the major_version config setting '''
    return version

_bcgov_commit_id = None

def get_bcgov_commit_id():
    '''Return the commit id corresponding to ckanext.bcgov'''
    global _bcgov_commit_id

    if _bcgov_commit_id is None:
        _bcgov_commit_id = get_short_commit_id(ckanext.bcgov.__path__[0])
        if _bcgov_commit_id is None:
            _bcgov_commit_id = 'unknown'

    return _bcgov_commit_id
