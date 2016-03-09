# -*- coding: utf-8 -*-
import json
import traceback

from spider.config_center import ConfigCenter
from spider.spider_downloader import SpiderDownloader

class itemMiner(object):

    def __init__(self):
        pass

    def mining(self, item):
        platform, skuid = item.split("_")

        url = ConfigCenter.url_resee(item)
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


