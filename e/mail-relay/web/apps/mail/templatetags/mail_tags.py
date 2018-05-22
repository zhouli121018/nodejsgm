# coding=utf-8
import datetime

import re
from django.utils import timezone
from django import template
from apps.mail.models import get_mail_model, Statistics, BulkCustomer, TempSenderBlacklist
from apps.core.models import RouteRule
from apps.collect_mail.models import get_mail_model as get_col_mail_model, Statistics as ColStatistics
from lib.django_redis import get_redis
import json
from apps.collect.models import ColCustomer
from django.conf import settings
import base64

register = template.Library()


@register.filter
def preview_check(filname):
    # allow_suffix = ( 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tif', 'tiff', 'xbm', 'xpm',
    # 'doc', 'docx', 'dot', 'dotx',
    #                  'ppt', 'pptx', 'pps', 'ppsx', 'pot', 'potx',
    #                  'xls', 'xlsx', 'xlt', 'xltx'
    # )
    allow_suffix = ( 'jpg', 'jpeg', 'png', 'gif', 'bmp')
    suffix = filname.split('.')[-1]
    suffix = suffix.lower()
    return suffix in allow_suffix


@register.filter
def list_sum(list, key):
    return sum([l.get(key, 0) for l in list])


@register.filter
def get_mail_count(mail_obj, date):
    model = get_mail_model(date.replace('-', ''))
    mail_id = mail_obj.mail_id if mail_obj.mail_id else mail_obj.id
    return model.objects.filter(mail_id=mail_id).count() + 1


@register.filter
def get_send_info(obj, type):
    date = datetime.date.today()
    msg = u"""<span>总共:<a href='/mail/mail_list?show=sendlog&{type}={value}'>{count}</a>
    成功:<a href='/mail/mail_list?show=sendlog&send=success&{type}={value}'>{success}</a>
    成功率:<code>{rate}</code>%
    </span></br>
    <a href='/mail/statistics?{type}={value}&type={type}'><code>查看历史详情</code></a>
    """

    class DefaultS:
        count = 0
        success = 0
        rate = 0

    s = DefaultS()
    objs = []
    if type == 'customer':
        objs = Statistics.objects.filter(date=date, customer=obj)
    if type == 'cluster':
        objs = Statistics.objects.filter(date=date, cluster=obj)
    if type == 'ip':
        objs = Statistics.objects.filter(date=date, ip=obj.ip)
    if type == 'ip_pool':
        objs = Statistics.objects.filter(date=date, ip_pool=obj)

    if objs:
        s = objs[0]
    rs = {
        'type': type,
        'value': obj.id if type != 'ip' else obj.ip,
        'count': s.count,
        'success': s.success,
        'rate': '%.2f' % s.rate,
    }
    return msg.format(**rs)

@register.filter
def get_col_send_info(obj, type):
    date = datetime.date.today()
    msg = u"""
    <span>总:<a href='/collect_mail/mail_list?{type}={value}'>{total}</a>
    拒:<a href='/collect_mail/mail_list?{type}={value}&review=reject'>{total_reject}</a>
    <span>发:<a href='/collect_mail/mail_list?show=sendlog&{type}={value}'>{count}</a>
    成:<a href='/collect_mail/mail_list?show=sendlog&send=success&{type}={value}'>{success}</a>
    垃圾过滤率:<code>{rate}</code>%
    </span></br>
    <a href='/collect_mail/statistics?{type}={value}&type={type}'><code>查看历史详情</code></a>
    """

    class DefaultS:
        count = 0
        success = 0
        rate = 0
        total = 0
        total_reject = 0

    s = DefaultS()
    model = get_col_mail_model(date.strftime('%Y%m%d'))

    if type == 'customer':
        try:
            s = ColStatistics.objects.get(date=date, customer=obj)
            s.total = model.objects.filter(customer=obj).count()
        except:
            s.total = 0
        try:
            s.total_reject = model.objects.filter(customer=obj, review_result='reject').count()
        except:
            s.total_reject = 0
    rs = {
        'total': s.total,
        'total_reject': s.total_reject,
        'type': type,
        'value': obj.id if type != 'ip' else obj.ip,
        'count': s.count,
        'success': s.success,
        'rate': '%.2f' % (float(s.total_reject) * 100 / float(s.total)) if s.total else 0,
    }
    return msg.format(**rs)


@register.filter
def get_auto_review_rate(d):
    check_dict = d.get('check', {})
    auto_reveiw_count = check_dict.get('auto_pass', 0) + check_dict.get('auto_reject', 0)
    check_count = check_dict.get('subject_blacklist', 0) + check_dict.get('keyword_blacklist', 0) + check_dict.get(
        'active_spam', 0) + check_dict.get('high_risk', 0) + auto_reveiw_count
    return '%.2f' % (float(auto_reveiw_count) * 100 / float(check_count)) if check_count else 0

@register.filter
def get_route_rule_count(pool, type):
    return RouteRule.objects.filter(ip_pool=pool, type=type).count()

