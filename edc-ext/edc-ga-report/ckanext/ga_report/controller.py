import re
import csv
import sys
import json
import logging
import operator
import collections
from ckan.lib.base import (BaseController, c, g, render, request, response, abort)

import sqlalchemy
from sqlalchemy import func, cast, Integer
import ckan.model as model
from ga_model import GA_Url, GA_Stat, GA_ReferralStat, GA_Publisher

log = logging.getLogger('ckanext.ga-report')

DOWNLOADS_AVAILABLE_FROM = '2012-12'

def _get_month_name(strdate):
    import calendar
    from time import strptime
    d = strptime(strdate, '%Y-%m')
    return '%s %s' % (calendar.month_name[d.tm_mon], d.tm_year)

def _get_unix_epoch(strdate):
    from time import strptime,mktime
    d = strptime(strdate, '%Y-%m')
    return int(mktime(d))

def _month_details(cls, stat_key=None):
    '''
    Returns a list of all the periods for which we have data, unfortunately
    knows too much about the type of the cls being passed as GA_Url has a
    more complex query

    This may need extending if we add a period_name to the stats
    '''
    months = []
    day = None

    q = model.Session.query(cls.period_name,cls.period_complete_day)\
        .filter(cls.period_name!='All').distinct(cls.period_name)
    if stat_key:
        q=  q.filter(cls.stat_name==stat_key)

    vals = q.order_by("period_name desc").all()

    if vals and vals[0][1]:
        day = int(vals[0][1])
        ordinal = 'th' if 11 <= day <= 13 \
            else {1:'st',2:'nd',3:'rd'}.get(day % 10, 'th')
        day = "{day}{ordinal}".format(day=day, ordinal=ordinal)

    for m in vals:
        months.append( (m[0], _get_month_name(m[0])))

    return months, day


