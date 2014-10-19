from nose.tools import assert_equal

from ckanext.ga_report.download_analytics import DownloadAnalytics

_filter_browser_version = DownloadAnalytics._filter_browser_version

class TestBrowserVersionFilter:
    def test_chrome(self):
        assert_equal(_filter_browser_version('Chrome', u'6.0.472.0'), '6')
    def test_firefox(self):
        assert_equal(_filter_browser_version('Firefox', u'16.1'), '16')
    def test_safari(self):
        assert_equal(_filter_browser_version('Safari', u'534.55.3'), '53X')
        assert_equal(_filter_browser_version('Safari', u'1534.55.3'), '15XX')
    def test_ie(self):
        assert_equal(_filter_browser_version('Internet Explorer', u'8.0'), '8')
    def test_opera_mini(self):
        assert_equal(_filter_browser_version('Opera Mini', u'6.5.27431'), '6')
    def test_opera(self):
        assert_equal(_filter_browser_version('Opera', u'11.60'), '11')
        
class TestDownloadAnalytics:
    def test_filter_out_long_tail(self):
        data = {'Firefox': 100,
                'Obscure Browser': 5,
                'Chrome': 150}
        DownloadAnalytics._filter_out_long_tail(data, 10)
        assert_equal(data, {'Firefox': 100,
                            'Chrome': 150})
