# -*- coding: utf-8 -*-
import time

from analyze import comment_manager, incr_manager


class AnalyzeMain(object):

    def __init__(self):
        self.comments = comment_manager.CommentManager()
        self.incr = incr_manager.IncrManager()

    def __incr(self, markXh, incrXh, time_offset, incr, n):
        if not markXh and time_offset >= n:
            incrXh = incr * n / time_offset
            return True, incrXh
        return markXh, incrXh


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
            if skuid == "1361557":
                print "发现skuid=1361557"
            batch_time = comment[2]#爬取时间
            if batch_time == None:
                continue
            if first_batch_time == None:
                first_batch_time = batch_time
                first_comment = comment

            else:
                # 最新批次与当前批次的 时间差(小时)
                time_offset = (first_batch_time - batch_time).seconds / 3600
                # 评论增加量
                incr = first_comment[3] - comment[3]

                mark3h,  incr3h  = self.__incr(mark3h,  incr3h,  time_offset, incr, 3)
                mark6h,  incr6h  = self.__incr(mark6h,  incr6h,  time_offset, incr, 6)
                mark12h, incr12h = self.__incr(mark12h, incr12h, time_offset, incr, 12)
                mark24h, incr24h = self.__incr(mark24h, incr24h, time_offset, incr, 24)
                mark48h, incr48h = self.__incr(mark48h, incr48h, time_offset, incr, 48)
                mark72h, incr72h = self.__incr(mark72h, incr72h, time_offset, incr, 72)

                if mark72h and time_offset >= 72:
                    sku_datetime = comment[0]
                    #删除该记录

        return skuid, str(incr3h), str(incr6h), str(incr12h), str(incr24h), str(incr48h), str(incr72h)


    def analyze(self):
        num_none = 0
        num_not_none = 0
        num = 0

        try:
            while self.comments.has_next_sku():
                comments = self.comments.get_one_sku_comments()

                #计算某skuid的评价情况
                skuid_incrs_str = self.analyze_comments(comments)

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
            self.comments.commit_close()

        print "None :", num_none
        print "not None :", num_not_none


if __name__ == '__main__':
    print "程序开始 ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    start_time = time.time()

    analyzer = AnalyzeMain()
    analyzer.analyze()

    end_time = time.time()
    print "程序结束 ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print "耗时:", (end_time - start_time), "秒"

