# -*- coding: utf-8 -*-

import signal
import gevent
import gevent.signal

# --------------信号量处理---------------
# 设置监听信号量
# 设置程序结束信号量
def init_gevent_signal(handler):
    gevent.signal(signal.SIGINT, handler, 'sigint')  # 处理 Ctrl-C
    gevent.signal(signal.SIGTERM, handler, 'sigterm')  # 处理 kill
    gevent.signal(signal.SIGALRM, handler, 'sigalrm')  # 处理 signal.alarm()