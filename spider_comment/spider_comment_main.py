# -*- coding: utf-8 -*-
import time

from spider_comment import db_manager, spider_downloader


class SpiderCommentMain(object):
    def __init__(self):
        self.connectManager = db_manager.DbManager()
        self.spiderDownloader = spider_downloader.SpiderDownloader()

    def work(self):
        skuid_list = self.connectManager.getSkuidList()
        self.comment_dictionary = dict()
        for skuid in skuid_list:
            try:
                self.spiderDownloader.getComments(skuid)
            except Exception as e:
                print e
        self.connectManager.commit_close()


if __name__ == '__main__':
    print "-------- analyze --------"
    print "[%s] 抓取评论任务开始" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    start_time = time.time()

    spiderComment = SpiderCommentMain()
    spiderComment.work()

    end_time = time.time()
    print "[%s] 程序结束, 耗时:%.1f分钟" \
          % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), (end_time - start_time) / 60)
