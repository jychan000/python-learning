import traceback
import urllib2


class SpiderDownloader(object):

    @staticmethod
    def get_html_cont(url):
        response = None
        try:
            request = urllib2.Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0')
            response = urllib2.urlopen(request)
            if response.getcode() != 200:
                return None
        except Exception as e:
            print e
            print "spider_downloader.SpiderDownloader.get_html_cont(url)"
            print url
        finally:
            if response is None or response.getcode() != 200:
                return None
            else:
                return response.read()