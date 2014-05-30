import logging
import ckan.lib.helpers

snippet = ckan.lib.helpers.snippet
url_for = ckan.lib.helpers.url_for
log = logging.getLogger(__name__)
import ckan.plugins.toolkit as toolkit


def get_suborg_sectors(org, suborg):
    from ckanext.edc_schema.commands.base import default_org_file
    import os
    import json
    import sys
    
    sectors = []
    
    org_file = default_org_file
              
    if not os.path.exists(org_file):
        print 'File {0} does not exists'.format(org_file)
        sys.exit(1)
                                 
    #Read the organizations json file
    with open(org_file) as json_file:
        orgs = json.loads(json_file.read())
    
    branches = []                  
    #Create each organization and all of its branches if it is not in the list of available organizations
    for org_item in orgs:
        
        if org_item['title'] == org:
            branches = org_item['branches']
            break
    
    if branches != [] :                                             
        for branch in branches:
            if branch['title'] == suborg and 'sectors' in branch :
                sectors = branch["sectors"]
                break
    return sectors


def get_user_dataset_num(userobj):
    from ckan.lib.base import model
    from ckan.lib.search import SearchError
    from ckanext.edc_schema.util.util import (get_user_orgs)
    
    user_id = userobj.id
    
    #If this is the sysadmin user then return don't filter any dataset
    if userobj.sysadmin == True:
        fq = ''
    else :
        #Include only datsset created by this user or those from the orgs that the user has the admin role.
        fq = 'author:("%s")' %(user_id) 
        user_orgs = ['"' + org.id + '"' for org in get_user_orgs(user_id, 'admin')]
        if len(user_orgs) > 0:
            fq += ' OR owner_org:(' + ' OR '.join(user_orgs) + ')'
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
    