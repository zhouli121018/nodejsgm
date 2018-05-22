# !/usr/local/u-mail/app/engine/bin/python
# -*-coding:utf8-*-
#
"""
中继发件人信誉度处理程序
建立发件人信誉度：（下面这些分值允许修改）
1、初始默认1000分，被人工审核拒收/dspam/免审拒/的邮件一封扣5分，每天最多扣100分（总分允许负分）；人工审核通过一封增加1分，每天最多加10分；
2、发送一封收件人地址不存在的地址扣5分；发送一封 “垃圾邮件标志”的邮件扣5分；发送一封病毒邮件扣5分；
"""

import sys
import datetime
import traceback

import gevent
import gevent.pool
from gevent import monkey

from lib import common

monkey.patch_all()
common.init_django_enev()

from django.db import InterfaceError, DatabaseError, connection
from lib.common import outinfo, outerror
from lib.django_redis import get_redis
from apps.mail.models import SenderCredit, SenderCreditLog, SenderCreditSettings, get_mail_model, SenderWhitelist
from apps.collect_mail.models import SenderCreditLog as CSenderCreditLog, SenderCredit as CSenderCredit,  \
    SenderCreditSettings as CSenderCreditSettings, get_mail_model as get_cmail_model

# ###########################################################
# 对象
redis = get_redis()

# 变量
_DEBUG = False
REDIS_KEY = 'sender_credit'
REDIS_KEY_temp = 'sender_crecsender_creditdit_temp'
CREDIS_KEY = 'csender_credit'
CREDIS_KEY_temp = 'csender_credit_temp'

class DefaultSetting:
    check_auto_reject = -5
    check_dspam = -5
    review_reject = -5
    review_pass = 1
    send_spam = -5
    send_not_exist = -5
    increase_limit = 10
    reduce_limit = 100

setting = DefaultSetting()
csetting = None

def sender_credit():
    while True:
        try:
            j = redis.brpoplpush(REDIS_KEY, REDIS_KEY_temp)
            mail_id, reason = j.split('----')
            date, id = mail_id.split('_')
            m = get_mail_model(date).objects.get(id=id)
            if m.mail_id != 0:
                redis.lrem(REDIS_KEY_temp, j, 0)
                continue
            sender = m.mail_from.lower().split('=')[-1]
            expect_value = getattr(setting, reason, 0)
            if expect_value < 0:
                key = 'sender_credit-{}'.format(date)
                value_limit = int(setting.reduce_limit)
            else:
                key = 'sender_credit+{}'.format(date)
                value_limit = int(setting.increase_limit)
            try:
                value_count = int(redis.hget(key, sender))
            except:
                value_count = 0
            value = 0 if value_count >= value_limit else expect_value
            redis.hincrby(key, sender, abs(expect_value))
            SenderCreditLog.objects.create(sender=sender, expect_value=expect_value, value=value, reason=reason, mail_id=mail_id)
            if value != 0:
                obj, _ = SenderCredit.objects.get_or_create(sender=sender)
                obj.credit += value
                obj.save()
            outinfo('{}: expect_value({}), value({})'.format(j, expect_value, value))
            redis.lrem(REDIS_KEY_temp, j, 0)
        except (DatabaseError, InterfaceError), e:
            #如果报数据库异常，关闭连接，重新处理任务
            outerror('DatabaseError: {}'.format(j))
            outerror(traceback.format_exc())
            connection.close()
            gevent.sleep(10)
            return
        except BaseException as e:
            outerror('exception: {}'.format(j))
            outerror(traceback.format_exc())

