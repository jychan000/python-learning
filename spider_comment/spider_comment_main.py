# -*- coding: utf-8 -*-
import time

from spider_comment import comment_manager, spider_downloader

class spider_comment_main(object):
    def __init__(self):
        self.connectManager = comment_manager.CommentManager()
        self.spiderDownloader = spider_downloader.SpiderDownloader()

    def work(self):
        skuid_list = self.connectManager.getSkuidList()
        self.comment_dictionary = dict()
        index = 0
        for skuid in skuid_list:
            if index >= 100:
                break
            self.spiderDownloader.getComments(skuid)
            index += 1
        self.connectManager.commit_close()


if __name__ == '__main__':
    print "-------- analyze --------"
    print "[%s] 抓取评论任务开始" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    start_time = time.time()

    spiderComment = spider_comment_main()
    print "[%s] 任务完成." % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    spiderComment.work()

    end_time = time.time()
    print "[%s] 程序结束, 耗时:%.1f分钟" \
          % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), (end_time - start_time) / 60)
