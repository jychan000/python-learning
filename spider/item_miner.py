# -*- coding: utf-8 -*-
import json
import traceback

from spider.spider_downloader import SpiderDownloader

jd_1 = "http://diviner.jd.com/diviner?lid=19&lim=8&uuid=0&p=105000&sku=%s"


sw = {
    'jd':  lambda skuid: jd_1 % skuid,
    'tb':  lambda skuid: "unknow",
    'vip': lambda skuid: "unknow",
}

class itemMiner(object):

    def __init__(self):
        print "itemMiner.init()"

    def mining(self, item):
        if item is None:
            return None

        platform, skuid = item.split("_")
        if platform is None or skuid is None:
            print "unknow paltform or skuid"
            return None

        url = sw[platform](skuid)
        if url is None or url == "unknow":
            return None

        new_items = set()
        try:
            html_cont = SpiderDownloader.get_html_cont(url).decode('gbk', 'ignore')
            obj_items = json.loads(html_cont)
            for datae in obj_items['data']:
                new_items.add(platform + "_" + str(datae['sku']))
        except Exception as e:
            print "itemMiner mining faild."
            print e
            exstr = traceback.format_exc()
            print exstr
            new_items = None

        return new_items


