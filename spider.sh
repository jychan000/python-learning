#!/bin/sh

echo "---- spider ----"

tpid=`ps aux | grep -c 'spider_main'`

help() {
cat << HELP
Usage: spider.sh {start|stop|version|help}
    start:  start spider
    stop:   stop spider
    version:show the spider version
    help:   show help info
HELP
exit 0
}

start() {
    echo "starting......"
    if [ $tpid -le 1 ]; then

        #把终端输出的内容写到 console-spider.log  文件
        cd spider
        python spider_main.py >> ../console-spider.log &
        #把进程号pid写到 pid-spider.log文件
        echo $! > ../pid-spider.log
        echo "pid:$!"
        cd ..
    else
        echo "alread start. PID:`cat pid-spider.log`"
        exit 0
    fi
}

stop() {
    echo "stop......"
    pid=`cat pid-spider.log`
    echo "Kill pid:$pid"
    kill -9 $pid
    rm pid-spider.log
}

version() {
    echo "spider 1.0.1"
    echo "author:chenjinying"
    echo "email:415683089@qq.com"
}

case "$1" in
    start)
        start
    ;;
    stop)
        stop
    ;;
    restart)
        stop
        start
    ;;
    version)
        version
    ;;
    *)
        help
    ;;
esac

