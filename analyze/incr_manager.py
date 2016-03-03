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

        self.count = 0

    def upsert_incr(self, skuid_incrs):
        sql = "replace into analyze_comment_incr " \
              "(skuid, incr_3h, incr_6h, incr_12h, incr_24h, incr_48h, incr_72h, upsert_time) " \
              "values ('%s', %s, %s, %s, %s, %s, %s, now()) "
        sql = sql % (skuid_incrs)
        self.cursor_incr.execute(sql)

        self.count += 1
        if self.count >= 10:
            self.conn.commit()
            self.count = 0

    def close(self):
        self.conn.commit()
        self.cursor_incr.close()
        self.conn.close()


