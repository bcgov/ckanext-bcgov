import logging
import ckan.lib.helpers
import ckan.lib.datapreview as datapreview
from ckanext.edc_schema.util.util import get_edc_tag_name

from ckan.common import (
    _,
)

snippet = ckan.lib.helpers.snippet
url_for = ckan.lib.helpers.url_for
log = logging.getLogger(__name__)

def resource_preview(resource, package):
    '''
    Returns a rendered snippet for a embedded resource preview.

    Depending on the type, different previews are loaded.
    This could be an img tag where the image is loaded directly or an iframe
    that embeds a web page, recline or a pdf preview.
    '''

    if not resource['url']:
        return snippet("dataviewer/snippets/no_preview.html",
                       resource_type=format_lower,
                       reason=_(u'The resource url is not specified.'))
    
    
    res_format = get_edc_tag_name('resource_format', resource['format']).lower()
    
    if res_format == 'spreadsheet-xls':
        format_lower = 'xls'
    elif res_format == 'spreadsheet-zip':
        format_lower = 'zip'
    elif res_format == 'delimited text-json':
        format_lower = 'json'
    elif res_format == 'delimited text-csv':
        format_lower = 'csv'
    elif res_format == 'delimited text-txt':
        format_lower = 'txt'
    elif res_format == 'geospatial pdf':
        format_lower = 'pdf'
    else :
        format_lower = res_format
         
    
    directly = False
    data_dict = {'resource': resource, 'package': package}

    if datapreview.get_preview_plugin(data_dict, return_first=True):
        url = url_for(controller='package', action='resource_datapreview',
                      resource_id=resource['id'], id=package['id'], qualified=True)
    elif format_lower in datapreview.direct():
        directly = True
        url = resource['url']
    elif format_lower in datapreview.loadable():
        url = resource['url']
    else:
        reason = None
        if format_lower:
            log.info(
                _(u'No preview handler for resource of type {0}'.format(
                    format_lower))
            )
        else:
            reason = _(u'The resource format is not specified.')
        return snippet("dataviewer/snippets/no_preview.html",
                       reason=reason,
                       resource_type=format_lower)

    return snippet("dataviewer/snippets/data_preview.html",
                   embed=directly,
                   resource_url=url,
                   raw_resource_url=resource.get('url'))
