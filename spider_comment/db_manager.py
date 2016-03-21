# -*- coding: utf-8 -*-
import ConfigParser
import os
import time

import MySQLdb


class DbManager(object):
    def __init__(self):
        cf = ConfigParser.ConfigParser()
        path = os.path.dirname(os.path.abspath("db_config.ini"))
        path = path + "/db_config.ini"
        print "config file path: ", path
        cf.read(path)

        self.conn = MySQLdb.Connect(
            host=cf.get("baseconf", "host"),
            port=cf.getint("baseconf", "port"),
            user=cf.get("baseconf", "user"),
            passwd=cf.get("baseconf", "password"),
            db=cf.get("baseconf", "dbname"),
            charset='utf8'
        )

        self.cursor_items = self.conn.cursor()

        self.index = 0

    def getSkuidList(self):
        skuid_list = []
        # -------- 获取所有skuid --------
        sql_select_item = "select distinct skuid from spider_item "
        self.cursor_items.execute(sql_select_item)
        numrows = int(self.cursor_items.rowcount)
        for i in range(numrows):
            row = self.cursor_items.fetchone()
            skuid_list.append(row[0])  # 可能会爆
        # skuid_list = self.cursor_items.fetchall()
        return skuid_list

    def insert_comment(self, comment_info):
        sql = "insert into spider_comment" \
              "(commentid, skuid, platform, comment_content, comment_time, user_level_id, user_rovince, user_register_time, score,images) " \
              "values( '%s', '%s', 'jd', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
        sql = sql % (
            comment_info['id'],
            comment_info['referenceId'],
            comment_info['content'],
            comment_info['creationTime'],
            comment_info['userLevelId'],
            comment_info['userProvince'],
            comment_info['userRegisterTime'],
            comment_info['score'],
            comment_info['images']
        )
        # print sql
        self.cursor_items.execute(sql)

        self.index += 1
        if self.index >= 20:
            self.conn.commit()
            self.index = 0

    def commit_close(self):
        self.conn.commit()
        self.cursor_items.close()
        self.conn.close()
