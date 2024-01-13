# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 
import logging
# from ckan.lib.base import BaseController
from ckan.model import Session, Package
# from ckan.lib.helpers import url_for
from ckan.plugins.toolkit import config, url_for, request, c, h
from flask.wrappers import Response
from flask import Blueprint
from ckan.lib.search import SearchError
# from pylons.decorators.cache import beaker_cache
import ckan.model as model
# import ckan.lib.helpers as h
import time
from ckan.logic import get_action, NotFound

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
GSA_SITEMAP_NS = "http://www.w3.org/1999/xhtml"


log = logging.getLogger('ckanext.edc_schema')



# class GsaSitemapController(BaseController):

def get_package_chunk(self, data_dict):
    '''
    Gets a chunk of at most 1000 records from the search results, the offset is
    specified by the start parameter in data_dict.
    '''

    
    context = {'model': model, 'user': c.user or c.author,
                    'auth_user_obj': c.userobj}
    
    try:
        query = get_action('package_search')(context, data_dict)
        count = query.get('count', 0)
        packages = query.get('results', [])
    except SearchError as se:
        log.error('Dataset search error in creating the package site map: %r', se.args)
        count = 0
        packages = []
    return count, packages

def get_packages_sitemap(self, packages, output_type='html'):
    
    site_map = ''
    
    for pkg in packages:
        if output_type == 'html' :            
            site_map += "<a href=\""+ config.get('ckan.site_url') + "/dataset/" + pkg['name'] + "\">" + pkg['name'] + "</a><br>"
        else:
            pkg_lastmod = url_for(controller='package', action="read", id = pkg['metadata_modified'])
            short_date = pkg_lastmod[9:-7] 
            escaped_date = short_date.replace("%3A",":")
            utc_date = escaped_date + '-07:00'
            site_map += "<url>"            
            site_map += "<loc>" + config.get('ckan.site_url') +  "/dataset/" + pkg['name'] + "</loc>"
            #output += "<lastmod>" + pkg_lastmod[9:-20] + "</lastmod>"
            site_map += "<lastmod>" + utc_date + "</lastmod>"
            site_map += "</url>"  
                    
    return site_map


def create_sitemap(self, output_type='html'):
    output = ''
    
    if (output_type != 'html') and (output_type != 'xml') :
        return output
    
    if output_type == 'html' :
        output = '<!DOCTYPE html><html><head><title>EDC Sitemap</title><META NAME=\"ROBOTS\" CONTENT=\"NOINDEX\"></head><body>'
    else :
        output = '<?xml version="1.0" encoding="UTF-8"?>'
        output += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    
    user_name = c.user or 'visitor'
    fq = ''    
    if user_name == 'visitor':
        fq += ' +publish_state:("PUBLISHED" OR "PENDING ARCHIVE") +metadata_visibility:("Public")'

    max_results = 1000000
    data_dict = {
            'fq': fq.strip(),
            'rows' : max_results,
            'start' : 0
    }

    '''
    Get the first chunk of records and add them to the sitemap.
    '''
    count, packages = self.get_package_chunk(data_dict)
    log.info('Site map records count : {0}'.format(count))
    output += self.get_packages_sitemap(packages, output_type)
    
    '''
    Count the number of remaining records.
    Read the records in chunks and add them to the site map util there are no more records.
    '''
    max_records = min(count, max_results)
    start = 1000
    remained = max_records - 1000
    while remained > 0 :
        data_dict['start'] = start
        data_dict['rows'] = min(remained, 1000)
        count, packages = self.get_package_chunk(data_dict)
        output += self.get_packages_sitemap(packages, output_type)    
        remained -= 1000
        start += 1000

    if output_type == 'html' :
        output += "</body></html>" 
    else :
        output += "</urlset>"    

    return output   
        
#    @beaker_cache(expire=3600*24, type="dbm", invalidate_on_startup=True)
def _render_gsa_sitemap(self):
    return self.create_sitemap('html')
    
def _render_xml_sitemap(self):
    
    Response.content_type = "text/xml"
    return self.create_sitemap('xml')

site_map_blueprint = Blueprint('site_map_blueprint', __name__)
@site_map_blueprint.route('/sitemap.html', endpoint='view')
def view(self):
    return self._render_gsa_sitemap()

@site_map_blueprint.route('/sitemap.xml', endpoint='read')
def read(self):
    return self._render_xml_sitemap()        
