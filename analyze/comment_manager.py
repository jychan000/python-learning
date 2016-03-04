# -*- coding: utf-8 -*-
import ConfigParser
import os

import MySQLdb


class CommentManager(object):

    def __init__(self):
        print "CommentManager初始化"
        cf = ConfigParser.ConfigParser()
        path = os.path.dirname(os.path.abspath("db_config.ini"))
        path = path + "/db_config.ini"
        print "config file path: ", path
        cf.read(path)

        db_host = cf.get("baseconf", "host")
        db_port = cf.getint("baseconf", "port")
        db_user = cf.get("baseconf", "user")
        db_pwd = cf.get("baseconf", "password")
        db_name = cf.get("baseconf", "dbname")

        # s = cf.sections()
        # print s
        # o = cf.options("baseconf")
        # print o
        # v = cf.items("baseconf")
        # print v
        #生成新的配置文件,名为:config_file_path
        #cf.write(open("config_file_path", "w"))

        self.conn = MySQLdb.Connect(
            host = db_host,
            port = db_port,
            user = db_user,
            passwd = db_pwd,
            db = db_name,
            charset = 'utf8'
        )
        sql_select = "select * from spider_jd_comment order by skuid asc, crawl_time desc"
        self.cursor = self.conn.cursor()
        num = self.cursor.execute(sql_select)
        if num < 2:
            print "表[spider_jd_comment]无数据. num=%d" % (num)
            return

        self.rowcount = self.cursor.rowcount

        self.last_skuid = "0" #上一个skuid
        self.last_row = None
        self.last_comments = list()

        # -------- 用于删除 --------
        self.rm_count = 0
        self.cursor_rm = self.conn.cursor()

    def get_one_sku_comments(self):
        try:
            while self.cursor.rownumber < self.rowcount:
                row = self.cursor.fetchone()
                skuid = row[1]

                if skuid == self.last_skuid:
                    self.last_comments.append(row)
                    self.last_row = row
                else:
                    #出现新sku, 且不是第一条纪录, 返回上一个sku所有评论
                    if self.last_skuid == "0":
                        self.last_skuid = skuid #上一个skuid
                        self.last_row = row
                        self.last_comments.append(row)
                    else:
                        tmp_comments = self.last_comments

                        self.last_skuid = skuid
                        self.last_row = row
                        self.last_comments = list()
                        self.last_comments.append(row)

                        return tmp_comments

            self.last_row = None
            return self.last_comments

        except Exception as e:
            print e
        finally:
            pass


    def has_next_sku(self):
        #1.是否首次访问
        if self.last_skuid == "0" and self.rowcount >= 1:
            return True
        #2.是否有上次的纪录
        if self.last_row != None:
            return True
        return False

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
        self.cursor.close()
        self.conn.close()

    def test(self):
        print "test."