def csender_credit():
    while True:
        try:
            j = redis.brpoplpush(CREDIS_KEY, CREDIS_KEY_temp)
            mail_id, reason = j.split('----')
            date, id = mail_id.split('_')
            m = get_cmail_model(date).objects.get(id=id)
            if m.mail_id != 0:
                redis.lrem(CREDIS_KEY_temp, j, 0)
                continue
            sender = m.mail_from.lower().split('=')[-1]
            expect_value = getattr(csetting, reason, 0)
            if expect_value < 0:
                key = 'csender_credit-{}'.format(date)
                value_limit = int(csetting.reduce_limit)
            else:
                key = 'csender_credit+{}'.format(date)
                value_limit = int(csetting.increase_limit)
            try:
                value_count = int(redis.hget(key, sender))
            except:
                value_count = 0
            value = 0 if value_count >= value_limit else expect_value
            redis.hincrby(key, sender, abs(expect_value))
            CSenderCreditLog.objects.create(sender=sender, expect_value=expect_value, value=value, reason=reason, mail_id=mail_id)
            if value != 0:
                obj, _ = CSenderCredit.objects.get_or_create(sender=sender)
                obj.credit += value
                obj.save()
                if obj.credit > csetting.whitelist_credit:
                    SenderWhitelist.objects.get_or_create(sender=sender, is_global=True)
            outinfo('collect:{}: expect_value({}), value({})'.format(j, expect_value, value))
            redis.lrem(CREDIS_KEY_temp, j, 0)
        except (DatabaseError, InterfaceError), e:
            #如果报数据库异常，关闭连接，重新处理任务
            outerror('DatabaseError: {}'.format(j))
            outerror(traceback.format_exc())
            connection.close()
            gevent.sleep(10)
            return
        except BaseException as e:
            outerror('exception: {}'.format(j))
            outerror(traceback.format_exc())

def init_resource_routine():
    global setting, csetting
    while True:
        settings = SenderCreditSettings.objects.all()
        if settings:
            setting = settings[0]

        settings = CSenderCreditSettings.objects.all()
        if settings:
            csetting = settings[0]
        gevent.sleep(60)


def clear_redis_routine():
    while True:
        clear_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y%m%d')
        outinfo('clear redis: {}'.format(clear_date))
        redis.delete('sender_credit-{}'.format(clear_date))
        redis.delete('sender_credit+{}'.format(clear_date))
        redis.delete('csender_credit-{}'.format(clear_date))
        redis.delete('csender_credit+{}'.format(clear_date))
        gevent.sleep(3600)


def push_data():
    from_date = '20160801'
    to_date = '20160809'
    while from_date != to_date:
        outinfo('push data: {}'.format(from_date))
        mails = get_mail_model(from_date).objects.filter(mail_id=0)
        for m in mails:
            if m.state == 'reject' and m.check_result == 'spam':
                reason = 'check_dspam'
            elif m.state == 'reject' and m.check_result == 'k_auto_reject':
                reason = 'check_auto_reject'
            elif m.state == 'fail_finished' and m.error_type == 2:
                reason = 'send_not_exist'
            elif m.state == 'fail_finished' and m.error_type == 5:
                reason = 'send_spam'
            elif m.reviewer and m.review_result.find('reject') != -1:
                reason = 'review_reject'
            elif m.reviewer and m.review_result.find('pass') != -1:
                reason = 'review_pass'
            else:
                continue
            d = '{}----{}'.format(m.date_id(), reason)
            redis.lpush(REDIS_KEY, d)
        from_date = (datetime.datetime.strptime(from_date, "%Y%m%d") + datetime.timedelta(days=1)).strftime("%Y%m%d")


def init():
    while redis.rpoplpush(REDIS_KEY_temp, REDIS_KEY) is not None:
        pass
    while redis.rpoplpush(CREDIS_KEY_temp, CREDIS_KEY) is not None:
        pass


def main():
    init()
    gevent.joinall([
        gevent.spawn(sender_credit),
        gevent.spawn(csender_credit),
        gevent.spawn(init_resource_routine),
        gevent.spawn(clear_redis_routine),
        #gevent.spawn(push_data),
    ])



if __name__ == "__main__":
    globals()['_DEBUG'] = common.check_debug()
    common.init_cfg_default()
    common.init_run_user(common.cfgDefault.get('global', 'user'))
    common.init_pid_file('SenderCredit.pid')
    common.init_logger('SenderCredit', len(sys.argv) > 1, _DEBUG)

    # 运行程序
    EXIT_CODE = 0
    outinfo("program start")
    main()
    outinfo("program quit")
    sys.exit(EXIT_CODE)
