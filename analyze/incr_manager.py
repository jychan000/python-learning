# -*- coding: utf-8 -*-
import ConfigParser

import MySQLdb


class IncrManager(object):

    def __init__(self):
        cf = ConfigParser.ConfigParser()
        cf.read("db_config.ini")

        self.conn = MySQLdb.Connect(
            host = cf.get("baseconf", "host"),
            port = cf.getint("baseconf", "port"),
            user = cf.get("baseconf", "user"),
            passwd = cf.get("baseconf", "password"),
            db = cf.get("baseconf", "dbname"),
            charset = 'utf8'
        )
        self.cursor_incr = self.conn.cursor()
        self.cursor_item = self.conn.cursor()

        self.count = 0

    def upsert_incr(self, skuid, comStrIncrs, priceIncrs):

        # 获取分类信息
        sql_item = "select category1, category2, category3, category4 from spider_item where skuid=%s " % (skuid)
        self.cursor_item.execute(sql_item)
        categorys = self.cursor_item.fetchone()
        if categorys is None:
            return False

        sql = "replace into analyze_comment_incr " \
              "(skuid, " \
              "incr_3h, incr_6h, incr_12h, incr_24h, incr_48h, incr_72h, " \
              "price_incr_1d, price_incr_2d, price_incr_3d, price_incr_7d, price_incr_10d, price_incr_15d, " \
              "category1, category2, category3, category4, upsert_time) " \
              "values ('%s', %s, %s, %s, %s, %s, %s, " \
              "%f, %f, %f, %f, %f, %f, " \
              "'%s', '%s', '%s', '%s', now()) "

        list_incrs = list()
        list_incrs.append(skuid)
        for ele in comStrIncrs:
            list_incrs.append(ele)
        for ele in priceIncrs:
            list_incrs.append(float(ele))
        for ele in categorys:
            list_incrs.append(ele)

        sql = sql % (tuple(list_incrs))
        self.cursor_incr.execute(sql)

        self.count += 1
        if self.count >= 20:
            self.conn.commit()
            self.count = 0
        return True

    def close(self):
        self.conn.commit()
        self.cursor_item.close()
        self.cursor_incr.close()
        self.conn.close()


