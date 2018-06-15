# coding=utf-8
import os

import re
import time
import datetime
import uuid
import subprocess
import random
import string
import dns.resolver
from django.db import models

#dns.resolver.get_default_resolver().cache = dns.resolver.LRUCache()
SEEDS = string.ascii_letters + string.digits


# 生成dkim 公私钥
def GenDkimKeys():
    """
    :return:
    """
    uuid_str = uuid.uuid1()
    private_file = '/tmp/private_{}'.format(uuid_str)
    publice_file = '/tmp/public_{}'.format(uuid_str)
    gen_private_cmd = 'openssl genrsa -out {} 1024'.format(private_file)
    gen_public_cmd = 'openssl rsa -in {} -out {} -pubout -outform PEM'.format(private_file, publice_file)
    p = subprocess.Popen(gen_private_cmd, shell=True)
    p.wait()
    p = subprocess.Popen(gen_public_cmd, shell=True)
    p.wait()
    with open(private_file, 'r') as fr:
        private_key = fr.read()
    with open(publice_file, 'r') as fr:
        publice_key = ''.join(fr.readlines()[1:-1]).replace('\n', '')
    os.unlink(private_file)
    os.unlink(publice_file)
    return private_key, publice_key


def try_query(qname, rdtype):
    try:
        rs = []
        answers = dns.resolver.query(qname, rdtype)
        for a in answers:
            if rdtype == 'mx':
                rs.append(a.exchange.to_text())
            elif rdtype in ['txt', 'cname']:
                rs.append(a.to_text())
            else:
                rs.append(a)
        return rs
    except dns.exception.DNSException:
        return []

def is_find_key(lists, key):
    if isinstance(lists, list):
        for l in lists:
            if l.find(key) != -1:
                return True
    return False

def valid_domain(domain, rdtype, record='', dkim_selector='umail'):
    """
    检测域名记录
    :param domain: 域名
    :param rdtype: 检测类型 mx, spf, dkim
    :param record: 数据库的记录
    :return:
    """
    if rdtype == 'spf':
        t_record = try_query(domain, 'txt')
        return is_find_key(t_record, record)
    if rdtype == 'mx':
        t_record = try_query(domain, 'mx')
        return record in t_record or '{}.'.format(record) in t_record
    if rdtype == 'dkim':
        t_record = try_query('{}._domainkey.{}'.format(dkim_selector, domain), 'txt')
        return t_record[0][1:-1] == record if t_record else False
    if rdtype == 'cname':
        t_record = try_query(domain, 'cname')
        return t_record[0].find(record) != -1 if t_record else False


# 生成随机字符串
def get_random_string(str_len=5):
    return ''.join(random.sample(SEEDS, str_len))

# 生成随机SMTP账号
def get_sys_smtp_mailbox(obj, domain):
    while True:
        name = get_random_string(random.randint(5, 15))
        # insert_index = random.randint(1,15)
        # special_chars = [ '_', '-'] + random.sample(SEEDS, 10)
        # special_char = random.choice(special_chars)
        # name = name[0:insert_index] + special_char + name[insert_index:0] + get_random_string(1)
        mailbox = '{}@{}'.format(name, domain)
        _e = obj.objects.filter(domain=domain, mailbox=mailbox).exists()
        if not _e:
            return name, mailbox

# 获取当天时间戳
def get_timestamp():
    now = datetime.datetime.now()
    t1 = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
    timestamp1 = int(time.mktime(t1.timetuple()))
    t2 = datetime.datetime(now.year, now.month, now.day, 23, 59, 59)
    timestamp2 = int(time.mktime(t2.timetuple()))
    timeStamp = int(time.mktime(now.timetuple()))
    return timeStamp, timestamp1, timestamp2


# 获取最近3天时间戳
def get_timestamp_last3days():
    now = datetime.datetime.now()
    daybefore3 = now - datetime.timedelta(days=3)
    t1 = datetime.datetime(daybefore3.year, daybefore3.month, daybefore3.day, 0, 0, 0)
    timestamp1 = int(time.mktime(t1.timetuple()))
    t2 = datetime.datetime(now.year, now.month, now.day, 23, 59, 59)
    timestamp2 = int(time.mktime(t2.timetuple()))
    timeStamp = int(time.mktime(now.timetuple()))
    return timeStamp, timestamp1, timestamp2


# 附近大小换算 MB KB
def file_size_conversion(size, unit):
    return size * 1.0000 / unit


def safe_format(template, **kwargs):
    def replace(mo):
        name = mo.group('name')
        if name in kwargs:
            return unicode(kwargs[name])
        else:
            return mo.group()

    p = r'\{(?P<name>\w+)\}'
    return re.sub(p, replace, template)


# 创建指定的多个路径
def make_dir(path_list, mode=0755):
    if type(path_list) == type(''): path_list = [path_list]
    for path in path_list:
        if os.path.exists(path): continue
        recursion_make_dir(path, mode)
    return True


# 递归创建路径
def recursion_make_dir(path, mode=0755):
    if path[0] != '/': return False
    path_list = os.path.realpath(path).split('/')[1:]
    path_full = ''
    for i in path_list:
        path_full += '/' + i
        if os.path.exists(path_full): continue
        os.mkdir(path_full, mode)
    return True


def gen_len_chars(s, length=8):
    while len(s) % length != 0: s += ' '
    return s

class ZeroDateTimeField(models.DateTimeField):
    def get_db_prep_value(self, value, connection, prepared=False):
        # Casts datetimes into the format expected by the backend
        if not prepared:
            value = self.get_prep_value(value)

        # Use zeroed datetime instead of NULL
        if value is None:
            return "0000-00-00 00:00:00"
        else:
            return connection.ops.adapt_datetimefield_value(value)
            # return connection.ops.value_to_db_datetime(value)

class ZeroDateField(models.DateField):
    def get_db_prep_value(self, value, connection, prepared=False):
        # Casts datetimes into the format expected by the backend
        if not prepared:
            value = self.get_prep_value(value)

        # Use zeroed datetime instead of NULL
        if value is None:
            return "0000-00-00"
        else:
            return connection.ops.adapt_datetimefield_value(value)
            # return connection.ops.value_to_db_datetime(value)


# 匹配浏览器是否满足最低版本号
def get_browser_version(agent, conflists):
    # regStr_ie = re.compile('(msie \d+)', re.I)
    # regStr_ff = re.compile('(firefox\/\d+)', re.I)
    # regStr_chrome = re.compile('(chrome\/\d+)', re.I)
    # regStr_saf = re.compile('(safari\/\d+)', re.I)
    if agent in (None, ''):
        return False

    flag = False
    for obj in conflists:
        rule = re.compile(obj.rule, re.I|re.U)
        m = rule.search(agent)
        if m:
            try:
                match = m.group(1)
                try:
                    version = m.group(2)
                    version = int(version)
                except:
                    try:
                        version = int(match)
                    except:
                        flag = False
                        continue
                flag = False if version < obj.version else True
                break
            except:
                flag = False
                continue

    return flag
    # return u'建议使用IE10+、最新版本的Chrome、Firefox、Safari、Opera浏览器登录使用本平台！'

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
