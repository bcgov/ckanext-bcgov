import os
import logging
import datetime
import httplib
import collections
import requests
import json
from pylons import config
from ga_model import _normalize_url
import ga_model

#from ga_client import GA

log = logging.getLogger('ckanext.ga-report')

FORMAT_MONTH = '%Y-%m'
MIN_VIEWS = 50
MIN_VISITS = 20
MIN_DOWNLOADS = 10

class DownloadAnalytics(object):
    '''Downloads and stores analytics info'''

    def __init__(self, service=None, token=None, profile_id=None, delete_first=False,
                 skip_url_stats=False):
        self.period = config['ga-report.period']
        self.service = service
        self.profile_id = profile_id
        self.delete_first = delete_first
        self.skip_url_stats = skip_url_stats
        self.token = token

    def specific_month(self, date):
        import calendar

        first_of_this_month = datetime.datetime(date.year, date.month, 1)
        _, last_day_of_month = calendar.monthrange(int(date.year), int(date.month))
        last_of_this_month =  datetime.datetime(date.year, date.month, last_day_of_month)
        # if this is the latest month, note that it is only up until today
        now = datetime.datetime.now()
        if now.year == date.year and now.month == date.month:
            last_day_of_month = now.day
            last_of_this_month = now
        periods = ((date.strftime(FORMAT_MONTH),
                    last_day_of_month,
                    first_of_this_month, last_of_this_month),)
        self.download_and_store(periods)


    def latest(self):
        if self.period == 'monthly':
            # from first of this month to today
            now = datetime.datetime.now()
            first_of_this_month = datetime.datetime(now.year, now.month, 1)
            periods = ((now.strftime(FORMAT_MONTH),
                        now.day,
                        first_of_this_month, now),)
        else:
            raise NotImplementedError
        self.download_and_store(periods)


    def for_date(self, for_date):
        assert isinstance(for_date, datetime.datetime)
        periods = [] # (period_name, period_complete_day, start_date, end_date)
        if self.period == 'monthly':
            first_of_the_months_until_now = []
            year = for_date.year
            month = for_date.month
            now = datetime.datetime.now()
            first_of_this_month = datetime.datetime(now.year, now.month, 1)
            while True:
                first_of_the_month = datetime.datetime(year, month, 1)
                if first_of_the_month == first_of_this_month:
                    periods.append((now.strftime(FORMAT_MONTH),
                                    now.day,
                                    first_of_this_month, now))
                    break
                elif first_of_the_month < first_of_this_month:
                    in_the_next_month = first_of_the_month + datetime.timedelta(40)
                    last_of_the_month = datetime.datetime(in_the_next_month.year,
                                                           in_the_next_month.month, 1)\
                                                           - datetime.timedelta(1)
                    periods.append((now.strftime(FORMAT_MONTH), 0,
                                    first_of_the_month, last_of_the_month))
                else:
                    # first_of_the_month has got to the future somehow
                    break
                month += 1
                if month > 12:
                    year += 1
                    month = 1
        else:
            raise NotImplementedError
        self.download_and_store(periods)

    @staticmethod
    def get_full_period_name(period_name, period_complete_day):
        if period_complete_day:
            return period_name + ' (up to %ith)' % period_complete_day
        else:
            return period_name


    def download_and_store(self, periods):
        for period_name, period_complete_day, start_date, end_date in periods:
            log.info('Period "%s" (%s - %s)',
                     self.get_full_period_name(period_name, period_complete_day),
                     start_date.strftime('%Y-%m-%d'),
                     end_date.strftime('%Y-%m-%d'))

            if self.delete_first:
                log.info('Deleting existing Analytics for this period "%s"',
                         period_name)
                ga_model.delete(period_name)

            if not self.skip_url_stats:
                # Clean out old url data before storing the new
                ga_model.pre_update_url_stats(period_name)

                accountName = config.get('googleanalytics.account')

                log.info('Downloading analytics for dataset views')
                #data = self.download(start_date, end_date, '~/%s/dataset/[a-z0-9-_]+' % accountName)
                data = self.download(start_date, end_date, '~/dataset/[a-z0-9-_]+')
                
                log.info('Storing dataset views (%i rows)', len(data.get('url')))
                self.store(period_name, period_complete_day, data, )

                log.info('Downloading analytics for organization views')
                #data = self.download(start_date, end_date, '~/%s/publisher/[a-z0-9-_]+' % accountName)
                data = self.download(start_date, end_date, '~/organization/[a-z0-9-_]+')

                #log.info('Storing publisher views (%i rows)', len(data.get('url')))
                self.store(period_name, period_complete_day, data,)

                # Make sure the All records are correct.
                ga_model.post_update_url_stats()

                log.info('Associating datasets with their organization')
                ga_model.update_publisher_stats(period_name) # about 30 seconds.


            log.info('Downloading and storing analytics for site-wide stats')
            self.sitewide_stats( period_name, period_complete_day )

            log.info('Downloading and storing analytics for social networks')
            self.update_social_info(period_name, start_date, end_date)


    def update_social_info(self, period_name, start_date, end_date):
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')
        query = 'ga:hasSocialSourceReferral=~Yes$'
        metrics = 'ga:entrances'
        sort = '-ga:entrances'

        try:
            # Because of issues of invalid responses, we are going to make these requests
            # ourselves.
            headers = {'authorization': 'Bearer ' + self.token}

            args = dict(ids='ga:' + self.profile_id,
                       filters=query,
                       metrics=metrics,
                       sort=sort,
                       dimensions="ga:landingPagePath,ga:socialNetwork",
                       max_results=10000)

            args['start-date'] = start_date
            args['end-date'] = end_date

            results = self._get_json(args)
        except Exception, e:
            log.exception(e)
            results = dict(url=[])


        data = collections.defaultdict(list)
        rows = results.get('rows',[])
        for row in rows:
            #url = _normalize_url('http:/' + row[0])
            url = row[0]
            data[url].append( (row[1], int(row[2]),) )
        ga_model.update_social(period_name, data)


    def download(self, start_date, end_date, path=None):
        '''Get data from GA for a given time period'''
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')
        query = 'ga:pagePath=%s$' % path
        metrics = 'ga:pageviews, ga:visits'
        sort = '-ga:pageviews'

        # Supported query params at
        # https://developers.google.com/analytics/devguides/reporting/core/v3/reference
        try:
            args = {}
            args["sort"] = "-ga:pageviews"
            args["max-results"] = 100000
            args["dimensions"] = "ga:pagePath"
            args["start-date"] = start_date
            args["end-date"] = end_date
            args["metrics"] = metrics
            args["ids"] = "ga:" + self.profile_id
            args["filters"] = query
            args["alt"] = "json"

            results = self._get_json(args)
        
        except Exception, e:
            log.exception(e)
            return dict(url=[])
        log.info("profile id:")
        log.info(self.profile_id)
        log.info(results)
        log.info(self.profile_id)
        
        packages = []
        log.info("There are %d results" % results['totalResults'])
        for entry in results.get('rows'):
            (loc,pageviews,visits) = entry
            
            #url = _normalize_url('http:/' + loc) # strips off domain e.g. www.data.gov.uk or data.gov.uk
            url = loc 

            
            if not url.startswith('/dataset/') and not url.startswith('/organization/'):
                # filter out strays like:
                # /data/user/login?came_from=http://data.gov.uk/dataset/os-code-point-open
                # /403.html?page=/about&from=http://data.gov.uk/publisher/planning-inspectorate
                continue
            packages.append( (url, pageviews, visits,) ) # Temporary hack
        return dict(url=packages)

    def store(self, period_name, period_complete_day, data):
        if 'url' in data:
            ga_model.update_url_stats(period_name, period_complete_day, data['url'])

    def sitewide_stats(self, period_name, period_complete_day):
        import calendar
        year, month = period_name.split('-')
        _, last_day_of_month = calendar.monthrange(int(year), int(month))

        start_date = '%s-01' % period_name
        end_date = '%s-%s' % (period_name, last_day_of_month)
        funcs = ['_totals_stats', '_social_stats', '_os_stats',
                 '_locale_stats', '_browser_stats', '_mobile_stats', '_download_stats']
        for f in funcs:
            log.info('Downloading analytics for %s' % f.split('_')[1])
            getattr(self, f)(start_date, end_date, period_name, period_complete_day)

    def _get_results(self, result_data, f):
        data = {}
        for result in result_data:
            key = f(result)
            data[key] = data.get(key,0) + result[1]
        return data

    def _get_json(self, params, prev_fail=False):
        ga_token_filepath = os.path.expanduser(config.get('googleanalytics.token.filepath', ''))
        if not ga_token_filepath:
            print 'ERROR: In the CKAN config you need to specify the filepath of the ' \
                'Google Analytics token file under key: googleanalytics.token.filepath'
            return

        log.info("Trying to refresh our OAuth token")
        try:
            from ga_auth import init_service
            self.token, svc = init_service(ga_token_filepath, None)
            log.info("OAuth token refreshed")
        except Exception, auth_exception:
            log.error("Oauth refresh failed")
            log.exception(auth_exception)
            return

        try:
            headers = {'authorization': 'Bearer ' + self.token}
            r = requests.get("https://www.googleapis.com/analytics/v3/data/ga", params=params, headers=headers)
            if r.status_code != 200:
                log.info("STATUS: %s" % (r.status_code,))
                log.info("CONTENT: %s" % (r.content,))
                raise Exception("Request with params: %s failed" % params)

            return json.loads(r.content)
        except Exception, e:
            log.exception(e)

        return dict(url=[])

    def _totals_stats(self, start_date, end_date, period_name, period_complete_day):
        """ Fetches distinct totals, total pageviews etc """
        try:
            args = {}
            args["max-results"] = 100000
            args["start-date"] = start_date
            args["end-date"] = end_date
            args["ids"] = "ga:" + self.profile_id

            args["metrics"] = "ga:pageviews"
            args["sort"] = "-ga:pageviews"
            args["alt"] = "json"

            results = self._get_json(args)
        except Exception, e:
            log.exception(e)
            results = dict(url=[])

        result_data = results.get('rows')
        ga_model.update_sitewide_stats(period_name, "Totals", {'Total page views': result_data[0][0]},
            period_complete_day)

        try:
            # Because of issues of invalid responses, we are going to make these requests
            # ourselves.
            headers = {'authorization': 'Bearer ' + self.token}

            args = {}
            args["max-results"] = 100000
            args["start-date"] = start_date
            args["end-date"] = end_date
            args["ids"] = "ga:" + self.profile_id

            args["metrics"] = "ga:pageviewsPerVisit,ga:avgTimeOnSite,ga:percentNewVisits,ga:visits"
            args["alt"] = "json"

            results = self._get_json(args)
        except Exception, e:
            log.exception(e)
            results = dict(url=[])

        result_data = results.get('rows')
        data = {
            'Pages per visit': result_data[0][0],
            'Average time on site': result_data[0][1],
            'New visits': result_data[0][2],
            'Total visits': result_data[0][3],
        }
        ga_model.update_sitewide_stats(period_name, "Totals", data, period_complete_day)

        # Bounces from / or another configurable page.
        path = '/%s%s' % (config.get('googleanalytics.account'),
                          config.get('ga-report.bounce_url', '/'))
