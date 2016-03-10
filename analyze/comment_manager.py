# -*- coding: utf-8 -*-
import ConfigParser
import os

import MySQLdb


class CommentManager(object):

    def __init__(self):
        cf = ConfigParser.ConfigParser()
        path = os.path.dirname(os.path.abspath("db_config.ini"))
        path = path + "/db_config.ini"
        print "config file path: ", path
        cf.read(path)

        self.conn = MySQLdb.Connect(
            host = cf.get("baseconf", "host"),
            port = cf.getint("baseconf", "port"),
            user = cf.get("baseconf", "user"),
            passwd = cf.get("baseconf", "password"),
            db = cf.get("baseconf", "dbname"),
            charset = 'utf8'
        )

        # -------- 先获取skuid再获取具体评论 --------
        sql_select_item = "select distinct skuid from spider_jd_comment "
        self.cursor_items = self.conn.cursor()
        num_items = self.cursor_items.execute(sql_select_item)

        # -------- 用于删除 --------
        self.rm_count = 0
        self.cursor_rm = self.conn.cursor()

        # -------- 不用重复new -------
        self.cursor_comments = self.conn.cursor()

        # -------- 用来缓存下n个comments 类型:Map(skuid, List<comment>)--------
        self.comment_cache = dict()
        if self.cursor_items.rownumber < self.cursor_items.rowcount:
            skuids = self.cursor_items.fetchmany(20) #一次缓存 10 个
            commentCache = self.__get_comments(skuids)
            self.comment_cache = commentCache


    def has_next(self):
        # return self.cursor_items.rownumber < self.cursor_items.rowcount
        return len(self.comment_cache) > 0

    def __get_comments(self, skuids):
        """
        skuids -> Map(skuid, List<comment>)
        """
        skuids_str = ""
        for skuid in skuids:
            skuids_str += (skuid[0] + ", ")
        skuids_str = skuids_str[:-2]

        sql_comments = "select * from spider_jd_comment where skuid in (%s) order by skuid asc, crawl_time desc " % skuids_str
        num_comments = self.cursor_comments.execute(sql_comments)
        if num_comments < 2:
            return None
        comments = self.cursor_comments.fetchall()

        commentCache = dict()
        for comment in comments:
            skuid = comment[1]

            skucomments = list()
            if commentCache.has_key(skuid):
                skucomments = commentCache[skuid]
            skucomments.append(comment)
            commentCache[skuid] = skucomments
        return commentCache


    def next_comments(self):
        """
        <type 'tuple'> [0]skuid, [1]comments
        """
        skucomments = self.comment_cache.popitem()#<type 'tuple'> [0]skuid, [1]comments
        if not self.has_next():
            if self.cursor_items.rownumber < self.cursor_items.rowcount:
                skuids = self.cursor_items.fetchmany(20) #一次缓存 10 个
                commentCache = self.__get_comments(skuids)
                self.comment_cache = commentCache
        return skucomments



            # skuid = self.cursor_items.fetchone()[0]
            # comments = None
            # try:
            #     comments = self.__get_comments_by_skuid(skuid)
            # except Exception as e:
            #     print e
            # finally:
            #     pass
            # return comments

    def rm_old_comment(self, sku_datetime):
        if sku_datetime == None or sku_datetime == "":
            pass
        sql_delete = "delete from spider_jd_comment where sku_datetime='%s'" % (sku_datetime)
        self.cursor_rm.execute(sql_delete)
        self.rm_count += 1
        if self.rm_count >= 10:
            self.conn.commit()

    def commit_close(self):
        self.conn.commit()
        self.cursor_comments.close()
        self.cursor_items.close()
        self.cursor_rm.close()
        self.conn.close()





