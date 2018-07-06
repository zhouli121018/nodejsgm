#coding=utf-8

import logging
import datetime
import time
import random


from django.http import Http404
from django.db import models
from django.conf import settings

from app.core.models import CoreMssSmtpAcct, Prefs

def get_service_obj_check(request):
    service_obj = request.user.service()
    if service_obj.is_share_flag in('3', '4'):
        raise Http404
    return service_obj

def get_object(model, customer, pk):
    """
    获取customer所有的model对象
    :param model:
    :param customer:
    :param pk:
    :return:
    """
    try:
        return model.objects.get(customer=customer, pk=pk)
    except:
        try:
            return model.objects.get(user=customer, pk=pk)
        except:
            raise Http404

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class ZeroDateTimeField(models.DateTimeField):
    def get_db_prep_value(self, value, connection, prepared=False):
        # Casts datetimes into the format expected by the backend
        if not prepared:
            value = self.get_prep_value(value)

        # Use zeroed datetime instead of NULL
        if value is None:
            return  "0000-00-00 00:00:00"
        else:
            return connection.ops.adapt_datetimefield_value(value)
            # return connection.ops.value_to_db_datetime(value)

def get_smtp_acct(receiver):
    domain = receiver.split('@')[-1]
    lists = CoreMssSmtpAcct.objects.filter(domain__icontains=domain)
    # obj = CoreMssSmtpAcct.objects.filter(domain__icontains=domain).first()
    if lists:
        obj = random.choice(lists)
        host, port, account, password = obj.server, obj.port, obj.account, obj.password
    else:
        existsObj = CoreMssSmtpAcct.objects.filter(default='Y')[:1]
        obj = existsObj[0]
        host, port, account, password = obj.server, obj.port, obj.account, obj.password
    return host, port, account, password

def get_smtp_sys_acct(receiver):
    # SMTP服务器 设置
    m_server, _ = Prefs.objects.get_or_create(name='mail_server')
    mail_server = m_server.value
    # SMTP服务器端口 设置
    m_port, _ = Prefs.objects.get_or_create(name='mail_port')
    mail_port = int(m_port.value)
    # SMTP服务器 邮箱帐号 设置
    m_from, _ = Prefs.objects.get_or_create(name='mail_from')
    mail_from = m_from.value
    # SMTP服务器 邮箱密码 设置
    m_passwd, _ = Prefs.objects.get_or_create(name='mail_from_password')
    mail_from_password = m_passwd.value

    if mail_server and mail_port and mail_from and mail_from_password:
        return mail_server, mail_port, mail_from, mail_from_password
    else:
        return get_smtp_acct(receiver)

def set_session_lang(request, response):
    lang_code = request.user.lang_code
    if request.LANGUAGE_CODE != lang_code:
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
        max_age = 60*60*24*365
        expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code, max_age, expires)
    return response


# 日志输出函数
def outinfo(msg): outlog(msg, logging.INFO)


def outerror(msg): outlog(msg, logging.ERROR)


def outdebug(msg): outlog(msg, logging.DEBUG)


def outlog(m, t): logging.log(t, m)

# 安全调用对象
def safe_call(fn, *args, **kwargs) :
    try :
        return fn(*args, **kwargs)
    except Exception, e:
        outerror('call "%s" failure\n %s' % (fn.__name__, e.message))
        return None

# 等待调用成功 (有超时时间)
def time_call(fn, *args, **kwargs) :
    try_count = 3
    while try_count > 0 :
        res = safe_call(fn, *args, **kwargs)
        if res is not None:
            return res
        outerror('try call "%s" count: %d' % (fn.__name__, try_count))
        try_count -= 1
        time.sleep(0.5)
    return

# 等待调用成功 (无超时时间)
def wait_call(fn, *args, **kwargs) :
    while True :
        res = safe_call(fn, *args, **kwargs)
        if res is not None:
            return res
        time.sleep(0.5)
    return

def set_import_status(obj, status):
    obj.status = '{}'.format(int(status))
    obj.save(update_fields=['status'])
    return True

class ExcuterOrderCounter():
    def __init__(self, size=2):
        self.start_at = -1
        self.size = size

    def __call__(self, *args, **kwargs):
        self.start_at += 1
        if self.start_at == self.size - 1:
            self.start_at = -1
        return self.start_at