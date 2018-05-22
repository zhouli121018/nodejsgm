# !/usr/local/u-mail/app/engine/bin/python
# -*-coding:utf8-*-
#

import sys


import json
import os
import traceback
import time
import datetime
import re
import random

import gevent
import gevent.pool
from gevent import monkey

import lib.common         as Common

monkey.patch_socket()
Common.init_django_enev()
# from redis_cache import get_redis_connection
from lib.django_redis import get_redis
from django.conf import settings
from django.db import DatabaseError, InterfaceError, connection

data_path = settings.DATA_PATH
mails_path = settings.DATA_MAILS_PATH
rcpts_path = settings.DATA_RCPTS_PATH
froms_path = settings.DATA_FROMS_PATH
error_path = settings.DATA_ERROR_PATH
server_id = settings.SERVER_ID

# from lib.ModMailOperate import get_mail_subject
from lib.parse_email import ParseEmail
from lib.validators import check_email_format, is_same_domain

from lib.common import outinfo, outerror
from apps.mail.models import get_mail_model, install_model, InvalidMail, RecipientBlacklist, ValidMailSuffix, \
    InvalidSenderWhitelist
from apps.core.models import CustomerSetting

# ###########################################################
# 公共数据
addr_reg = re.compile("(?:^.+<(.+)>$)|(?:^<(.+)>$)|(?:^(.+)$)")
addr_get = lambda x: "".join(addr_reg.findall(x)[0])

# redis_queue_name
#MAIL_INCHECK_QUEUE = 'relay_incheck'
MAIL_INCHECK_QUEUE = ['relay_incheck', 'relay_incheck_bak']

# 退信队列
MAIL_BOUNCE_QUEUE = 'control_bounce'

# 对象
# redis = get_redis_connection('default')
redis = get_redis()

# 变量
_DEBUG = False
signal_stop = False
_MAXTHREAD = 1
_threads = []
_dates = []
# 收件人黑名单
recipient_blacklist = []
#有效域名后缀列表
suffix_list = []
#无效地址发件人白名单
invalidsender_whitelist = []
#需要替换真实发件人的客户
replace_sender_customers = []


# ###########################################################
# 处理器

def check_invalid_mail(rcpt):
    return InvalidMail.objects.filter(mail=rcpt.lower()).exists()


def is_contains(name, list):
    for r in list:
        if re.search(r, name, re.IGNORECASE | re.UNICODE):
            return True
    return False

def replace_sender(message, sender):
    message_object = email.message_from_string(message)
    if 'From' in message_object:
        name, old_sender = email.utils.parseaddr(message_object['From'])
        message_object.replace_header('From', email.utils.formataddr((name, sender)))
    else:
        message_object.add_header('From', sender)
    return message_object.as_string()