class GaReport(BaseController):

    def csv(self, month):
        import csv

        q = model.Session.query(GA_Stat).filter(GA_Stat.stat_name!='Downloads')
        if month != 'all':
            q = q.filter(GA_Stat.period_name==month)
        entries = q.order_by('GA_Stat.period_name, GA_Stat.stat_name, GA_Stat.key').all()

        response.headers['Content-Type'] = "text/csv; charset=utf-8"
        response.headers['Content-Disposition'] = str('attachment; filename=stats_%s.csv' % (month,))

        writer = csv.writer(response)
        writer.writerow(["Period", "Statistic", "Key", "Value"])

        for entry in entries:
            writer.writerow([entry.period_name.encode('utf-8'),
                             entry.stat_name.encode('utf-8'),
                             entry.key.encode('utf-8'),
                             entry.value.encode('utf-8')])


    def index(self):

        # Get the month details by fetching distinct values and determining the
        # month names from the values.
        c.months, c.day = _month_details(GA_Stat)

        # Work out which month to show, based on query params of the first item
        c.month_desc = 'all months'
        c.month = request.params.get('month', '')
        if c.month:
            c.month_desc = ''.join([m[1] for m in c.months if m[0]==c.month])

        q = model.Session.query(GA_Stat).\
            filter(GA_Stat.stat_name=='Totals')
        if c.month:
            q = q.filter(GA_Stat.period_name==c.month)
        entries = q.order_by('ga_stat.key').all()

        def clean_key(key, val):
            if key in ['Average time on site', 'Pages per visit', 'New visits', 'Bounce rate (home page)']:
                val =  "%.2f" % round(float(val), 2)
                if key == 'Average time on site':
                    mins, secs = divmod(float(val), 60)
                    hours, mins = divmod(mins, 60)
                    val = '%02d:%02d:%02d (%s seconds) ' % (hours, mins, secs, val)
                if key in ['New visits','Bounce rate (home page)']:
                    val = "%s%%" % val
            if key in ['Total page views', 'Total visits']:
                val = int(val)

            return key, val

        # Query historic values for sparkline rendering
        sparkline_query = model.Session.query(GA_Stat)\
                .filter(GA_Stat.stat_name=='Totals')\
                .order_by(GA_Stat.period_name)
        sparkline_data = {}
        for x in sparkline_query:
            sparkline_data[x.key] = sparkline_data.get(x.key,[])
            key, val = clean_key(x.key,float(x.value))
            tooltip = '%s: %s' % (_get_month_name(x.period_name), val)
            sparkline_data[x.key].append( (tooltip,x.value) )
        # Trim the latest month, as it looks like a huge dropoff
        for key in sparkline_data:
            sparkline_data[key] = sparkline_data[key][:-1]

        c.global_totals = []
        if c.month:
            for e in entries:
                key, val = clean_key(e.key, e.value)
                sparkline = sparkline_data[e.key]
                c.global_totals.append((key, val, sparkline))
        else:
            d = collections.defaultdict(list)
            for e in entries:
                d[e.key].append(float(e.value))
            for k, v in d.iteritems():
                if k in ['Total page views', 'Total visits']:
                    v = sum(v)
                else:
                    v = float(sum(v))/float(len(v))
                sparkline = sparkline_data[k]
                key, val = clean_key(k,v)

                c.global_totals.append((key, val, sparkline))
        # Sort the global totals into a more pleasant order
        def sort_func(x):
            key = x[0]
            total_order = ['Total page views','Total visits','Pages per visit']
            if key in total_order:
                return total_order.index(key)
            return 999
        c.global_totals = sorted(c.global_totals, key=sort_func)

        keys = {
            'Browser versions': 'browser_versions',
            'Browsers': 'browsers',
            'Operating Systems versions': 'os_versions',
            'Operating Systems': 'os',
            'Social sources': 'social_networks',
            'Languages': 'languages',
            'Country': 'country'
        }

        def shorten_name(name, length=60):
            return (name[:length] + '..') if len(name) > 60 else name

        def fill_out_url(url):
            import urlparse
            return urlparse.urljoin(g.site_url, url)

        c.social_referrer_totals, c.social_referrers = [], []
        q = model.Session.query(GA_ReferralStat)
        q = q.filter(GA_ReferralStat.period_name==c.month) if c.month else q
        q = q.order_by('ga_referrer.count::int desc')
        for entry in q.all():
            c.social_referrers.append((shorten_name(entry.url), fill_out_url(entry.url),
                                       entry.source,entry.count))

        q = model.Session.query(GA_ReferralStat.url,
                                func.sum(GA_ReferralStat.count).label('count'))
        q = q.filter(GA_ReferralStat.period_name==c.month) if c.month else q
        q = q.order_by('count desc').group_by(GA_ReferralStat.url)
        for entry in q.all():
            c.social_referrer_totals.append((shorten_name(entry[0]), fill_out_url(entry[0]),'',
                                            entry[1]))

        for k, v in keys.iteritems():
            q = model.Session.query(GA_Stat).\
                filter(GA_Stat.stat_name==k).\
                order_by(GA_Stat.period_name)
            # Buffer the tabular data
            if c.month:
                entries = []
                q = q.filter(GA_Stat.period_name==c.month).\
                          order_by('ga_stat.value::int desc')
            d = collections.defaultdict(int)
            for e in q.all():
                d[e.key] += int(e.value)
            entries = []
            for key, val in d.iteritems():
                entries.append((key,val,))
            entries = sorted(entries, key=operator.itemgetter(1), reverse=True)

            # Run a query on all months to gather graph data
            graph_query = model.Session.query(GA_Stat).\
                filter(GA_Stat.stat_name==k).\
                order_by(GA_Stat.period_name)
            graph_dict = {}
            for stat in graph_query:
                graph_dict[ stat.key ] = graph_dict.get(stat.key,{
                    'name':stat.key,
                    'raw': {}
                    })
                graph_dict[ stat.key ]['raw'][stat.period_name] = float(stat.value)
            stats_in_table = [x[0] for x in entries]
            stats_not_in_table = set(graph_dict.keys()) - set(stats_in_table)
            stats = stats_in_table + sorted(list(stats_not_in_table))
            graph = [graph_dict[x] for x in stats]
            setattr(c, v+'_graph', json.dumps( _to_rickshaw(graph,percentageMode=True) ))

            # Get the total for each set of values and then set the value as
            # a percentage of the total
            if k == 'Social sources':
                total = sum([x for n,x,graph in c.global_totals if n == 'Total visits'])
            else:
                total = sum([num for _,num in entries])
            setattr(c, v, [(k,_percent(v,total)) for k,v in entries ])

        return render('ga_report/site/index.html')


