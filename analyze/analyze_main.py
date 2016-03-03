# -*- coding: utf-8 -*-
import ConfigParser
import os

import time

from analyze import comment_manager, incr_manager


class AnalyzeMain(object):

    def __init__(self):
        self.comments = comment_manager.CommentManager()
        self.incr = incr_manager.IncrManager()

    def analyze_comments(self, comments):
        """
        处理某skuid的所有评论, 处理目的:
        1.计算出不同时间段内的增量情况
        2.删除计算范围以外的评价记录,用来缓解数据量
        :param comments: 某skuid的评价
        :return:
        """

        skuid = None

        first_batch_time = None
        first_comment = None

        incr3h = 0l
        incr6h = 0l
        incr12h = 0l
        incr24h = 0l
        incr48h = 0l
        incr72h = 0l

        mark3h = False
        mark6h = False
        mark12h = False
        mark24h = False
        mark48h = False
        mark72h = False

        for comment in comments:

            skuid = comment[1]
            batch_time = comment[2]#爬去时间
            if batch_time == None:
                continue
            if first_batch_time == None:
                first_batch_time = batch_time
                first_comment = comment

            else:
                # 最新批次评论与首批的 时间差(小时)
                time_offset = (first_batch_time - batch_time).seconds / 3600

                if not mark3h and time_offset >= 3:
                    incr = first_comment[3] - comment[3]
                    incr3h = incr * 3 / time_offset;
                    mark3h = True
                if not mark6h and time_offset >= 6:
                    incr = first_comment[3] - comment[3]
                    incr6h = incr * 6 / time_offset;
                    mark6h = True
                if not mark12h and time_offset >= 12:
                    incr = first_comment[3] - comment[3]
                    incr12h = incr * 12 / time_offset;
                    mark12h = True
                if not mark24h and time_offset >= 24:
                    incr = first_comment[3] - comment[3]
                    incr24h = incr * 24 / time_offset;
                    mark24h = True
                if not mark48h and time_offset >= 48:
                    incr = first_comment[3] - comment[3]
                    incr48h = incr * 48 / time_offset;
                    mark48h = True
                if not mark72h and time_offset >= 72:
                    incr = first_comment[3] - comment[3]
                    incr72h = incr * 72 / time_offset;
                    mark72h = True

        return skuid, str(incr3h), str(incr6h), str(incr12h), str(incr24h), str(incr48h), str(incr72h)




    def analyze(self):

        num_none = 0
        num_not_none = 0
        num = 0

        try:
            while self.comments.has_next_sku():
                comments = self.comments.get_one_sku_comments()
                # print comments

                #计算某skuid的评价情况
                skuid_incrs_str = self.analyze_comments(comments)
                # print skuid_incrs_str

                #更新增量数据
                self.incr.upsert_incr(skuid_incrs_str);

                num += 1
                if comments == None:
                    num_none += 1
                else:
                    num_not_none += 1

        except Exception as e:
            print e
        finally:
            self.incr.close()


        print "None :", num_none
        print "not None :", num_not_none


if __name__ == '__main__':
    print "程序开始 ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    start_time = time.time()

    # analyzer = AnalyzeMain()
    # analyzer.analyze()

    end_time = time.time()
    print "程序结束 ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print "耗时:", (end_time - start_time), "秒"

    print os.path.dirname(os.path.abspath("db_config.ini"))