class Processor(object):
    def __init__(self, task):
        self.task = task
        self.mail_path = os.path.join(mails_path, task)
        self.rcpt_path = os.path.join(rcpts_path, task)
        self.from_path = os.path.join(froms_path, task)

    # 运行处理器
    def run(self):
        if not os.path.exists(self.mail_path):
            return

        date = time.strftime('%Y%m%d')
        #创建django的mail模型
        mail_model = get_mail_model(date)
        if date not in _dates:
            install_model(mail_model)
            #创建的目录　用户组也有权限修改
            Common.make_dir([os.path.join(data_path, date)], permit=0775)
            _dates.append(date)

        uid, mail_id, client_ip = self.task.split(',')[:3]

        with open(self.mail_path) as f:
            email_str = f.read()

        with open(self.from_path) as f:
            mail_from = f.read()
        mail_from = mail_from.split('=')[-1]

        with open(self.rcpt_path) as f:
            rcpt_list = f.readlines()

        # subject = get_mail_subject(mail_data=email_str)
        p = ParseEmail(email_str)
        if int(uid) in replace_sender_customers:
            email_str = p.replace_sender(mail_from)
        subject = p.get_attr('subject')
        try:
            sender_name = re.search('(.*?)\(.*?\)', p.get_attr('from')).group(1)
        except:
            outerror('get sender_name error: {}'.format(self.task))
            outerror(traceback.format_exc())
            sender_name = ''

        data = p.parseMailTemplate()

        attaches = data.get('attachments', [])
        try:
            attach_name = u'----'.join([a.get('decode_name', '') for a in attaches])
        except:
            outerror('get attach_name error: {}'.format(self.task))
            outerror(traceback.format_exc())
            attach_name = ''


        #被推送到检测队列中的邮件
        #当有多个收件人时, 只推送mail_id=0的一个对象到检测队列
        #mail_id=0一定不是无效地址中的邮件, 如果都在无效地址中, check_mail=None, 则无邮件推送到检测队列
        check_mail = None
        outinfo(self.task)
        outinfo('rcpt_list:{}'.format(rcpt_list))
        #mail id列表
        mail_ids = []
        is_white = is_contains(mail_from, invalidsender_whitelist)

        for rcpt in rcpt_list:
            if rcpt == '': continue
            # remove \n
            rcpt = rcpt.replace('\n', '')
            # 去掉字符串中的引号
            #rcpt = rcpt.replace('"', '').replace("'", "")

            rcpt = addr_get(rcpt)

            try:
                mail_obj = mail_model(customer_id=uid, mail_from=mail_from.lower(), mail_to=rcpt.lower(), client_ip=client_ip,
                                      subject=subject, size=len(email_str), sender_name=sender_name, server_id=server_id, attach_name=attach_name)
                mail_obj.save()
            except (DatabaseError, InterfaceError), e:
                outerror(traceback.format_exc())
                continue

            with open(mail_obj.get_mail_path(), 'w') as f:
                f.write(email_str)

            filename = mail_obj.get_mail_filename()

            if not check_email_format(rcpt, suffix_list) or is_same_domain(rcpt, mail_from):
                outinfo('{}: error format'.format(filename))
                self._do_invalid_mail(mail_obj, 'error_format')
            elif not is_white and check_invalid_mail(rcpt):
                outinfo('{}: invalid mail'.format(filename))
                self._do_invalid_mail(mail_obj, 'invalid_mail')
            elif is_contains(rcpt, recipient_blacklist):
                outinfo('{}: recipient blacklist'.format(filename))
                self._do_invalid_mail(mail_obj, 'recipient_blacklist')
            else:
                outinfo('{}: pass'.format(filename))
                if not check_mail:
                    check_mail = mail_obj

            mail_ids.append(mail_obj.id)

        if check_mail:
            mail_id = check_mail.id
        else:
            mail_id = mail_ids[0]
        mail_model.objects.filter(id__in=mail_ids).exclude(id=mail_id).update(mail_id=mail_id)
        #只有第一封邮件 推送到待检测队列
        if check_mail:
            #redis.lpush(MAIL_INCHECK_QUEUE, check_mail.get_mail_filename())
            redis.lpush(random.choice(MAIL_INCHECK_QUEUE), check_mail.get_mail_filename())


        # remove original mail and rcpt file
        try:
            os.remove(self.mail_path)
            os.remove(self.rcpt_path)
            os.remove(self.from_path)
        except BaseException as e:
            outerror('remove error: {}'.format(self.task))
            outerror(traceback.format_exc())
        return


    def _do_invalid_mail(self, mail_obj, check_result):
        rcpt = mail_obj.mail_to
        return_message = 'unknown user: {}'.format(rcpt)
        mail_obj.check_result = check_result
        #mail_obj.review_result = 'reject'
        mail_obj.return_message = return_message
        mail_obj.state = 'bounce'
        mail_obj.error_type = 2
        mail_obj.save()
        bounce_dict = {
            'mail_ident': mail_obj.get_mail_filename(),
            'sender': mail_obj.mail_from,
            'receiver': rcpt,
            'deliver_ip': '202.103.191.28',
            'result': [{
                           'deliver_time': str(datetime.datetime.now()),
                           'mx_record': '',
                           'receive_ip': '',
                           'return_code': 550,
                           'return_message': return_message
                       }]
        }

        redis.lpush(MAIL_BOUNCE_QUEUE, json.dumps(bounce_dict))

    def handle_error(self):
        try:
            error_file = os.path.join(error_path, self.task)
            os.rename(self.mail_path, error_file)
        except:
            outerror('handle error:{}'.format(self.task))
            outerror(traceback.format_exc())


