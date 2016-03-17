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
        sql_item = "select comment_count, price, category1, category2, category3, category4 from spider_item where skuid=%s " % (skuid)
        self.cursor_item.execute(sql_item)
        categorys = self.cursor_item.fetchone()
        if categorys is None:
            return False

        sql = "replace into analyze_comment_incr " \
              "(skuid, " \
              "incr_3h, incr_6h, incr_12h, incr_24h, incr_48h, incr_72h, " \
              "price_reduce_1d, price_reduce_2d, price_reduce_3d, price_reduce_7d, price_reduce_10d, price_reduce_15d, " \
              "comment_count, price, category1, category2, category3, category4, upsert_time) " \
              "values ('%s', %s, %s, %s, %s, %s, %s, " \
              "%f, %f, %f, %f, %f, %f, " \
              "%d, %f, '%s', '%s', '%s', '%s', now()) "

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

    def clean(self):
        self.conn.commit()

        self.cursor_clean = self.conn.cursor()
        sql_clean = "delete from analyze_comment_incr where category3 in ( " \
              "select category3 from " \
              "(select count(*) as category3_count, category3 from analyze_comment_incr group by category3 order by category3_count)b " \
              "where category3_count <=5 order by category3 desc) "

        rs_clean = self.cursor_clean.execute(sql_clean)
        self.conn.commit()
        self.cursor_clean.close()

        return rs_clean