@register.filter
def get_check_result_display(msg):
    if msg.find(u'----') != -1:
        re_s, s = msg.split(u'----', 1)
        return re.sub(u'(?P<name>{})'.format(re_s), u'<span class="text-danger">\g<name></span>', s)
    else:
        return u'<span class="text-danger">{}</span>'.format(msg)


@register.filter
def get_recent_bulk_customer(c, day):
    date = c.date - datetime.timedelta(days=day)
    try:
        cus = BulkCustomer.objects.filter(date=date, customer=c.customer)
        return cus[0] if cus else None
    except:
        return None


@register.filter
def get_sender_black(sender):
    objs = TempSenderBlacklist.objects.filter(sender=sender, expire_time__gt=datetime.datetime.now())
    if objs:
        return objs[0].expire_time - timezone.now()
    else:
        return False

@register.filter
def get_rate(value1, value2):
    return '%.2f' % (float(value1) * 100 / float(value2)) if value2 else 0

@register.filter('timestamp_to_time')
def convert_timestamp_to_time(timestamp):
    return datetime.date.fromtimestamp(int(timestamp))

@register.filter
def get_div(value1, value2):
    return '%.0f' % (float(value1) / float(value2)) if value2 else 0


@register.filter
def get_dispatch_status(obj):
    msg = u"""队列大小:<code>{queue_size}</code> 线程数:<code>{pool_size}</code><br/> 通讯异常时间:<code>{exception_time}</code>"""
    redis = get_redis()
    ip = obj.ip
    try:
        status_dict = json.loads(redis.get('control_dispatch_state'))
    except:
        status_dict = {}
    rs = {
        'queue_size': status_dict.get(ip, {}).get('queue_size', 0),
        'pool_size': status_dict.get(ip, {}).get('pool_size', 0),
        'exception_time': status_dict.get(ip, {}).get('exception_time', 0)
    }
    return msg.format(**rs)

@register.filter
def split_tag(s, split_s):
    if s:
        l = s.split(split_s)
        return len(l), ','.join(l)
    return 0, ''

@register.filter
def get_web_server(server_id):
    server = server_id.upper()
    server = '{}'.format( getattr(settings, 'WEB_{}'.format(server)) )
    return server

@register.filter
def get_user_web_server(server_id):
    server = server_id.upper()
    server = '{}'.format( getattr(settings, 'WEB_USER_SHENZHEN') )
    return server

@register.filter
def get_private_key(date_id):
    key = base64.b64encode('MAILDOWNLOAD' + '_' + date_id)
    return key

@register.filter
def get_base64_key(word):
    key = base64.b64encode(str(word))
    return key

@register.filter
def parse_file_format(attach_name):
    suffix = attach_name.split('.')[-1]
    suffix = suffix.lower()
    if suffix in ['doc', 'docx', 'dotx', 'docm', 'dot', 'docm', 'dotm', 'rtf', 'wps']:
        # word 文件
        return '1'
    elif suffix in ['xls', 'xlsx', 'xlsm', 'xltx', 'xltm', 'xlsb', 'xlam']:
        # excel 文件
        return '2'
    elif suffix in ['ppt', 'pptx', 'pptm', 'ppsx', 'ppsx', 'potx', 'potm', 'ppam']:
        # ppt 文件
        return '3'
    elif suffix in ['gif', 'pcd', 'psd', 'pcx', 'png', 'dxf', 'cdr', 'jpg', 'bmp', 'dwg', 'pic', 'tif']:
        # 图像文件
        return '4'
    elif suffix in ['zip', 'tar', 'rar', 'arj', 'lzh', 'jar', 'gz', 'z']:
        # 压缩文件
        return '5'
    elif suffix in ['wav', 'aif', 'au', 'mp3', 'ram', 'wma', 'mmf', 'amr', 'aac', 'flac', 'avi', 'mpg', 'mov', 'swf', 'mp4', 'rm', 'rmvb', 'wmv', 'vob', 'h264', 'mjpeg', 'xvid', 'divx', 'flv', 'dvd', 'vcd', 'svcd']:
        # 声音文件 视频文件
        return '6'
    elif suffix in ['txt', 'xps', 'text', 'css', 'c', 'asm', 'for', 'lib', 'lst', 'msg', 'obj', 'pas', 'wki','bas', 'py', 'pyc', 'pyo', 'cpp', 'hpp', 'h', 'java']:
        # txt 文件
        return '7'
    elif suffix in ['html', 'xml', 'mht', 'mhtml', 'jsp']:
        return '8'
    elif suffix == 'pdf':
        return '9'
    elif suffix == 'eml':
        return '10'
    else:
        return '11'

@register.filter
def get_domain(mail):
    return mail.split('@')[-1]

@register.filter
def get_temp_sender_blacklist(mail_from):
    return TempSenderBlacklist.objects.filter(sender=mail_from, expire_time__gt=datetime.datetime.now()).first()
