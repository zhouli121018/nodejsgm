# !/usr/local/u-mail/app/engine/bin/python
# -*-coding:utf8-*-
#
"""
实时同步邮件内容
"""

import os
import sys
import traceback

import gevent
import gevent.pool
from gevent import monkey

import lib.common         as Common


monkey.patch_all()
Common.init_django_enev()
from django.conf import settings
from apps.mail.models import get_mail_model
from apps.collect_mail.models import get_mail_model as get_collect_mail_model
from lib.django_redis import get_redis
from datetime import timedelta, datetime

from lib.common import outinfo, outerror, scp

# ###########################################################
# 对象
redis = get_redis()

# 变量
_DEBUG = False


def sync_mail(key, get_model):
    rkey = '{}_sync'.format(key)
    tmp_rkey = '{}_sync_temp'.format(key)
    server = settings.SYNC_SERVER.upper()
    is_allow_sync = settings.IS_ALLOW_SYNC
    while True:
        try:
            j = redis.brpoplpush(rkey, tmp_rkey)
            date, id = j.split(',')[:2]
            if is_allow_sync:
                mail = get_model(date).objects.get(id=id)
                scp(mail.get_mail_path(), getattr(settings, 'HOST_{}'.format(server)),
                    getattr(settings, 'PORT_{}'.format(server)), flat=False)
                outinfo('{}: {}'.format(rkey, j))
            redis.lrem(tmp_rkey, j, 0)
        except BaseException as e:
            outerror('exception: {}'.format(j))
            outerror(traceback.format_exc())

def make_dir():
    hour_to = 22
    data_path = settings.DATA_PATH
    umail = 'umail'
    while True:
        cur = datetime.now()
        if cur.hour == hour_to:
            next = cur + timedelta(+1)
            da_table = next.strftime('%Y%m%d')
            c_da_table = 'c_' + da_table
            relay_path = os.path.join(data_path, da_table)
            collect_path = os.path.join(data_path, c_da_table)
            if not os.path.exists(relay_path):
                value = {'relay_path': relay_path, 'umail': umail}
                cmd = 'mkdir -p {relay_path}; chmod 775 {relay_path}; chown {umail}:{umail} {relay_path}'.format(**value)
                os.system(cmd)

            if not os.path.exists(collect_path):
                value = {'collect_path': collect_path, 'umail': umail}
                cmd = 'mkdir -p {collect_path}; chmod 775 {collect_path}; chown {umail}:{umail} {collect_path}'.format(**value)
                os.system(cmd)
        gevent.sleep(600)

def init():
    while redis.rpoplpush('relay_sync_temp', 'relay_sync') is not None:
        pass
    while redis.rpoplpush('collect_sync_temp', 'collect_sync') is not None:
        pass


def main():
    init()
    gevent.joinall([
        gevent.spawn(make_dir),
        gevent.spawn(sync_mail, 'relay', get_mail_model),
        gevent.spawn(sync_mail, 'collect', get_collect_mail_model),
    ])


if __name__ == "__main__":
    globals()['_DEBUG'] = Common.check_debug()
    # Common.init_cfg_default()
    # Common.init_run_user(Common.cfgDefault.get('global', 'user'))
    Common.init_pid_file('SyncMail.pid')
    Common.init_logger('SyncMail', len(sys.argv) > 1, _DEBUG)

    # 运行程序
    EXIT_CODE = 0
    outinfo("program start")
    main()
    outinfo("program quit")
    sys.exit(EXIT_CODE)
