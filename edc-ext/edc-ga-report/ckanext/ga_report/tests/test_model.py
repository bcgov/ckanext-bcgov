from nose.tools import assert_equal

from ckanext.ga_report.ga_model import _normalize_url

class TestNormalizeUrl:
    def test_normal(self):
        assert_equal(_normalize_url('http://data.gov.uk/dataset/weekly_fuel_prices'),
                     '/dataset/weekly_fuel_prices')

    def test_www_dot(self):
        assert_equal(_normalize_url('http://www.data.gov.uk/dataset/weekly_fuel_prices'),
                     '/dataset/weekly_fuel_prices')

    def test_https(self):
        assert_equal(_normalize_url('https://data.gov.uk/dataset/weekly_fuel_prices'),
                     '/dataset/weekly_fuel_prices')

