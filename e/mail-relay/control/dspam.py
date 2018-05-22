# !/usr/local/u-mail/app/engine/bin/python
# -*-coding:utf8-*-
#

import sys
import os
import time
import traceback

import gevent
import gevent.pool
from gevent import monkey

import lib.common         as Common


monkey.patch_all()
Common.init_django_enev()
from django.conf import settings

from lib.common import outinfo, outerror
from lib.report_spam import dspamc
from apps.mail.models import get_mail_model
from apps.collect_mail.models import get_mail_model as get_collect_mail_model

# ###########################################################
# 对象
redis = Common.get_redis_cli()
dspam_path = settings.DATA_DSPAM_PATH

# 变量
_DEBUG = False


def dspam_reject_from_path(dspam_path, get_model):
    while True:
        mails = os.listdir(dspam_path)
        if not mails:
            gevent.sleep(1)
            continue
        for mail in mails:
            try:
                mail_path = os.path.join(dspam_path, mail)
                if not os.path.exists(mail_path):
                    continue

                try:
                    date, id = mail.split(',')[:2]
                    sig = get_model(date).objects.get(id=id).dspam_sig
                except Exception, e:
                    sig = ''

                dspamc(file_path=mail_path, report='spam', sig=sig)
                outinfo('{}: imap reject'.format(mail))

                try:
                    os.remove(mail_path)
                except:
                    outerror('remove error: {}'.format(mail))
                    outerror(traceback.format_exc())
            except BaseException as e:
                outerror('exception: {}'.format(mail))
                outerror(traceback.format_exc())


def dspam_reject(key, get_model):
    rkey = '{}_reject'.format(key)
    tmp_rkey = '{}_reject_temp'.format(key)
    while True:
        try:
            j = redis.brpoplpush(rkey, tmp_rkey)
            date, id = j.split(',')[:2]
            mail = get_model(date).objects.get(id=id)
            if mail.check_result not in ['spam', 'virus'] and mail.mail_id == 0:
                dspamc(file_path=mail.get_mail_path(), report='spam', sig=mail.dspam_sig)
                mail.dspam_study = 1
                mail.customer_report = 2
                mail.save(update_fields=['dspam_study', 'customer_report'])
            redis.lrem(tmp_rkey, 0, j)
            outinfo('{}: {}'.format(rkey, j))
            if key.find('collect') == -1:
                _do_save_review_resutl(mail, 'reject')
        except BaseException as e:
            outerror('exception: {}'.format(j))
            outerror(traceback.format_exc())


def dspam_pass(key, get_model):
    rkey = '{}_pass'.format(key)
    tmp_rkey = '{}_pass_temp'.format(key)
    while True:
        try:
            j = redis.brpoplpush(rkey, tmp_rkey)
            date, id = j.split(',')[:2]
            mail = get_model(date).objects.get(id=id)
            if mail.mail_id == 0:
                dspamc(file_path=mail.get_mail_path(), report='innocent', sig=mail.dspam_sig)
                mail.dspam_study = 2
                mail.save(update_fields=['dspam_study'])
            redis.lrem(tmp_rkey, 0, j)

            # 将mail_id=0的邮件 保存到POP目录
            if mail.mail_id == 0:
                mail.save_mail_for_pop()
            outinfo('{}: {}'.format(rkey, j))
            if key.find('collect') == -1:
                _do_save_review_resutl(mail, 'pass')
        except BaseException as e:
            outerror('exception: {}'.format(j))
            outerror(traceback.format_exc())


def _do_save_review_resutl(mail, result):
    """
    ———自动审核———
    关键词/动态SPAM/高危邮件的审核策略调整：
    1、在X时间内，如果同一个发件人和同一个收件人连续X次通过/拒绝，则记住对应关系，下次直接放行/拒绝。
    2、这个规则不适合多个收件人
    3、规则有效期为X天
    :param mail:
    :param resutl:
    :return:
    """
    check_list = ['subject_blacklist', 'keyword_blacklist', 'active_spam', 'high_risk']
    check_result = mail.check_result
    if check_result in check_list and mail.mail_id == 0 and not get_mail_model(mail.get_date()).objects.filter(
            mail_id=mail.id):
        _save_review_result(mail.mail_from, mail.mail_to, result, check_result)


def _save_review_result(sender, receiver, result, step):
    """
    :param redis:
    :param sender:
    :param receiver:
    :param result: 'pass' or 'reject'
    """

    lua = redis.register_script('''
        local sender_receiver, result, time = ARGV[1], ARGV[2], tonumber(ARGV[3])
        local a, b

        a = redis.call('hget', KEYS[1], sender_receiver)
        if a then
            b = cjson.decode(a)
            if b.result == result then
                table.insert(b.history, time)
            else
                b = {result = result, history = {time}}
            end
        else
            b = {result = result, history = {time}}
        end
        redis.call('hset', KEYS[1], sender_receiver, cjson.encode(b))
    ''')
    key = 'relay_review_history:{}'.format(step)

    lua(keys=[key],
        args=['{},{}'.format(sender, receiver), result, time.time()])


def init():
    while redis.rpoplpush('dspam_reject_temp', 'dspam_reject') is not None:
        pass
    while redis.rpoplpush('dspam_pass_temp', 'dspam_pass') is not None:
        pass
    while redis.rpoplpush('dspam_collect_reject_temp', 'dspam_collect_reject') is not None:
        pass
    while redis.rpoplpush('dspam_collect_pass_temp', 'dspam_collect_pass') is not None:
        pass


def main():
    init()
    gevent.joinall([
        gevent.spawn(dspam_reject, 'dspam', get_mail_model),
        gevent.spawn(dspam_pass, 'dspam', get_mail_model),
        gevent.spawn(dspam_reject, 'dspam_collect', get_collect_mail_model),
        gevent.spawn(dspam_pass, 'dspam_collect', get_collect_mail_model),
        gevent.spawn(dspam_reject_from_path, settings.DATA_DSPAM_PATH, get_mail_model),
        gevent.spawn(dspam_reject_from_path, settings.DATA_COLLECT_DSPAM_PATH, get_collect_mail_model)
    ])


if __name__ == "__main__":
    globals()['_DEBUG'] = Common.check_debug()
    Common.init_cfg_default()
    Common.init_run_user(Common.cfgDefault.get('global', 'user'))
    Common.init_makedir()
    Common.init_pid_file('Dspam.pid')
    Common.init_logger('Dspam', len(sys.argv) > 1, _DEBUG)

    # 运行程序
    EXIT_CODE = 0
    outinfo("program start")
    main()
    outinfo("program quit")
    sys.exit(EXIT_CODE)
