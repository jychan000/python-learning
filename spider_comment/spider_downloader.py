#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib2
import time
# from pandas import json

import comment_manager


class SpiderDownloader:
    def __init__(self):
        self.connectManager = comment_manager.CommentManager()
        self.comment_id_set = set()

    def get_html_cont(self, url):
        # sec = random.randint(1, 4) # 随机延时1~4秒，防止被Ban
        # time.sleep(sec)
        # userAgent = random.choice(self.ua_list)
        userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0'
        request = urllib2.Request(url)
        request.add_header('User-Agent', userAgent)
        request.add_header('Host', 'club.jd.com')
        request.add_header('Referer', 'http://item.jd.com/0.html')
        response = urllib2.urlopen(request)
        if response.getcode() != 200:
            return None
        return response.read()

    def getComments(self, item_str):
        page = 0
        nextPage = True
        print 'crawing skuid:', item_str
        while (nextPage):
            # time.sleep(1)
            url = "http://club.jd.com/productpage/p-%s-s-0-t-3-p-%s.html" % (item_str, page)
            html_cont = self.get_html_cont(url).decode('GBK', 'ignore').encode('UTF-8')
            # sec = random.randint(1, 2) # 随机延时1~2秒，防止被Ban
            # time.sleep(sec)
            if html_cont == '':
                print 'sleep 8 seconds for url %s' % (url)
                # time.sleep(3)
                page = page + 1
                continue


            product_comments = json.loads(html_cont)
            comments = product_comments["comments"]
            if comments:
                # print page
                page = page + 1
                for comment in comments:
                    content = comment['content']
                    commentId = comment['id']
                    # 如果commentId存在说明该spu下已有该sku评论，已经入库，所以不处理
                    if commentId in self.comment_id_set:
                        continue
                    else:
                        self.comment_id_set.add(commentId)
                    # 简单过滤掉太短的评论
                    # if len(content) < 4:
                    #     continue
                    skuid = comment['referenceId']
                    try:
                        self.connectManager.insert_comment(comment)
                    except Exception as e:
                        print e
                        # 若commentid重复，说明数据库已存有该评论，自动跳过该sku
                        if 'Duplicate entry' in str(e):
                            return
                            # exstr = traceback.format_exc()
                            # print exstr
            else:
                nextPage = False
                # for k in self.comment_dictionary.keys():
                #     print 'keys:%s,length:%d' % (k, len(self.comment_dictionary[k]))
