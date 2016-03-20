# -*- coding: utf-8 -*-
import time

import datetime


class Analyzer(object):

    def filter(self, skuid, comment_count, comment_incrs, price_incrs):
        # 评价数量小于1000的分析结果
        if comment_count < 2000:
            return False

        #增长率异常
        incr_24h = long(comment_incrs[3])  # 24小时增量
        incr_48h = long(comment_incrs[4])  # 48小时增量
        incr_72h = long(comment_incrs[5])  # 72小时增量
        count_24h = comment_count - incr_24h  # 24小时前数量
        count_48h = comment_count - incr_48h  # 48小时前数量
        count_72h = comment_count - incr_72h  # 72小时前数量

        if (float(incr_24h) / count_24h > 0.3) and (comment_count >= 10000):
            return False
        if (float(incr_48h) / count_48h > 0.3) and (comment_count >= 10000):
            return False
        if (float(incr_72h) / count_72h > 0.3) and (comment_count >= 10000):
            return False

        if (float(incr_24h) / count_24h > 0.17) and (comment_count >= 100000):
            return False
        if (float(incr_48h) / count_48h > 0.17) and (comment_count >= 100000):
            return False
        if (float(incr_72h) / count_72h > 0.17) and (comment_count >= 100000):
            return False

        return True

    def getincr(self, markXh, incrXh, time_offset, incr, n):  # (mark[0], incrs[0], time_offset, incr, 3)
        if not markXh and time_offset >= n:
            incrXh = incr * n / time_offset
            return True, incrXh
        return markXh, incrXh

    def analyze_snapshot(self, skusnapshots):
        skuid = skusnapshots[0]
        comments = skusnapshots[1]
        today = datetime.datetime.now()

        # 记录已经过时的
        outdate_comments = list()

        # ---- 用于计算评价数量 ----
        # 标记是否获取 [3h, 6h, 12h, 24h, 48h, 72h, over72h]
        mark = [False, False, False, False, False, False, False]
        # 标记评价数增量 [3h, 6h, 12h, 24h, 48h, 72h]
        comIncrs = [0l, 0l, 0l, 0l, 0l, 0l]
        # 标记第一条记录的时间
        first_batch_time = None
        first_comment = None
        first_comment_count = None

        # ---- 用于计算价格增量 ----
        # 价格降幅 [1日, 2日, 3日, 7日, 10日, 15日]
        price_incrs = [None, None, None, None, None, None]
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
                first_comment_count = first_comment[6]
            else:
                date_offset = (first_batch_time - batch_time)
                time_offset = date_offset.days * 24 + (date_offset.seconds / 3600)
                incr = first_comment[6] - comment[6]

                mark[0], comIncrs[0] = self.getincr(mark[0], comIncrs[0], time_offset, incr, 3)
                mark[1], comIncrs[1] = self.getincr(mark[1], comIncrs[1], time_offset, incr, 6)
                mark[2], comIncrs[2] = self.getincr(mark[2], comIncrs[2], time_offset, incr, 12)
                mark[3], comIncrs[3] = self.getincr(mark[3], comIncrs[3], time_offset, incr, 24)
                mark[4], comIncrs[4] = self.getincr(mark[4], comIncrs[4], time_offset, incr, 48)
                mark[5], comIncrs[5] = self.getincr(mark[5], comIncrs[5], time_offset, incr, 72)

                # 计算价格增量
                if first_price is not None and price is not None:
                    # 偏移天数 如:first:9号, batch:3, day_offset=6 相差6日
                    tmp_batch_time = datetime.datetime.combine(batch_time, datetime.time.min)  # 某天零时
                    day_offset = first_price_date.day - tmp_batch_time.day

                    # day_offset -> index for price_incrs[]
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
                        if price_incrs[index] is None:
                            price_incrs[index] = price_incr
                        else:
                            if price_incr < price_incrs[index]:
                                price_incrs[index] = price_incr  # 按当天最低价计算

                if mark[6] and date_offset.days > 15:  # 数据保留15天,以后改为配置
                    sku_datetime = comment[0]
                    outdate_comments.append(sku_datetime)
                if mark[5]:  # 72h
                    mark[6] = True

        # 修正价格变化
        for i in range((len(price_incrs) - 1), -1, -1):
            if price_incrs[i] is None:
                price_incrs[i] = 0
            elif i > 0:
                for j in range(i-1, -1, -1):
                    if price_incrs[j] is None:
                        price_incrs[j] = price_incrs[i]
                    else:
                        break
        # 封装评价增量对象
        comment_incrs = [str(comIncrs[0]), str(comIncrs[1]), str(comIncrs[2]), str(comIncrs[3]), str(comIncrs[4]), str(comIncrs[5])]
        return skuid, first_comment_count, comment_incrs, price_incrs, outdate_comments


