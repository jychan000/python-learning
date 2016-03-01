# -*- coding: utf-8 -*-
import time

from spider_jd import item_manager, spider_parser, spider_outputer


class SpiderMain(object):

    def __init__(self):
        self.items = item_manager.UrlManager() #管理要爬得目标商品列表
        self.parser = spider_parser.SpiderParser() #分析下载回来的文本
        self.outputer = spider_outputer.SpiderOutputer() #输出爬到的结果

    def craw(self, target_items, time_long):

        app_start_time = time.time()

        time_start = time.time()
        count = 1
        count_output = 1

        self.items.add_new_items(target_items)
        while self.items.has_new_item():
            try:
                new_item = self.items.get_new_item()
                # print ">> craw %d: %s" % (count, new_item)

                new_items, product_info = self.parser.parse(new_item)

                self.items.add_new_items(new_items)
                self.outputer.collect_data(product_info)

                if count_output >= 10:
                    self.outputer.out_2_mysql()
                    count_output = 0

                time_end = time.time()
                if ((time_end - time_start) / 60 >= time_long):
                # if count >= 1:
                    break

                count += 1
                count_output += 1
            except Exception as e:
                print "craw %d failed..." % (count)
                print e

        self.outputer.out_2_mysql()

        app_end_time = time.time()

        print "耗时:%d分钟, 处理数量:%d" % ((app_end_time - app_start_time)/60, count)





if __name__ == "__main__":
    print "程序开始 ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


    # 打包参考https://github.com/robintibor/python-mindwave-mobile

    base_target_items = [1413825] #1413825 1545675031
    time_long = 1 #运行多久,分钟

    obj_spider = SpiderMain()
    obj_spider.craw(base_target_items, time_long)


    print "程序结束 ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
