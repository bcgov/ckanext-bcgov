import ckan.lib.base as base
import ckan.model as model
import ckan.logic as logic
import ckan.lib.render as lib_render
import datetime
import time

from ckan.common import _, c, response
from pylons import config

import pprint

get_action = logic.get_action
render = base.render

class RSSController(base.BaseController):

    def recent(self):

        context =  {
            'model': model,
            'session': model.Session,
            'user': c.user
        }

        data_dict = {
            'q' : '+metadata_visibility:Public',
            'fq': '+edc_state:("PUBLISHED" OR "PENDING ARCHIVE")',
            'start': 0,
            'rows': 50,
            'sort': 'publish_date desc, metadata_modified desc',
        }

        query = get_action('package_search')(context, data_dict)
        count = query['count']
        results = query['results']
        
        for result in results:
            if 'publish_date' in result:
                timestamp = time.mktime(datetime.datetime.strptime(result['publish_date'], "%Y-%m-%d").timetuple())
                result['publish_date'] = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%a, %d %b %Y %H:%M:%S PST')


        base_url = config.get('ckan.site_url')

        vars = { 'results': results, 'count': count, 'base_url': base_url }

        response.content_type = 'xml'

        return render('recent.html', extra_vars=vars)

