import os
import datetime
from nose.tools import assert_equal
from ckanext.ga_report.download_analytics import DownloadAnalytics
from ckanext.ga_report.ga_auth import (init_service, get_profile_id)
from ckanext.ga_report.ga_model import init_tables

class TestAPI:

    @classmethod
    def setup_class(cls):
        if not os.path.exists("token.dat") or not os.path.exists("credentials.json"):
            print '*' * 60
            print "Tests may not run without first having run the auth process"
            print '*' * 60
        init_tables()

    @classmethod
    def teardown_class(cls):
        pass

    def test_latest(self):
        svc = init_service("token.dat", "credentials.json")
        try:
            downloader = DownloadAnalytics(svc, profile_id=get_profile_id(svc))
            downloader.latest()
        except Exception as e:
            assert False, e


    def test_since(self):
        svc = init_service("token.dat", "credentials.json")
        downloader = DownloadAnalytics(svc, profile_id=get_profile_id(svc))
        try:
            downloader.for_date(datetime.datetime.now() - datetime.timedelta(days=-30))
        except Exception as e:
            assert False, e
