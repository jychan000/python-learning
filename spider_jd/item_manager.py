# -*- coding: utf-8 -*-
class UrlManager(object):
    
    def __init__(self):
        self.new_items = set()
        self.old_items = set()

    def add_new_item(self, new_item):
        if new_item is None:
            return
        if new_item not in self.new_items and new_item not in self.old_items:
            self.new_items.add(new_item)

    def add_new_items(self, new_items):
        if new_items is None or len(new_items) == 0:
            return
        for new_item in new_items:
            self.add_new_item(new_item)

    def has_new_item(self):
        return len(self.new_items) != 0

    def get_new_item(self):
        new_item = self.new_items.pop() #从set中取出一个
        self.old_items.add(new_item)
        return new_item

    def show_old(self):
        print self.old_items
        print