class GaDatasetReport(BaseController):
    """
    Displays the pageview and visit count for datasets
    with options to filter by publisher and time period.
    """
    def publisher_csv(self, month):
        '''
        Returns a CSV of each publisher with the total number of dataset
        views & visits.
        '''
        c.month = month if not month == 'all' else ''
        response.headers['Content-Type'] = "text/csv; charset=utf-8"
        response.headers['Content-Disposition'] = str('attachment; filename=organizations_%s.csv' % (month,))

        writer = csv.writer(response)
        writer.writerow(["Publisher Title", "Publisher Name", "Views", "Visits", "Period Name"])

        top_publishers = _get_top_publishers(limit=None)

        for publisher,view,visit in top_publishers:
            writer.writerow([publisher.title.encode('utf-8'),
                             publisher.name.encode('utf-8'),
                             view,
                             visit,
                             month])

    def dataset_csv(self, id='all', month='all'):
        '''
        Returns a CSV with the number of views & visits for each dataset.

        :param id: A Publisher ID or None if you want for all
        :param month: The time period, or 'all'
        '''
        c.month = month if not month == 'all' else ''
        if id != 'all':
            c.publisher = model.Group.get(id)
            if not c.publisher:
                abort(404, 'An organization with that name could not be found')

        packages = self._get_packages(publisher=c.publisher, month=c.month)
        response.headers['Content-Type'] = "text/csv; charset=utf-8"
        response.headers['Content-Disposition'] = \
            str('attachment; filename=datasets_%s_%s.csv' % (c.publisher_name, month,))

        writer = csv.writer(response)
        writer.writerow(["Dataset Title", "Dataset Name", "Views", "Visits", "Resource downloads", "Period Name"])

        for package,view,visit,downloads in packages:
            writer.writerow([package.title.encode('utf-8'),
                             package.name.encode('utf-8'),
                             view,
                             visit,
                             downloads,
                             month])

    def publishers(self):
        '''A list of publishers and the number of views/visits for each'''

        # Get the month details by fetching distinct values and determining the
        # month names from the values.
        c.months, c.day = _month_details(GA_Url)

        # Work out which month to show, based on query params of the first item
        c.month = request.params.get('month', '')
        c.month_desc = 'all months'
        if c.month:
            c.month_desc = ''.join([m[1] for m in c.months if m[0]==c.month])

        c.top_publishers = _get_top_publishers()
        graph_data = _get_top_publishers_graph()
        c.top_publishers_graph = json.dumps( _to_rickshaw(graph_data) )

        x =  render('ga_report/publisher/index.html')

        return x

    def _get_packages(self, publisher=None, month='', count=-1):
        '''Returns the datasets in order of views'''
        have_download_data = True
        month = month or 'All'
        if month != 'All':
            have_download_data = month >= DOWNLOADS_AVAILABLE_FROM

        q = model.Session.query(GA_Url,model.Package)\
            .filter(model.Package.name==GA_Url.package_id)\
            .filter(GA_Url.url.like('/dataset/%'))
        if publisher:
            q = q.filter(GA_Url.department_id==publisher.name)
        q = q.filter(GA_Url.period_name==month)
        q = q.order_by('ga_url.pageviews::int desc')
        top_packages = []
        if count == -1:
            entries = q.all()
        else:
            entries = q.limit(count)

        for entry,package in entries:
            if package:
                # Downloads ....
                if have_download_data:
                    dls = model.Session.query(GA_Stat).\
                        filter(GA_Stat.stat_name=='Downloads').\
                        filter(GA_Stat.key==package.name)
                    if month != 'All':  # Fetch everything unless the month is specific
                        dls = dls.filter(GA_Stat.period_name==month)
                    downloads = 0
                    for x in dls:
                        downloads += int(x.value)
                else:
                    downloads = 'No data'
                top_packages.append((package, entry.pageviews, entry.visits, downloads))
            else:
                log.warning('Could not find package associated package')

        return top_packages

    def read(self):
        '''
        Lists the most popular datasets across all publishers
        '''
        return self.read_publisher(None)

    def read_publisher(self, id):
        '''
        Lists the most popular datasets for a publisher (or across all publishers)
        '''
        count = 20
        
        print 'ID : ', id

        c.publishers = _get_publishers()

        id = request.params.get('publisher', id)
        if id and id != 'all':
            c.publisher = model.Group.get(id)
            if not c.publisher:
                abort(404, 'An organization with that name could not be found')
            c.publisher_name = c.publisher.name
        c.top_packages = [] # package, dataset_views in c.top_packages

        # Get the month details by fetching distinct values and determining the
        # month names from the values.
        c.months, c.day = _month_details(GA_Url)

        # Work out which month to show, based on query params of the first item
        c.month = request.params.get('month', '')
        if not c.month:
            c.month_desc = 'all months'
        else:
            c.month_desc = ''.join([m[1] for m in c.months if m[0]==c.month])

        month = c.month or 'All'
        c.publisher_page_views = 0
        q = model.Session.query(GA_Url).\
            filter(GA_Url.url=='/organization/%s' % c.publisher_name)
        entry = q.filter(GA_Url.period_name==c.month).first()
        c.publisher_page_views = entry.pageviews if entry else 0

        c.top_packages = self._get_packages(publisher=c.publisher, count=20, month=c.month)

        # Graph query
        top_packages_all_time = self._get_packages(publisher=c.publisher, count=20, month='All')
        top_package_names = [ x[0].name for x in top_packages_all_time ]
        graph_query = model.Session.query(GA_Url,model.Package)\
            .filter(model.Package.name==GA_Url.package_id)\
            .filter(GA_Url.url.like('/dataset/%'))\
            .filter(GA_Url.package_id.in_(top_package_names))
        all_series = {}
        for entry,package in graph_query:
            if not package: continue
            if entry.period_name=='All': continue
            all_series[package.name] = all_series.get(package.name,{
                'name':package.title,
                'raw': {}
                })
            all_series[package.name]['raw'][entry.period_name] = int(entry.pageviews)
        graph = [ all_series[series_name] for series_name in top_package_names ]
        c.graph_data = json.dumps( _to_rickshaw(graph) )

        return render('ga_report/publisher/read.html')

