#!/bin/sh

echo "---- analyze ----"

tpid=`ps aux | grep -c 'analyze_main'`

help() {
cat << HELP
Usage: analyze.sh {start|stop|version|help}
    start:  启动分析
    stop:   停止分析
    version:显示版本
    help:   帮助信息
HELP
exit 0
}

start() {
    echo "starting......"
    if [ $tpid -le 1 ]; then

        #把终端输出的内容写到 console-analyze.log 文件
        python analyze/analyze_main.py >> console-analyze.log &
        #把进程号pid写到 analyze_pid.log文件
        echo $! > analyze_pid.log
        echo "pid:$!"
    else
        echo "analyze alread start. PID:`cat analyze_pid.log`"
        exit 0
    fi
}

stop() {
    echo "stop analyze ......"
    pid=`cat analyze_pid.log`
    echo "Kill pid:$pid"
    kill -9 $pid
    rm analyze_pid.log
}

version() {
    echo "analyze 1.0.1"
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

