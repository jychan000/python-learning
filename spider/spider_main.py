# -*- coding: utf-8 -*-
import Queue
import time

from spider import item_manager, item_miner, spider_thread


class SpiderMain(object):

    def __init__(self):
        self.items = item_manager.UrlManager() #管理要爬得目标商品列表
        self.item_miner = item_miner.itemMiner() # item矿工,用来发现更多item
        self.runtime = 150 #运行时间(分钟)

        self.item_pending_queue = Queue.Queue(0)
        self.paserA = spider_thread.SpiderParserThread("parser_A", self.item_pending_queue, 4, (self.runtime + 2))
        self.paserB = spider_thread.SpiderParserThread("parser_B", self.item_pending_queue, 5, (self.runtime + 2))
        self.paserC = spider_thread.SpiderParserThread("parser_C", self.item_pending_queue, 6, (self.runtime + 2))
        self.paserA.start()
        self.paserB.start()
        self.paserC.start()

    def add_2_queue(self, items):
        if items is not None:
            for item in items:
                self.item_pending_queue.put(item)

    # 开始爬之前的动作
    def pre_craw(self):
        target_items = ["jd_1413825", "jd_2141606", "tb_123456", "vip_123456"]
        true_new_items = self.items.add_new_items(target_items)
        self.add_2_queue(true_new_items)

    def craw(self):
        time_start = time.time()
        while ((time.time() - time_start) / 60 < self.runtime):

            if not self.items.has_new_item():
                #items里没有新的item,无法继续探索其他item,结束item_miner工作
                break

            new_item = self.items.get_new_item()
            new_items = self.item_miner.mining(new_item)
            if new_items is not None:
                true_new_items = self.items.add_new_items(new_items)
                self.add_2_queue(true_new_items)

            # print self.item_pending_queue._qsize(), self.items.nums()
            if self.item_pending_queue.qsize() > 200:
                # print "item_queue数量大于300, 暂停5秒中..."
                time.sleep(5)
        print "[%s] 主线程停止抓取items,等待全部子线程结束." % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def after_craw(self):
        pass


# 合理控制退出

if __name__ == '__main__':
    print "[%s] 爬虫程序开始" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    obj_spider = SpiderMain()
    obj_spider.pre_craw()
    obj_spider.craw()
    obj_spider.after_craw()