def _to_rickshaw(data, percentageMode=False):
    import pprint
#    pprint.pprint(data)
    if data==[]:
        return data
    # x-axis is every month in c.months. Note that data might not exist
    # for entire history, eg. for recently-added datasets
    x_axis = [x[0] for x in c.months]
    x_axis.reverse() # Ascending order
    x_axis = x_axis[:-1] # Remove latest month
    totals = {}
    for series in data:
        series["data"] = []
        for x_string in x_axis:
            print "x_string   ", x_string
            x = _get_unix_epoch( x_string )
            y = series["raw"].get(x_string,0)
            series["data"].append({"x":x,"y":y})
            totals[x] = totals.get(x,0)+y
    pprint.pprint(series)
    if not percentageMode:
        return data
    # Turn all data into percentages
    # Roll insignificant series into a catch-all
    THRESHOLD = 1
    raw_data = data
    data = []
    for series in raw_data:
        for point in series["data"]:
            percentage = (100*float(point["y"])) / totals[point["x"]]
            if not (series in data) and percentage>THRESHOLD:
                data.append(series)
            point["y"] = percentage
    others = [ x for x in raw_data if not (x in data) ]
    if len(others):
        data_other = []
        for i in range(len(x_axis)):
            x = _get_unix_epoch(x_axis[i])
            y = 0
            for series in others:
                y += series["data"][i]["y"]
            data_other.append({"x":x,"y":y})
        data.append({
            "name":"Other",
            "data": data_other
            })
    return data


def _get_top_publishers(limit=20):
    '''
    Returns a list of the top 20 publishers by dataset visits.
    (The number to show can be varied with 'limit')
    '''
    month = c.month or 'All'
    connection = model.Session.connection()
    q = """
        select department_id, sum(pageviews::int) views, sum(visits::int) visits
        from ga_url
        where department_id <> ''
          and package_id <> ''
          and url like '/dataset/%%'
          and period_name=%s
        group by department_id order by views desc
        """
    if limit:
        q = q + " limit %s;" % (limit)

    top_publishers = []
    res = connection.execute(q, month)
    for row in res:
        g = model.Group.get(row[0])
        if g:
            top_publishers.append((g, row[1], row[2]))
    return top_publishers


def _get_top_publishers_graph(limit=20):
    '''
    Returns a list of the top 20 publishers by dataset visits.
    (The number to show can be varied with 'limit')
    '''
    connection = model.Session.connection()
    q = """
        select department_id, sum(pageviews::int) views
        from ga_url
        where department_id <> ''
          and package_id <> ''
          and url like '/dataset/%%'
          and period_name='All'
        group by department_id order by views desc
        """
    if limit:
        q = q + " limit %s;" % (limit)

    res = connection.execute(q)
    department_ids = [ row[0] for row in res ]

    # Query for a history graph of these department ids
    q = model.Session.query(
            GA_Url.department_id,
            GA_Url.period_name,
            func.sum(cast(GA_Url.pageviews,sqlalchemy.types.INT)))\
        .filter( GA_Url.department_id.in_(department_ids) )\
        .filter( GA_Url.url.like('/dataset/%') )\
        .filter( GA_Url.package_id!='' )\
        .group_by( GA_Url.department_id, GA_Url.period_name )
    graph_dict = {}
    for dept_id,period_name,views in q:
        graph_dict[dept_id] = graph_dict.get( dept_id, {
            'name' : model.Group.get(dept_id).title,
            'raw' : {}
            })
        graph_dict[dept_id]['raw'][period_name] = views
    return [ graph_dict[id] for id in department_ids ]


def _get_publishers():
    '''
    Returns a list of all publishers. Each item is a tuple:
      (name, title)
    '''
    publishers = []
    for pub in model.Session.query(model.Group).\
               filter(model.Group.type=='organization').\
               filter(model.Group.state=='active').\
               order_by(model.Group.name):
        publishers.append((pub.name, pub.title))
    return publishers

def _percent(num, total):
    p = 100 * float(num)/float(total)
    return "%.2f%%" % round(p, 2)
