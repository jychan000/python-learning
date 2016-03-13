import ConfigParser

url_homepage_jd = "http://item.jd.com/%s.html"
url_homepage_tb = ""
url_homepage_vip = ""

url_comment_jd = "http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds=%s"
url_comment_tb = ""
url_comment_vip = ""

url_price_jd = "http://p.3.cn/prices/get?skuid=J_%s"
url_price_tb = ""
url_price_vip = ""

#url_resee_jd = "http://diviner.jd.com/diviner?lid=19&lim=8&uuid=0&p=105000&sku=%s"
url_resee_jd = "http://diviner.jd.com/diviner?lid=19&lim=6&uuid=1047138762&pin=&p=102001&sku=%s&ck=pin,ipLocation,atw,aview&c1=1316&c2=1381&c3=1391"
url_resee_tb = ""
url_resee_vip = ""

sw_homepage = {
    'jd': lambda skuid: url_homepage_jd % skuid,
    'tb': lambda skuid: url_homepage_tb % skuid,
    'vip': lambda skuid: url_homepage_vip % skuid
}

sw_comment = {
    'jd': lambda skuid: url_comment_jd % skuid,
    'tb': lambda skuid: url_comment_tb % skuid,
    'vip': lambda skuid: url_comment_vip % skuid
}

sw_price = {
    'jd': lambda skuid: url_price_jd % skuid,
    'tb': lambda skuid: url_price_tb % skuid,
    'vip': lambda skuid: url_price_vip % skuid
}

sw_resee = {
    'jd': lambda skuid: url_resee_jd % skuid,
    'tb': lambda skuid: url_resee_tb % skuid,
    'vip': lambda skuid: url_resee_vip % skuid
}


class ConfigCenter(object):
    @staticmethod
    def geturl(sw, item):
        if item is None:
            return None

        platform, skuid = item.split("_")
        if platform is None or skuid is None:
            print "unknow paltform or skuid"
            return None

        url = None
        try:
            url = sw[platform](skuid)
            if url is None or url == "unknow":
                return None
        except Exception as e:
            url = None
        return url

    @staticmethod
    def url_homepage(item):
        return ConfigCenter.geturl(sw_homepage, item)

    @staticmethod
    def url_comment(item):
        return ConfigCenter.geturl(sw_comment, item)

    @staticmethod
    def url_price(item):
        return ConfigCenter.geturl(sw_price, item)

    @staticmethod
    def url_resee(item):
        return ConfigCenter.geturl(sw_resee, item)


def singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

@singleton
class SpiderConfig(object):

    def __init__(self):
        cf = ConfigParser.ConfigParser()
        cf.read("spider.ini")

        self.runtime = int(cf.get("baseconf", "runtime"))
        # self.firsttarget = int(cf.get("baseconf", "runtime"))

if __name__ == '__main__':
    c1 = SpiderConfig()
    c2 = SpiderConfig()
    print c1.runtime
    c1.a = 7
    print c2.runtime

