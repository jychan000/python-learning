# -*- coding: utf-8 -*-
import time

import datetime

from analyze import comment_manager, incr_manager


class AnalyzeMain(object):

    def __init__(self):
        self.comments = comment_manager.CommentManager()
        self.incr = incr_manager.IncrManager()

    def __incr(self, markXh, incrXh, time_offset, incr, n): #(mark[0], incrs[0], time_offset, incr, 3)
        if not markXh and time_offset >= n:
            incrXh = incr * n / time_offset
            return True, incrXh
        return markXh, incrXh


    def price_decr(self, sku_snapshots):
        print "计算降价幅度"
        # 记录1日, 2日, 3日, 7日, 15日, 30日 价格与当前价格的差距,可为正负值,每天取最低价
        # 当天最高价,当天最低价
        # 昨天最高价,昨天最低价

        # 这个应该从旧数据中获取
        # [当日最高, 当日最低, 昨日最高, 昨日最低, 1日降幅, 2日降幅, 3日降幅, 7日降幅, 15日降幅, 30日降幅]
        price_info = [0, 999999, 0, 999999, 0, 0, 0, 0, 0, 0]

        skuid = sku_snapshots[0]
        snapshots = sku_snapshots[1]

        today = datetime.datetime.now()
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

        for snapshot in snapshots:
            crawltime = snapshot[3]
            price = snapshot[4]

            if crawltime is None or price is None:
                continue

            # 1.判断是否今天
            if today.year == crawltime.year and today.month == crawltime.month and today.day == crawltime.day:
                # 更新当日,最高价/最低价
                if price_info[0] < price:
                    price_info[0] = price
                if price_info[1] > price:
                    price_info[1] = price

            # 2.判断是否昨天
            if yesterday.year == crawltime.year and yesterday.month == crawltime.month and yesterday.day == crawltime.day:
                # 更新昨日,最高价/最低价
                if price_info[3] < price:
                    price_info[3] = price
                if price_info[4] > price:
                    price_info[4] = price


        return None



    def analyze_snapshot(self, skusnapshots):
        # price_decr = self.price_decr(skusnapshots)

        skuid = skusnapshots[0]
        comments = skusnapshots[1]
        today = datetime.datetime.now()

        # 标记是否获取 [3h, 6h, 12h, 24h, 48h, 72h, over72h]
        mark = [False, False, False, False, False, False, False]
        # 标记评价数增量 [3h, 6h, 12h, 24h, 48h, 72h]
        incrs = [0l, 0l, 0l, 0l, 0l, 0l]
        # 标记第一条记录的时间
        first_batch_time = None
        first_comment = None

        for comment in comments:
            batch_time = comment[3]#批次爬取时间
            if batch_time == None:
                continue

            if first_batch_time == None:
                #如果最新的记录非当天,则停止,把全部增量设置为0  --------暂时不起用
                # if today.year != batch_time.year and today.month != batch_time.month and today.day != batch_time.day:
                #     break
                first_batch_time = batch_time
                first_comment = comment
            else:
                date_offset = (first_batch_time - batch_time)
                time_offset = date_offset.days * 24 + (date_offset.seconds / 3600)
                incr = first_comment[6] - comment[6]

                mark[0], incrs[0] = self.__incr(mark[0], incrs[0], time_offset, incr, 3)
                mark[1], incrs[1] = self.__incr(mark[1], incrs[1], time_offset, incr, 6)
                mark[2], incrs[2] = self.__incr(mark[2], incrs[2], time_offset, incr, 12)
                mark[3], incrs[3] = self.__incr(mark[3], incrs[3], time_offset, incr, 24)
                mark[4], incrs[4] = self.__incr(mark[4], incrs[4], time_offset, incr, 48)
                mark[5], incrs[5] = self.__incr(mark[5], incrs[5], time_offset, incr, 72)

                if mark[6]: # over72h
                    sku_datetime = comment[0]
                    #删除该记录
                    self.comments.rm_old_comment(sku_datetime)
                if mark[5]: # 72h
                    mark[6] = True
        return skuid, str(incrs[0]), str(incrs[1]), str(incrs[2]), str(incrs[3]), str(incrs[4]), str(incrs[5])


    def analyze(self):
        num_none = 0
        num_not_none = 0
        num = 0

        try:
            while self.comments.has_next():
                skusnapshots = self.comments.next_comments()#<type 'tuple'> [0]skuid, [1]comments
                skucomments_incrs = self.analyze_snapshot(skusnapshots)
                # print skucomments_incrs
                self.incr.upsert_incr(skucomments_incrs)
                num_not_none += 1

        except Exception as e:
            print e
        finally:
            self.incr.close()
            self.comments.commit_close()

        print "None :", num_none
        print "not None :", num_not_none


if __name__ == '__main__':
    print "-------- analyze --------"
    print "[%s] 程序开始" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    start_time = time.time()

    analyzer = AnalyzeMain()
    print "[%s] analyze初始化完成." % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    analyzer.analyze()

    end_time = time.time()
    print "[%s] 程序结束, 耗时:%.1f分钟" \
          % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), (end_time - start_time) / 60)

