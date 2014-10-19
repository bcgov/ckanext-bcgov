import os
from nose.tools import assert_equal
from ckanext.ga_report.ga_auth import (init_service, get_profile_id)

class TestAuth:

    @classmethod
    def setup_class(cls):
        if not os.path.exists("token.dat") or not os.path.exists("credentials.json"):
            print '*' * 60
            print "Tests may not run without first having run the auth process"
            print '*' * 60

    @classmethod
    def teardown_class(cls):
        pass

    def test_init(self):
        try:
            res = init_service(None, None)
            assert False, "Init service worked without credentials or tokens"
        except TypeError:
            pass

    def test_init_with_token(self):
        res = init_service("token.dat", None)
        assert res is not None, "Init service worked without credentials"

    def test_init_with_token_and_credentials(self):
        res = init_service("token.dat", "credentials.json")
        assert res is not None, "Unable to create service with valid details"

    def test_init_with_redentials(self):
        #res = init_service("", "credentials.json")
        # Triggers the auth flow via the browser
        pass

    def test_get_profile(self):
        svc = init_service("token.dat", "credentials.json")
        profile = get_profile_id(svc)
        assert profile is not None, "Unable to find a profile given configured UA id and user details"