#        path = '/'

        try:
            # Because of issues of invalid responses, we are going to make these requests
            # ourselves.
            headers = {'authorization': 'Bearer ' + self.token}

            args = {}
            args["max-results"] = 100000
            args["start-date"] = start_date
            args["end-date"] = end_date
            args["ids"] = "ga:" + self.profile_id

            args["filters"] = 'ga:pagePath==%s' % (path,)
            args["dimensions"] = 'ga:pagePath'
            args["metrics"] = "ga:visitBounceRate"
            args["alt"] = "json"

            results = self._get_json(args)
        except Exception, e:
            log.exception(e)
            results = dict(url=[])

        result_data = results.get('rows')
        if not result_data or len(result_data) != 1:
            log.error('Could not pinpoint the bounces for path: %s. Got results: %r',
                      path, result_data)
            return
        results = result_data[0]
        bounces = float(results[1])
        # visitBounceRate is already a %
        log.info('Google reports visitBounceRate as %s', bounces)
        ga_model.update_sitewide_stats(period_name, "Totals", {'Bounce rate (home page)': float(bounces)},
            period_complete_day)


    def _locale_stats(self, start_date, end_date, period_name, period_complete_day):
        """ Fetches stats about language and country """

        try:
            # Because of issues of invalid responses, we are going to make these requests
            # ourselves.
            headers = {'authorization': 'Bearer ' + self.token}

            args = {}
            args["max-results"] = 100000
            args["start-date"] = start_date
            args["end-date"] = end_date
            args["ids"] = "ga:" + self.profile_id

            args["dimensions"] = "ga:language,ga:country"
            args["metrics"] = "ga:pageviews"
            args["sort"] = "-ga:pageviews"
            args["alt"] = "json"

            results = self._get_json(args)
        except Exception, e:
            log.exception(e)
            results = dict(url=[])

        result_data = results.get('rows')
        data = {}
        for result in result_data:
            data[result[0]] = data.get(result[0], 0) + int(result[2])
        self._filter_out_long_tail(data, MIN_VIEWS)
        ga_model.update_sitewide_stats(period_name, "Languages", data, period_complete_day)

        data = {}
        for result in result_data:
            data[result[1]] = data.get(result[1], 0) + int(result[2])
        self._filter_out_long_tail(data, MIN_VIEWS)
        ga_model.update_sitewide_stats(period_name, "Country", data, period_complete_day)


    def _download_stats(self, start_date, end_date, period_name, period_complete_day):
        """ Fetches stats about data downloads """
        import ckan.model as model

        data = {}

        try:
            # Because of issues of invalid responses, we are going to make these requests
            # ourselves.
            headers = {'authorization': 'Bearer ' + self.token}

            args = {}
            args["max-results"] = 100000
            args["start-date"] = start_date
            args["end-date"] = end_date
            args["ids"] = "ga:" + self.profile_id

            args["filters"] = 'ga:eventAction==download'
            args["dimensions"] = "ga:eventLabel"
            args["metrics"] = "ga:totalEvents"
            args["alt"] = "json"

            results = self._get_json(args)
        except Exception, e:
            log.exception(e)
            results = dict(url=[])

        result_data = results.get('rows')
        import pprint
        print "Download data: "
        pprint.pprint(result_data)
        if not result_data:
            # We may not have data for this time period, so we need to bail
            # early.
            log.info("There is no download data for this time period")
            return

        def process_result_data(result_data, cached=False):
            progress_total = len(result_data)
            progress_count = 0
            resources_not_matched = []
            for result in result_data:
                progress_count += 1
                if progress_count % 100 == 0:
                    log.debug('.. %d/%d done so far', progress_count, progress_total)

                url = result[0].strip()

                # Get package id associated with the resource that has this URL.
                q = model.Session.query(model.Resource)
                if cached:
                    r = q.filter(model.Resource.cache_url.like("%s%%" % url)).first()
                else:
                    r = q.filter(model.Resource.url.like("%s%%" % url)).first()

                package_name = r.resource_group.package.name if r else ""
                if package_name:
                    data[package_name] = data.get(package_name, 0) + int(result[1])
                else:
                    resources_not_matched.append(url)
                    continue
            if resources_not_matched:
                log.debug('Could not match %i or %i resource URLs to datasets. e.g. %r',
                          len(resources_not_matched), progress_total, resources_not_matched[:3])

        log.info('Associating downloads of resource URLs with their respective datasets')
        process_result_data(results.get('rows'))

        try:
            # Because of issues of invalid responses, we are going to make these requests
            # ourselves.
            headers = {'authorization': 'Bearer ' + self.token}

            args = dict( ids='ga:' + self.profile_id,
                         filters='ga:eventAction==download-cache',
                         metrics='ga:totalEvents',
                         sort='-ga:totalEvents',
                         dimensions="ga:eventLabel",
                         max_results=10000)
            args['start-date'] = start_date
            args['end-date'] = end_date

            results = self._get_json(args)
        except Exception, e:
            log.exception(e)
            results = dict(url=[])

        log.info('Associating downloads of cache resource URLs with their respective datasets')
        process_result_data(results.get('rows'), cached=False)

        self._filter_out_long_tail(data, MIN_DOWNLOADS)
        ga_model.update_sitewide_stats(period_name, "Downloads", data, period_complete_day)

    def _social_stats(self, start_date, end_date, period_name, period_complete_day):
        """ Finds out which social sites people are referred from """

        try:
            # Because of issues of invalid responses, we are going to make these requests
            # ourselves.
            headers = {'authorization': 'Bearer ' + self.token}

            args = dict( ids='ga:' + self.profile_id,
                         metrics='ga:pageviews',
                         sort='-ga:pageviews',
                         dimensions="ga:socialNetwork,ga:referralPath",
                         max_results=10000)
            args['start-date'] = start_date
            args['end-date'] = end_date

            results = self._get_json(args)
        except Exception, e:
            log.exception(e)
            results = dict(url=[])

        result_data = results.get('rows')
        data = {}
        for result in result_data:
            if not result[0] == '(not set)':
                data[result[0]] = data.get(result[0], 0) + int(result[2])
        self._filter_out_long_tail(data, 3)
        ga_model.update_sitewide_stats(period_name, "Social sources", data, period_complete_day)


    def _os_stats(self, start_date, end_date, period_name, period_complete_day):
        """ Operating system stats """
        try:
            # Because of issues of invalid responses, we are going to make these requests
            # ourselves.
            headers = {'authorization': 'Bearer ' + self.token}

            args = dict( ids='ga:' + self.profile_id,
                         metrics='ga:pageviews',
                         sort='-ga:pageviews',
                         dimensions="ga:operatingSystem,ga:operatingSystemVersion",
                         max_results=10000)
            args['start-date'] = start_date
            args['end-date'] = end_date

            results = self._get_json(args)
        except Exception, e:
            log.exception(e)
            results = dict(url=[])

        result_data = results.get('rows')
        data = {}
        for result in result_data:
            data[result[0]] = data.get(result[0], 0) + int(result[2])
        self._filter_out_long_tail(data, MIN_VIEWS)
        ga_model.update_sitewide_stats(period_name, "Operating Systems", data, period_complete_day)

        data = {}
        for result in result_data:
            if int(result[2]) >= MIN_VIEWS:
                key = "%s %s" % (result[0],result[1])
                data[key] = result[2]
        ga_model.update_sitewide_stats(period_name, "Operating Systems versions", data, period_complete_day)


    def _browser_stats(self, start_date, end_date, period_name, period_complete_day):
        """ Information about browsers and browser versions """

        try:
            # Because of issues of invalid responses, we are going to make these requests
            # ourselves.
            headers = {'authorization': 'Bearer ' + self.token}

            args = dict( ids='ga:' + self.profile_id,
                         metrics='ga:pageviews',
                         sort='-ga:pageviews',
                         dimensions="ga:browser,ga:browserVersion",
                         max_results=10000)

            args['start-date'] = start_date
            args['end-date'] = end_date

            results = self._get_json(args)
        except Exception, e:
            log.exception(e)
            results = dict(url=[])


        result_data = results.get('rows')
        # e.g. [u'Firefox', u'19.0', u'20']

        data = {}
        for result in result_data:
            data[result[0]] = data.get(result[0], 0) + int(result[2])
        self._filter_out_long_tail(data, MIN_VIEWS)
        ga_model.update_sitewide_stats(period_name, "Browsers", data, period_complete_day)

        data = {}
        for result in result_data:
            key = "%s %s" % (result[0], self._filter_browser_version(result[0], result[1]))
            data[key] = data.get(key, 0) + int(result[2])
        self._filter_out_long_tail(data, MIN_VIEWS)
        ga_model.update_sitewide_stats(period_name, "Browser versions", data, period_complete_day)

    @classmethod
    def _filter_browser_version(cls, browser, version_str):
        '''
        Simplifies a browser version string if it is detailed.
        i.e. groups together Firefox 3.5.1 and 3.5.2 to be just 3.
        This is helpful when viewing stats and good to protect privacy.
        '''
        ver = version_str
        parts = ver.split('.')
        if len(parts) > 1:
            if parts[1][0] == '0':
                ver = parts[0]
            else:
                ver = "%s" % (parts[0])
        # Special case complex version nums
        if browser in ['Safari', 'Android Browser']:
            ver = parts[0]
            if len(ver) > 2:
                num_hidden_digits = len(ver) - 2
                ver = ver[0] + ver[1] + 'X' * num_hidden_digits
        return ver

    def _mobile_stats(self, start_date, end_date, period_name, period_complete_day):
        """ Info about mobile devices """

        try:
            # Because of issues of invalid responses, we are going to make these requests
            # ourselves.
            headers = {'authorization': 'Bearer ' + self.token}

            args = dict( ids='ga:' + self.profile_id,
                         metrics='ga:pageviews',
                         sort='-ga:pageviews',
                         dimensions="ga:mobileDeviceBranding, ga:mobileDeviceInfo",
                         max_results=10000)
            args['start-date'] = start_date
            args['end-date'] = end_date

            results = self._get_json(args)
        except Exception, e:
            log.exception(e)
            results = dict(url=[])


        result_data = results.get('rows')
        
        if not result_data : return
        
        data = {}
        for result in result_data:
            data[result[0]] = data.get(result[0], 0) + int(result[2])
        self._filter_out_long_tail(data, MIN_VIEWS)
        ga_model.update_sitewide_stats(period_name, "Mobile brands", data, period_complete_day)

        data = {}
        for result in result_data:
            data[result[1]] = data.get(result[1], 0) + int(result[2])
        self._filter_out_long_tail(data, MIN_VIEWS)
        ga_model.update_sitewide_stats(period_name, "Mobile devices", data, period_complete_day)

    @classmethod
    def _filter_out_long_tail(cls, data, threshold=10):
        '''
        Given data which is a frequency distribution, filter out
        results which are below a threshold count. This is good to protect
        privacy.
        '''
        for key, value in data.items():
            if value < threshold:
                del data[key]
