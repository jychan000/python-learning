# -*- coding: utf-8 -*-
import time

format = "%Y-%m-%d %H:%M:%S"

def gettimeStr():
    return time.strftime(format, time.localtime())


if __name__ == '__main__':
    print gettimeStr()