############################################################
# 线程

# 任务执行线程
def worker(task):
    p = Processor(task)
    try:
        with gevent.Timeout(60):
            p.run()
    except gevent.Timeout, e:
        p.handle_error()
        outerror('Process timeout:{}'.format(task))
        outerror(traceback.format_exc())
    except (DatabaseError, InterfaceError), e:
        #如果报数据库异常，关闭连接，重新处理任务
        outerror('DatabaseError: {}'.format(task))
        outerror(traceback.format_exc())
        p.handle_error()
        connection.close()
        gevent.sleep(2)
    except:
        p.handle_error()
        outerror('Process error:{}'.format(task))
        outerror(traceback.format_exc())
    _threads.remove(task)
    return


# 队列扫描管理线程
def scanner():
    pool = gevent.pool.Pool(_MAXTHREAD)

    while True:
        if signal_stop: break
        mails = os.listdir(mails_path)
        if not mails:
            gevent.sleep(1)
            continue
        for mail in mails:
            if signal_stop:
                outinfo('signal stop')
                break
            if mail in _threads:
                gevent.sleep(0.1)
                continue
            _threads.append(mail)
            pool.spawn(worker, mail)
            gevent.sleep(0.001)

    outinfo('waiting stop...')
    pool.join()
    return


############################################################
#初始化全局变量
def init_resource():
    global recipient_blacklist, suffix_list, invalidsender_whitelist, replace_sender_customers
    recipient_blacklist = RecipientBlacklist.objects.filter(disabled=False).values_list('keyword', flat=True)
    invalidsender_whitelist = InvalidSenderWhitelist.objects.filter(disabled=False).values_list('sender', flat=True)
    invalidsender_whitelist = map(lambda a: a.replace('\r', ''), invalidsender_whitelist)
    suffix_list = ValidMailSuffix.objects.filter(disabled=False).values_list('keyword', flat=True)
    suffix_list = map(lambda a: a.replace('\r', ''), suffix_list)
    replace_sender_customers = CustomerSetting.objects.filter(replace_sender=True).values_list('customer_id', flat=True)


def init_resource_routine():
    while True:
        try:
            outinfo('init resouce routine')
            init_resource()
        except BaseException as e:
            outerror('init_resource_routine exception')
        gevent.sleep(600)


############################################################

# 信号量处理
def signal_handle(mode):
    outinfo("catch signal: %s" % mode)
    global signal_stop
    signal_stop = True
    # for task_id in _threads:
    #     outinfo('task back to queue: %s' % task_id)
    #     redis.rpush(MAIL_INCHECK_QUEUE, task_id)
    # if mode != 'sigint': sys.exit(0)

############################################################

if __name__ == "__main__":
    globals()['_DEBUG'] = Common.check_debug()
    Common.init_cfg_default()
    Common.init_run_user(Common.cfgDefault.get('global', 'user'))
    Common.init_makedir()
    Common.make_dir([mails_path, rcpts_path, error_path, froms_path])
    Common.init_pid_file('HandleMail.pid')
    Common.init_logger('HandleMail', len(sys.argv) > 1, _DEBUG)

    init_resource()
    gevent.spawn(init_resource_routine)

    # 运行程序
    EXIT_CODE = 0
    outinfo("program start")
    try:
        # 设置监听信号量
        Common.gevent_signal_init(signal_handle)

        scanner()
    except KeyboardInterrupt:
        signal_handle('sigint')
    except:
        outerror(traceback.format_exc())
        EXIT_CODE = 1
    outinfo("program quit")
    sys.exit(EXIT_CODE)
