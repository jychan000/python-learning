# -*- coding: utf-8 -*-
import Queue
import time

from spider import item_manager, item_miner, spider_thread, config_center


class SpiderMain(object):

    def __init__(self):
        self.items = item_manager.UrlManager() #管理要爬得目标商品列表
        self.item_miner = item_miner.itemMiner() # item矿工,用来发现更多item
        self.config = config_center.SpiderConfig()
        self.runtime = self.config.runtime #运行时间(分钟)

        print "[%s] 爬取新item计划 %d分钟" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.runtime)

        self.item_pending_queue = Queue.Queue(0)
        for i in range(self.config.worker):
            workername = "worker-%d" % (i)
            spider_thread.SpiderParserThread(workername, self.item_pending_queue, (i + 4), (self.runtime + 2)).start()

        # self.paserA = spider_thread.SpiderParserThread("parser_A", self.item_pending_queue, 4, (self.runtime + 2))
        # self.paserB = spider_thread.SpiderParserThread("parser_B", self.item_pending_queue, 5, (self.runtime + 2))
        # self.paserC = spider_thread.SpiderParserThread("parser_C", self.item_pending_queue, 6, (self.runtime + 2))
        # self.paserA.start()
        # self.paserB.start()
        # self.paserC.start()

    def add_2_queue(self, items):
        if items is not None:
            for item in items:
                self.item_pending_queue.put(item)

    # 开始爬之前的动作
    def pre_craw(self):
        target_items = self.config.targetItems
        # target_items = ["jd_1021643905", "jd_549056", "jd_1135614", "jd_1783428386", "jd_1413825", "tb_123456", "vip_123456"] #"jd_1783428386", "jd_1413825",
        true_new_items = self.items.add_new_items(target_items)
        self.add_2_queue(true_new_items)

    def craw(self):
        time_start = time.time()
        while ((time.time() - time_start) / 60 < self.runtime):

            if not self.items.has_new_item():
                print "[%s] item管理器里没有新的item,主程序停止抓取工作." % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                break

            new_item = self.items.get_new_item()
            new_items = self.item_miner.mining(new_item)
            if new_items is not None:
                true_new_items = self.items.add_new_items(new_items)
                self.add_2_queue(true_new_items)
            if self.item_pending_queue.qsize() > 200:
                time.sleep(5)

        print "[%s] 主程序停止抓取items,等待全部子线程结束." % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def after_craw(self):
        pass

if __name__ == '__main__':
    print "[%s] 爬虫程序开始" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    obj_spider = SpiderMain()
    obj_spider.pre_craw()
    obj_spider.craw()
    obj_spider.after_craw()


