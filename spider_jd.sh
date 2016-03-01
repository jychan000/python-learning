#!/bin/sh

echo "---- spider jd ----"

tpid=`ps aux | grep -c 'spider_main'`

help() {
cat << HELP
Usage: spider_jd.sh {start|stop|version|help}
    start:  启动爬虫
    stop:   停止爬虫
    version:显示版本
    help:   帮助信息
HELP
exit 0
}

start() {
    echo "starting......"
    if [ $tpid -le 1 ]; then

        #把终端输出的内容写到 console.log 文件
        python spider_jd/spider_main.py > console.log &
        #把进程号pid写到 spider_jd_pid.log文件
        echo $! > spider_jd_pid.log
        echo "pid:$!"
    else
        echo "alread start. PID:`cat spider_jd_pid.log`"
        exit 0
    fi
}

stop() {
    echo "stop......"
    pid=`cat spider_jd_pid.log`
    echo "Kill pid:$pid"
    kill -9 $pid
    rm spider_jd_pid.log
}

version() {
    echo "spider_jd 1.0.1"
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