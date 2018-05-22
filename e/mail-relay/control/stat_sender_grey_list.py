# coding=utf-8
"""
统计发送日志
"""
import sys
import time
import traceback
import datetime

import lib.common as Common
from lib.common import outinfo, outerror

Common.init_django_enev()

from django.db import connection
from apps.mail.models import CheckSettings
from lib.django_redis import get_redis


class DefaultCheckSetting(object):
    hrisk_sender_check_time = 60
    hrisk_sender_time = 600
    hrisk_sender_scale = 50
    hrisk_sender_total_num_min = 10
    hrisk_diff_sender_count = 5
    hrisk_diff_sender_time = 600


_DEBUG = False
redis = get_redis()
check_setting = DefaultCheckSetting()

KEY = 'relay_sender_grey_list'
KEY_TEMP = 'relay_sender_grey_list_temp'

KEY_1 = 'relay_sender_grey_list_1'
KEY_1_TEMP = 'relay_sender_grey_list_1_temp'

state_count_sql = '''
select
    mail_from,
    count(*) as total_num,
    count(case when state in ('reject', 'bounce', 'fail_finished')
               then 1
               else null end) as fail_num
from {}
where created > %s
group by mail_from;
'''

sender_name_count_sql = '''
with t as (select mail_from, sender_name from {}
           group by mail_from, sender_name)
    select mail_from from t
    group by mail_from having count(*) >= %s;
'''


def stat_sender_grey_list():
    outinfo('stat_sender_grey_list: start')

    # config
    period = datetime.timedelta(seconds=check_setting.hrisk_sender_check_time * 60)
    expire = check_setting.hrisk_sender_time * 60
    threshold = check_setting.hrisk_sender_scale / 100.00
    total_num_min = check_setting.hrisk_sender_total_num_min

    end_time = datetime.datetime.now()
    start_time = end_time - period
    t1 = start_time.strftime('mail_%Y%m%d')
    t2 = end_time.strftime('mail_%Y%m%d')
    if t1 == t2:
        table = t1
    else:
        table = '((select * from {}) union all (select * from {})) as u'.format(t1, t2)

    with connection.cursor() as curs:
        curs.execute(state_count_sql.format(table), [start_time])
        l = curs.fetchall()
    grey_list = [mail_from
                 for mail_from, total_num, fail_num in l
                 if total_num >= total_num_min and float(fail_num) / float(total_num) >= threshold]

    now = time.time()
    old_dict = redis.hgetall(KEY)
    new_dict = {}
    for sender, add_time in old_dict.iteritems():
        if float(add_time) + expire >= now:
            new_dict[sender] = add_time
    for sender in grey_list:
        if sender not in new_dict:
            new_dict[sender] = now

    outinfo('stat_sender_grey_list: update redis, size={}'.format(len(new_dict)))
    redis.delete(KEY_TEMP)
    redis.hmset(KEY_TEMP, new_dict)
    redis.rename(KEY_TEMP, KEY)


def stat_sender_grey_list_1():
    outinfo('stat_sender_grey_list_1: start')

    # config
    diff_sender_name_count_min = check_setting.hrisk_diff_sender_count
    expire = check_setting.hrisk_diff_sender_time * 60

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    t1 = today.strftime('mail_%Y%m%d')
    t2 = yesterday.strftime('mail_%Y%m%d')
    table = '((select * from {}) union all (select * from {})) as u'.format(t1, t2)

    with connection.cursor() as curs:
        curs.execute(sender_name_count_sql.format(table), [diff_sender_name_count_min])
        grey_list = [mail_from for mail_from, in curs]

    now = time.time()
    old_dict = redis.hgetall(KEY_1)
    new_dict = {}
    for sender, add_time in old_dict.iteritems():
        if float(add_time) + expire >= now:
            new_dict[sender] = add_time
    for sender in grey_list:
        if sender not in new_dict:
            new_dict[sender] = now

    outinfo('stat_sender_grey_list_1: update redis, size={}'.format(len(new_dict)))
    redis.delete(KEY_1_TEMP)
    redis.hmset(KEY_1_TEMP, new_dict)
    redis.rename(KEY_1_TEMP, KEY_1)


def init_resource():
    global check_setting

    check_settings = CheckSettings.objects.all()
    if check_settings:
        check_setting = check_settings[0]


if __name__ == "__main__":
    globals()['_DEBUG'] = Common.check_debug(2)
    Common.init_cfg_default()
    Common.init_run_user(Common.cfgDefault.get('global', 'user'))
    Common.init_pid_file('StatSenderGreyList.pid')
    Common.init_logger('StatSenderGreyList', len(sys.argv) > 1, _DEBUG)

    # 运行程序
    EXIT_CODE = 0
    outinfo("program start")
    init_resource()
    try:
        stat_sender_grey_list()
        stat_sender_grey_list_1()
    except:
        outerror(traceback.format_exc())
        EXIT_CODE = 1
    outinfo("program quit")
    sys.exit(EXIT_CODE)
