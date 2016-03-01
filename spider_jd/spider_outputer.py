# -*- coding: utf-8 -*-
import MySQLdb
import time


class SpiderOutputer(object):

    def __init__(self):
        self.product_infos = []


    def collect_data(self, product_info):
        if product_info is None:
            return
        self.product_infos.append(product_info)

    def show_infos(self):
        print self.product_infos

    #输出成html已经弃用,只是留着参考代码而已,不可用的了
    def output_html(self):
        print "=================="

        fout = open('output.html', 'w')

        fout.write("<html>")
        fout.write("<head>")
        fout.write("<meta charset='UTF-8'>")
        fout.write("</head>")
        fout.write("<body>")
        fout.write("<table border='1'>")

        fout.write("<tr>")
        fout.write("<td>%s</td>" % "skuid")
        fout.write("<td>%s</td>" % "商品名称")
        fout.write("<td>%s</td>" % "品牌编号")
        fout.write("<td>%s</td>" % "价格")
        fout.write("<td width='80px'>%s</td>" % "评论数")
        fout.write("<td>%s</td>" % "看了又看")
        fout.write("</tr>")

        for data in self.datas:

            re_see_str = ""
            for re_see_ele in data['re_see_info']['data']:
                #<p><font size="4" face="arial" color="red">A paragraph.<br>aaa</font></p>
                re_see_str += ("<font size='2' face='arial'>￥" + str(re_see_ele['jp'])
                               + "(<span style='text-decoration:line-through; color:#808080;'>" + str(re_see_ele['mp']) + "</span>)"
                               +"\t\t<a href='http://item.jd.com/" + str(re_see_ele['sku']) + ".html'>"
                               + re_see_ele['t'].encode('utf-8') + "</a></font>")
                re_see_str += "<br>"

            fout.write("<tr>")
            fout.write("<td><font size='2' face='arial'>%s</font></td>" % data['skuid'])
            fout.write("<td width='400px'><font size='2' face='arial'>%s</font></td>" % data['name'].encode('utf-8'))
            fout.write("<td><font size='2' face='arial'>%s</font></td>" % data['brand'].encode('utf-8'))
            fout.write("<td><font size='2' face='arial'>%s</font></td>" % (data['price_p'] + "<br><span style='text-decoration:line-through; color:#808080; '>" + data['price_m'] + "</span>" ))
            fout.write("<td><font size='2' face='arial'>%s<br>好评%s</font></td>"
                       % (data['comments']['CommentsCount'][0]['CommentCount'],
                          str(data['comments']['CommentsCount'][0]['GoodRate']*100) + "%"))
            fout.write("<td>%s</td>" % re_see_str)

            fout.write("</tr>")

        fout.write("</table>")
        fout.write("</body>")
        fout.write("</html>")

        fout.close()

    # 写入商品信息表
    def update_insert_item(self, data):
        sql = "replace into spider_jd_item(%s) " \
              "values('%s', '%s', '%s', '%s', '%s', '%s', '%s', %s, %s, %s, now(), %s)"
        sql_column = "" \
                     "skuid, " \
                     "product_name, " \
                     "brand_id, " \
                     "category1, " \
                     "category2, " \
                     "category3, " \
                     "category4, " \
                     "price, " \
                     "price_cost, " \
                     "comment_count, " \
                     "update_time, "

        re_see_str = ""
        index = 1
        for re_see_ele in data['re_see_info']['data']:
            sql_column += ("re_see_skuid" + str(index) + ", ")
            re_see_str += ("'" + str(re_see_ele['sku']) + "', ")
            index += 1

        sql_column = sql_column[:-2]
        re_see_str = re_see_str[:-2]
        sql = sql % (
            sql_column,
            data['skuid'],
            data['name'],
            data['brand'],
            data['category1'],
            data['category2'],
            data['category3'],
            data['category4'],
            data['price_p'],
            data['price_m'],
            data['CommentsCount'][0]['CommentCount'],
            re_see_str
        )
        # print sql
        self.cursor.execute(sql)


    # 写入商品评价表
    def insert_comment(self, data):
        comment_info = data['CommentsCount'][0] #是一个字典类型
        sku_datetime = time.strftime("%Y%m%d-%H", time.localtime()) + "-" + str(comment_info['SkuId'])

        sql = "replace into spider_jd_comment(" \
              "sku_datetime, " \
              "skuid, " \
              "crawl_time, " \
              "comment_count, " \
              "good_count, " \
              "general_count, " \
              "poor_count, " \
              "good_rate, " \
              "general_rate, " \
              "poor_rate, " \
              "score1_count, " \
              "score2_count, " \
              "score3_count, " \
              "score4_count, " \
              "score5_count, " \
              "average_score) " \
              "values('%s', '%s', now(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        sql = sql % (
            sku_datetime,
            comment_info['SkuId'],
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
        print "执行一次写入"
        self.conn = MySQLdb.Connect(
            host = '127.0.0.1',
            # host = '172.26.21.13',
            port = 3306,
            user = 'root',
            passwd = 'sa',
            db = 'spider',
            charset = 'utf8'
        )
        self.cursor = self.conn.cursor()
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
            self.cursor.close()
            self.conn.close()



    