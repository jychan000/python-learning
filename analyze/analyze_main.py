# -*- coding: utf-8 -*-
import time

import traceback
from analyze import comment_manager, incr_manager, analyze_center

# reload(sys)
# sys.setdefaultencoding('utf8')

class AnalyzeMain(object):

    def __init__(self):
        self.snapshots = comment_manager.CommentManager()
        self.incr = incr_manager.IncrManager()
        self.analyzer = analyze_center.Analyzer()

    def analyze(self):
        num_none = 0
        num_insert = 0
        num_filter = 0

        try:
            while self.snapshots.has_next():
                skusnapshots = self.snapshots.next_comments()  # <type 'tuple'> [0]skuid, [1]comments

                skuid, comment_count, comment_incrs, price_incrs, outdate_comments = self.analyzer.analyze_snapshot(skusnapshots)
                self.snapshots.rm_outdate_comment(outdate_comments)
                useful = self.analyzer.filter(skuid, comment_count, comment_incrs, price_incrs)
                if useful:
                    rs = self.incr.upsert_incr(skuid, comment_incrs, price_incrs)
                    if rs:
                        num_insert += 1
                    else:
                        num_none += 1
                else:
                    num_filter += 1

        except Exception as e:
            print e
            exstr = traceback.format_exc()
            print exstr
        finally:
            self.snapshots.commit_close()
            return num_insert, num_filter, num_none

    def clean(self):
        cleannum = self.incr.clean()
        print "[%s] 清除sku数量:%d" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), cleannum)
        self.incr.close()

if __name__ == '__main__':
    print "-------- analyze --------"
    print "[%s] 程序开始" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    start_time = time.time()

    analyzer = AnalyzeMain()
    print "[%s] analyze初始化完成." % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    num_insert, num_filter, num_none = analyzer.analyze()
    print "[%s] 写入:%d, 过滤:%d, 失败:%d" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), num_insert, num_filter, num_none)

    end_time = time.time()
    print "[%s] 分析结束, 耗时:%.1f分钟" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), (end_time - start_time) / 60)
    print "[%s] 开始清除一些无价值数据" % (time.strftime("%Y-%m-%d %H:%M:%S"))

    analyzer.clean()
    end_time2 = time.time()
    print "[%s] 清除结束, 耗时:%.1f分钟" \
          % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), (end_time2 - end_time) / 60)


