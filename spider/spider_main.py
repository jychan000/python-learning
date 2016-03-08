# -*- coding: utf-8 -*-
import Queue
import time

from spider import item_manager, item_miner, spider_parser


class SpiderMain(object):

    def __init__(self):
        self.items = item_manager.UrlManager() #管理要爬得目标商品列表
        self.item_miner = item_miner.itemMiner() # item矿工,用来发现更多item
        self.running_time = 1 #运行时间(分钟)

        self.item_queue = Queue.Queue(0)
        self.paserA = spider_parser.SpiderParser("parserA", self.item_queue)
        self.paserB = spider_parser.SpiderParser("parserB", self.item_queue)
        self.paserC = spider_parser.SpiderParser("parserC", self.item_queue)
        self.paserA.start()
        self.paserB.start()
        self.paserC.start()

    def add_2_queue(self, items):
        if items is not None:
            for item in items:
                self.item_queue.put(item)

    # 开始爬之前的动作
    def pre_craw(self):
        target_items = ["jd_1413825", "jd_2141606", "tb_123456", "vip_123456"]
        true_new_items = self.items.add_new_items(target_items)
        self.add_2_queue(true_new_items)

    def craw(self):
        time_start = time.time()
        while ((time.time() - time_start) / 60 < self.running_time):

            if not self.items.has_new_item():
                #items里没有新的item,无法继续探索其他item,结束item_miner工作
                break

            new_item = self.items.get_new_item()
            new_items = self.item_miner.mining(new_item)
            if new_items is not None:
                true_new_items = self.items.add_new_items(new_items)
                self.add_2_queue(true_new_items)

            print self.item_queue._qsize(), self.items.nums()
            if self.item_queue.qsize() > 300:
                #防止 items 量爆增
                print "item_queue数量大于300, 暂停5秒中..."
                time.sleep(5)


    def after_craw(self):
        pass


# 合理控制退出

if __name__ == '__main__':
    print "spider start..."

    obj_spider = SpiderMain()
    obj_spider.pre_craw()
    obj_spider.craw()
    obj_spider.after_craw()



