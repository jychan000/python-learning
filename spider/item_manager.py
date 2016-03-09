# -*- coding: utf-8 -*-
class UrlManager(object):
    
    def __init__(self):
        self.new_items = set() #用于判断是否需要爬取, 有进有出
        self.old_items = set() #用于判断是否需要爬取, 只进不出

    def add_new_item(self, new_item):
        len1 = 0
        len2 = 0
        if new_item is not None and new_item not in self.new_items and new_item not in self.old_items:
            len1 = len(self.new_items)
            self.new_items.add(new_item)
            len2 = len(self.new_items)
        return len2 > len1

    def add_new_items(self, new_items):
        true_new_items = set()
        if new_items is None or len(new_items) == 0:
            return None
        for new_item in new_items:
            rs = self.add_new_item(new_item)
            if rs:
                true_new_items.add(new_item)
        return true_new_items

    def has_new_item(self):
        return len(self.new_items) != 0

    def get_new_item(self):
        new_item = self.new_items.pop()
        self.old_items.add(new_item)
        return new_item

    def nums(self):
        return len(self.new_items), len(self.old_items)
