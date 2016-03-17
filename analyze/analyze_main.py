# -*- coding: utf-8 -*-
import time

import datetime
import traceback

from analyze import comment_manager, incr_manager


class AnalyzeMain(object):

    def __init__(self):
        self.comments = comment_manager.CommentManager()
        self.incr = incr_manager.IncrManager()

    def __incr(self, markXh, incrXh, time_offset, incr, n):  # (mark[0], incrs[0], time_offset, incr, 3)
        if not markXh and time_offset >= n:
            incrXh = incr * n / time_offset
            return True, incrXh
        return markXh, incrXh

    def analyze_snapshot(self, skusnapshots):
        skuid = skusnapshots[0]
        comments = skusnapshots[1]
        today = datetime.datetime.now()

        # ---- 用于计算评价数量 ----
        # 标记是否获取 [3h, 6h, 12h, 24h, 48h, 72h, over72h]
        mark = [False, False, False, False, False, False, False]
        # 标记评价数增量 [3h, 6h, 12h, 24h, 48h, 72h]
        comIncrs = [0l, 0l, 0l, 0l, 0l, 0l]
        # 标记第一条记录的时间
        first_batch_time = None
        first_comment = None

        # ---- 用于计算价格增量 ----
        # 价格降幅 [1日, 2日, 3日, 7日, 10日, 15日]
        priceIncrs = [None, None, None, None, None, None]
        first_price = None
        first_price_date = None

        for comment in comments:
            batch_time = comment[3]  # 批次爬取时间
            if batch_time is None:
                continue

            price = comment[4]
            if first_price is None:
                first_price = price
                first_price_date = datetime.datetime.combine(batch_time, datetime.time.min)  # 某天零时
            if first_batch_time is None:
                first_batch_time = batch_time
                first_comment = comment
            else:
                date_offset = (first_batch_time - batch_time)
                time_offset = date_offset.days * 24 + (date_offset.seconds / 3600)
                incr = first_comment[6] - comment[6]

                mark[0], comIncrs[0] = self.__incr(mark[0], comIncrs[0], time_offset, incr, 3)
                mark[1], comIncrs[1] = self.__incr(mark[1], comIncrs[1], time_offset, incr, 6)
                mark[2], comIncrs[2] = self.__incr(mark[2], comIncrs[2], time_offset, incr, 12)
                mark[3], comIncrs[3] = self.__incr(mark[3], comIncrs[3], time_offset, incr, 24)
                mark[4], comIncrs[4] = self.__incr(mark[4], comIncrs[4], time_offset, incr, 48)
                mark[5], comIncrs[5] = self.__incr(mark[5], comIncrs[5], time_offset, incr, 72)

                # 计算价格增量
                if first_price is not None and price is not None:
                    # 偏移天数 如:first:9号, batch:3, day_offset=6 相差6日
                    tmp_batch_time = datetime.datetime.combine(batch_time, datetime.time.min)  # 某天零时
                    day_offset = first_price_date.day - tmp_batch_time.day

                    # day_offset -> index for priceIncrs[]
                    if 0 < day_offset <= 3:
                        index = day_offset - 1
                    elif 3 < day_offset <= 7:
                        index = 3
                    elif 7 < day_offset <= 10:
                        index = 4
                    elif 10 < day_offset <= 15:
                        index = 5
                    else:
                        index = None

                    if index is not None:
                        price_incr = first_price - price  # 正数涨价,负数降价
                        if priceIncrs[index] is None:
                            priceIncrs[index] = price_incr
                        else:
                            if price_incr < priceIncrs[index]:
                                priceIncrs[index] = price_incr  # 按当天最低价计算

                if mark[6] and date_offset.days > 15:  # 数据保留15天,以后改为配置
                    sku_datetime = comment[0]
                    # 删除该记录
                    self.comments.rm_old_comment(sku_datetime)
                if mark[5]:  # 72h
                    mark[6] = True

        # 修正价格变化
        for i in range((len(priceIncrs) - 1), -1, -1):
            if priceIncrs[i] is None:
                priceIncrs[i] = 0
            elif i > 0:
                for j in range(i-1, -1, -1):
                    if priceIncrs[j] is None:
                        priceIncrs[j] = priceIncrs[i]
                    else:
                        break
        # 封装评价增量对象
        comStrIncrs = [str(comIncrs[0]), str(comIncrs[1]), str(comIncrs[2]), str(comIncrs[3]), str(comIncrs[4]), str(comIncrs[5])]
        return skuid, comStrIncrs, priceIncrs

    def analyze(self):
        num_none = 0
        num_not_none = 0
        num = 0

        try:
            while self.comments.has_next():
                skusnapshots = self.comments.next_comments()  # <type 'tuple'> [0]skuid, [1]comments
                skuid, comStrIncrs, priceIncrs = self.analyze_snapshot(skusnapshots)
                rs = self.incr.upsert_incr(skuid, comStrIncrs, priceIncrs)
                if rs:
                    num_not_none += 1
                else:
                    num_none += 1

        except Exception as e:
            print e
            exstr = traceback.format_exc()
            print exstr
        finally:
            # self.incr.close() #留在后面
            self.comments.commit_close()

        print "None :", num_none
        print "not None :", num_not_none

    def clean(self):
        cleannum = self.incr.clean()
        print "[%s] 清除sku数量:%d" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), cleannum)
        self.incr.close()

if __name__ == '__main__':
    print "-------- analyze --------"
    print "[%s] 程序开始" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    start_time = time.time()

    analyzer = AnalyzeMain()
    print "[%s] analyze初始化完成." % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    analyzer.analyze()

    end_time = time.time()
    print "[%s] 分析结束, 耗时:%.1f分钟" \
          % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), (end_time - start_time) / 60)

    print "[%s] 开始清除一些无价值数据" % (time.strftime("%Y-%m-%d %H:%M:%S"))
    analyzer.clean()
    end_time2 = time.time()
    print "[%s] 清除结束, 耗时:%.1f分钟" \
          % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), (end_time2 - end_time) / 60)




