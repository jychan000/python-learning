#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib2
import traceback

from spider_comment import db_manager


class SpiderDownloader:
    def __init__(self):
        self.connectManager = db_manager.DbManager()
        self.comment_id_set = set()

    def get_html_cont(self, url):
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

    def isneedfilter(self, content):
        # 长度小于等于4个汉字
        if content is None or len(set(content)) <= 12:
            return True
        # 不含有中文
        # include_chinese = False
        # for ch in content.decode('utf-8'):
        #     if u'\u4e00' <= ch <= u'\u9fff':
        #         include_chinese = True
        #         break
        # if not include_chinese:
        #     return True
        return False

    def getComments(self, item_str):
        page = 0
        page_faild = 0

        nextPage = True
        # print 'crawing skuid:', item_str

        while (nextPage):
            url = "http://club.jd.com/productpage/p-%s-s-0-t-3-p-%s.html" % (item_str, page)
            html_cont = None
            try:
                html_cont = self.get_html_cont(url).decode('GBK', 'ignore').encode('UTF-8')
            except Exception as e:
                print "error SpiderDownloader.getComments(), url=", url
                print e
                exstr = traceback.format_exc()
                print exstr

            if (page - page_faild) >= 15 or page_faild > 20:
                break
            if html_cont is None:
                page += 1
                page_faild += 1
                continue

            product_comments = json.loads(html_cont)
            comments = product_comments["comments"]
            if comments:
                page += 1

                for comment in comments:
                    content = comment['content']
                    commentId = comment['id']
                    # 如果commentId存在说明该spu下已有该sku评论，已经入库，所以不处理
                    if commentId in self.comment_id_set:
                        continue
                    else:
                        images_str = ''
                        if 'images' in comment:
                            images = comment['images']
                            if images:
                                for image in images:
                                    del image['associateId']
                                    del image['productId']
                                    del image['available']
                                    del image['pin']
                                    del image['dealt']
                                    del image['imgTitle']
                                    del image['isMain']
                                    image['imgUrl'] = "http:" + str(image['imgUrl']).replace("s128x96", "s760x500", 1)
                                images_str = json.dumps(images)
                                # imageUrls = image['imgUrl'],';'
                        comment['images'] = images_str
                        self.comment_id_set.add(commentId)

                    # 初步过滤
                    if self.isneedfilter(content):
                        continue
                    try:
                        self.connectManager.insert_comment(comment)
                    except Exception as e:
                        print e
                        # exstr = traceback.format_exc()
                        # print exstr
                        # 若commentid重复，说明数据库已存有该评论，自动跳过该sku
                        if 'Duplicate entry' in str(e):
                            return
            else:
                nextPage = False
                # for k in self.comment_dictionary.keys():
                #     print 'keys:%s,length:%d' % (k, len(self.comment_dictionary[k]))
