# -*- coding: utf-8 -*-
import ConfigParser

import MySQLdb
import time


class SpiderOutputer(object):

    def __init__(self):
        self.product_infos = []

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
        self.cursor = self.conn.cursor()

    def collect_data(self, product_info):
        if product_info is None:
            return
        self.product_infos.append(product_info)

    # 写入商品信息表
    def update_insert_item(self, data):
        sql = "replace into spider_jd_item(%s) " \
              "values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s, %s, %s, '%s', now(), %s)"
        sql_column = "skuid, platform, product_name, brand_id, " \
                     "category1, category2, category3, category4, " \
                     "price, price_cost, comment_count, picture, update_time, "

        # 看了又看的反馈数量不确定, 因此需要拼接sql
        resee_str = ""
        index = 1
        for resee_ele in data['re_see_info']['data']:
            sql_column += ("re_see_skuid" + str(index) + ", ")
            resee_str += ("'" + str(resee_ele['sku']) + "', ")
            index += 1

        sql_column = sql_column[:-2]
        resee_str = resee_str[:-2]
        sql = sql % (
            sql_column,
            data['skuid'], data['platform'], data['name'], data['brand'],
            data['category1'], data['category2'], data['category3'], data['category4'],
            data['price_p'], data['price_m'], data['CommentsCount'][0]['CommentCount'], data['picture'],
            resee_str
        )
        # print sql
        self.cursor.execute(sql)


    # 写入商品评价表
    def insert_comment(self, data):
        comment_info = data['CommentsCount'][0] #是一个字典类型
        sku_datetime = time.strftime("%Y%m%d-%H", time.localtime()) + "-" + str(comment_info['SkuId'])

        sql = "replace into spider_jd_comment" \
              "(sku_datetime, skuid, platform, crawl_time, price, price_cost, comment_count, good_count, " \
              "general_count, poor_count, good_rate, general_rate, poor_rate, " \
              "score1_count, score2_count, score3_count, score4_count, score5_count, average_score) " \
              "values('%s', '%s', '%s', now(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        sql = sql % (
            sku_datetime,
            comment_info['SkuId'],
            data['platform'],
            data['price_p'],
            data['price_m'],
            comment_info['CommentCount'],
            comment_info['GoodCount'],
            comment_info['GeneralCount'],
            comment_info['PoorCount'],
            comment_info['GoodRateShow'],
            comment_info['GeneralRateShow'],
            comment_info['PoorRateShow'],
            comment_info['Score1Count'],
            comment_info['Score2Count'],
            comment_info['Score3Count'],
            comment_info['Score4Count'],
            comment_info['Score5Count'],
            comment_info['AverageScore']
        )
        # print sql
        self.cursor.execute(sql)

    def out_2_mysql(self):
        try:
            for p_info in self.product_infos:
                self.update_insert_item(p_info)
                self.insert_comment(p_info)

            self.conn.commit()
        except Exception as e:
            print e
            self.conn.rollback()
        finally:
            self.product_infos = []

    def close(self):
        self.cursor.close()
        self.conn.close()



    