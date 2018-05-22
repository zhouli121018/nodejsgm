# !/usr/local/u-mail/app/engine/bin/python
# -*-coding:utf8-*-
#
"""
每隔２－３分钟监测dspam 如果超时　则重启postgres　和　dspam
"""

import sys

import os
import time
import subprocess

import gevent
import gevent.pool
from gevent import monkey

import lib.common         as Common


monkey.patch_all()
Common.init_django_enev()
from lib.report_spam import dspamc

from lib.common import outinfo, outerror, wait_call, timeout_command


# ###########################################################
# 变量
_DEBUG = False
eml_file_path = os.path.realpath(os.path.join(os.path.dirname(__file__), 'test.eml'))

def check_dspam():
    while True:
        h = int(time.strftime('%H'))
        if h < 5:
            gevent.sleep(600)
            continue

        res = dspamc(eml_file_path)
        outinfo(res)
        sig = res.get('result', '')
        if not sig:
            outinfo('restart server')
            outinfo('restart postgres')
            subprocess.call('/etc/init.d/postgresql_dspam restart', shell=True)
            outinfo('restart dsapm')
            subprocess.call('/etc/init.d/dspam restart', shell=True)
            outinfo('restart server end')
        gevent.sleep(600)

def main():
    gevent.joinall([
        gevent.spawn(check_dspam),
    ])

if __name__ == "__main__":
    globals()['_DEBUG'] = Common.check_debug()
    # Common.init_cfg_default()
    # Common.init_run_user(Common.cfgDefault.get('global', 'user'))
    # Common.init_pid_file('CheckDspam.pid')
    Common.init_logger('CheckDspam', len(sys.argv) > 1, _DEBUG)

    # 运行程序
    EXIT_CODE = 0
    outinfo("program start")
    main()
    outinfo("program quit")
    sys.exit(EXIT_CODE)
