# -*- coding: utf-8 -*-
import threading
import traceback

import time

from spider import spider_downloader, spider_outputer, spider_parser


class SpiderParserThread(threading.Thread):

    def __init__(self, name, queue, delay, runtime):
        threading.Thread.__init__(self, name=name)
        self.name = name
        self.queue = queue
        self.delay = delay
        self.runtime = runtime

        self.downloader = spider_downloader.SpiderDownloader()
        self.outputer = spider_outputer.SpiderOutputer()
        self.parser = spider_parser.SpiderParser()

    def run(self):
        time.sleep(self.delay)
        print "[%s] %s开始" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.getName())
        time_start_thread = time.time()

        all_count = 0
        success_count = 0
        faild_count = 0
        count_output = 0

        while not self.queue.empty():
            if (time.time() - time_start_thread) / 60 >= self.runtime:
                print "[%s] %s运行时间超出指定范围:%d分钟" \
                      % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.getName(), self.runtime)
                break

            item = self.queue.get()
            count_output += 1
            all_count += 1

            try:
                p_info = self.parser.parse(item)
                if p_info == None:
                    faild_count += 1
                    continue

                self.outputer.collect_data(p_info)

                if count_output >= 10:
                    self.outputer.out_2_mysql()
                    count_output = 0
                success_count += 1

            except Exception as e:
                faild_count += 1
                print "craw failed: %s" % (item)
                print e
                exstr = traceback.format_exc()
                print exstr

        self.outputer.out_2_mysql()
        self.outputer.close()

        time.sleep(self.delay - 3)
        time_end_thread = time.time()
        spend_time = (time_end_thread - time_start_thread) / 60
        timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print "[%s] %s结束, 总消时:%.1f分钟, 速度:%d条/分钟, 总处理:%d, 成功:%d, 失败:%d" \
              % (timestr, self.getName(), spend_time, (all_count / spend_time), all_count, success_count, faild_count)

