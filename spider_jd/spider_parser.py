# -*- coding: utf-8 -*-
import re

import unicodedata
from bs4 import BeautifulSoup
from pandas import json

from spider_jd import spider_downloader


class SpiderParser(object):

    def __init__(self):
        self.downloader = spider_downloader.SpiderDownloader() #用于下载商品信息并封装返回

    def _get_product_info(self, skuid, html_cont):
        soup = BeautifulSoup(html_cont, "html.parser")

        product_info = {}
        product_info['skuid'] = skuid

        # 商品名称
        product_name = soup.find("div", id="itemInfo").find("div", id="name").h1.string
        product_info['name'] = product_name

        # product_name2 = re.findall(r"name:(.+?),", soup.head.script.string)[0].encode('ascii','ignore').strip()
        # product_info['name2'] = product_name2

        # 1级分类
        category1 = soup.find('a', clstag='shangpin|keycount|product|mbNav-1')
        product_info['category1'] = category1.get_text()

        # 2级分类
        category2 = soup.find('a', clstag='shangpin|keycount|product|mbNav-2')
        product_info['category2'] = category2.get_text()

        # 3级分类
        category3 = soup.find('a', clstag='shangpin|keycount|product|mbNav-3')
        product_info['category3'] = category3.get_text()

        # 4级分类
        category4 = soup.find('a', clstag='shangpin|keycount|product|mbNav-4')
        product_info['category4'] = category4.get_text()

        #品牌id
        brand = re.findall(r"brand:(.+?),", soup.head.script.string)[0].encode('ascii','ignore').strip()
        product_info['brand'] = brand

        # 商品图片
        picture = re.findall(r"src: '(.+?)',", soup.head.script.string)[0]
        product_info['picture'] = picture

        # skuid2 = re.findall(r"skuid:(.+?),", soup.head.script.string)[0].encode('ascii','ignore').strip()
        # product_info['skuid2'] = skuid2

        # skuid3 = unicodedata.normalize('NFKD', re.findall(r"skuid:(.+?),", soup.head.script.string)[0]).encode('utf-8').strip()
        # product_info['skuid3'] = skuid3

        #skuidkey = re.findall(r"skuidkey:(.+?),", soup.head.script.string)[0].encode('ascii','ignore')
        #product_info['skuidkey'] = skuidkey


        return product_info

    def _get_product_price(self, html_cont_price):
        json_price = re.findall(r"\[(.+)\]", html_cont_price)[0]
        obj_price = json.loads(json_price)
        return obj_price

    def _get_product_comments(self, html_cont_comments):
        obj_comments = json.loads(html_cont_comments)
        return obj_comments

    def _get_re_see(self, html_re_see):
        #json_re_see = re.findall(r"jQuery.+?\((.+)\)", html_re_see)[0]
        obj_re_see = json.loads(html_re_see)
        return obj_re_see


    def _get_new_items(self, obj_re_see):
        new_items = set()
        for datae in obj_re_see['data']:
            new_items.add(datae['sku'])
        return new_items

    def parse(self, item):
        if item is None:
            return None

        item_str = str(item)
        url          = "http://item.jd.com/%s.html" % (item_str)
        url_price    = "http://p.3.cn/prices/get?skuid=J_" + item_str
        url_comments = "http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds=" + item_str
        url_re_see   = "http://diviner.jd.com/diviner?lid=19&lim=8&uuid=0&p=105000&sku=" + item_str

        html_cont          = self.downloader.get_html_cont(url).decode('gbk', 'ignore')
        html_cont_price    = self.downloader.get_html_cont(url_price)
        html_cont_comments = self.downloader.get_html_cont(url_comments)
        html_cont_re_see   = self.downloader.get_html_cont(url_re_see).decode('gbk', 'ignore')

        # print html_cont
        if html_cont is None:
            print "care! html_cont is None."

        product_info = self._get_product_info(item, html_cont)
        p_price = self._get_product_price(html_cont_price)
        p_comments = self._get_product_comments(html_cont_comments)
        p_re_see = self._get_re_see(html_cont_re_see)

        product_info['price_p'] = p_price['p'] # 现价
        product_info['price_m'] = p_price['m'] # 原价
        product_info['CommentsCount'] = p_comments['CommentsCount']  # 评价
        product_info['re_see_info'] = p_re_see #看了又看信息

        new_items = self._get_new_items(p_re_see)

        return new_items, product_info



