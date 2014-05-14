import logging

from ckan.common import   request, c

from ckan.lib.base import BaseController
from ckan.model import Session, Package
from ckan.lib.helpers import url_for
from pylons import config, response
from pylons.decorators.cache import beaker_cache
import ckan.model as model
import pprint 
from ckan.logic import get_action, NotFound

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
GSA_SITEMAP_NS = "http://www.w3.org/1999/xhtml"


log = logging.getLogger(__file__)



class GsaSitemapController(BaseController):

#    @beaker_cache(expire=3600*24, type="dbm", invalidate_on_startup=True)
    def _render_gsa_sitemap(self):
        context = {'model': model, 'user': c.user or c.author,
                       'auth_user_obj': c.userobj}
            
        output = '<!DOCTYPE html><html><head><title>EDC Sitemap</title><META NAME=\"ROBOTS\" CONTENT=\"NOINDEX\"></head><body>'
        pkgs = Session.query(Package).all() # 

        user_name = c.user or 'visitor'
        fq = ''    
        if user_name == 'visitor':
            fq += ' +edc_state:("PUBLISHED" OR "PENDING ARCHIVE" OR "ARCHIVED") +metadata_visibility:("002")'

        data_dict = {
                'fq': fq.strip(),
                'rows' : 10000,
                'start' : 0
        }

        query = get_action('package_search')(context, data_dict)
                
        for pkg in query['results']:
            pkg_url = url_for(controller='package', action="read", id = pkg['name'])            
            output += "<a href=\""+ config.get('ckan.site_url') + "/dataset/" + pkg['name'] + "\">" + pkg['name'] + "</a><br>"
        output += "</body></html>"    
        return output
        
    def _render_xml_sitemap(self):
        context = {'model': model, 'user': c.user or c.author,
                       'auth_user_obj': c.userobj}
            
        output = '<?xml version="1.0" encoding="UTF-8"?>'
        output += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        pkgs = Session.query(Package).all() # 

        user_name = c.user or 'visitor'
        fq = ''    
        if user_name == 'visitor':
            fq += ' +edc_state:("PUBLISHED" OR "PENDING ARCHIVE" OR "ARCHIVED") +metadata_visibility:("002")'

        data_dict = {
                'fq': fq.strip(),
                'rows' : 10000,
                'start' : 0
        }

        query = get_action('package_search')(context, data_dict)
                
        for pkg in query['results']:
            pkg_url = url_for(controller='package', action="read", id = pkg['name'])
            pkg_lastmod = url_for(controller='package', action="read", id = pkg['metadata_modified'])
            output += "<url>"            
            output += "<loc>" + config.get('ckan.site_url') +  "/dataset/" + pkg['name'] + "</loc>"
            output += "<lastmod>" + pkg_lastmod[9:-20] + "</lastmod>"
            output += "</url>"  
        output += "</urlset>"    
        response.content_type = "text/xml"
        return output        
    def view(self):
        return self._render_gsa_sitemap()
    def read(self):
        return self._render_xml_sitemap()        
