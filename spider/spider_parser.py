# -*- coding: utf-8 -*-
import threading

import time


class SpiderParser(threading.Thread):

    def __init__(self, name, queue):
        threading.Thread.__init__(self, name=name)
        self.name = name
        self.queue = queue

    def run(self):
        time.sleep(5)
        print "SpiderParser.run()"
        while not self.queue.empty():
            item = self.queue.get()
            print self.name, item, self.queue.qsize()
        print "SpiderParser end"