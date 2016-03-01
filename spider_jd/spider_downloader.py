import urllib2


class SpiderDownloader(object):

    def get_html_cont(self, url):
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0')
        response = urllib2.urlopen(request)
        if response.getcode() != 200:
            return None
        return response.read()