# coding=utf-8
import datetime
import re
from django import template
from django.conf import settings
from apps.collect_mail.models import get_mail_model, Statistics
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
    return suffix in allow_suffix


@register.filter
def list_sum(list, key):
    return sum([l.get(key, 0) for l in list])


@register.filter
def get_cmail_count(mail_obj, date):
    model = get_mail_model(date.replace('-', ''))
    mail_id = mail_obj.mail_id if mail_obj.mail_id else mail_obj.id
    return model.objects.filter(mail_id=mail_id).count() + 1

@register.filter
def get_send_info(obj, type):
    date = datetime.date.today()
    msg = u"""
    <span>总:<a href='/collect_mail/mail_list?{type}={value}'>{total}</a>
    拒:<a href='/collect_mail/mail_list?{type}={value}&review=reject'>{total_reject}</a>
    <span>发:<a href='/collect_mail/mail_list?show=sendlog&{type}={value}'>{count}</a>
    成:<a href='/collect_mail/mail_list?show=sendlog&send=success&{type}={value}'>{success}</a>
    成功率:<code>{rate}</code>%
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
    objs = []
    model = get_mail_model(date.strftime('%Y%m%d'))
    if type == 'customer':
        objs = Statistics.objects.filter(date=date, customer=obj)

    if objs:
        s = objs[0]

    if type == 'customer':
        try:
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
        'rate': '%.2f' % s.rate,
    }
    return msg.format(**rs)

@register.filter
def get_check_result_display(msg):
    if msg.find(u'----') != -1:
        re_s, s = msg.split(u'----', 1)
        return re.sub(u'(?P<name>{})'.format(re_s), u'<span class="text-danger">\g<name></span>', s)
    else:
        return u'<span class="text-danger">{}</span>'.format(msg)


@register.filter
def get_deliver_auth_key(date_id):
    action = 'deliver'
    word = action + '_' + date_id
    return md5_encrypt(word)

@register.filter
def get_whitelist_auth_key(date_id):
    action = 'whitelist'
    word = action + '_' + date_id
    return md5_encrypt(word)

@register.filter
def get_delete_auth_key(date_id):
    action = 'delete'
    word = action + '_' + date_id
    return md5_encrypt(word)

def md5_encrypt(word):
    encoded = base64.b64encode(settings.PRIVATE_SPAM_RPT_STR + '_' + word)
    return encoded


@register.filter
def get_spam_rpt_server(server_id):
    server = server_id.upper()
    server = '{}'.format( getattr(settings, 'WEB_{}'.format(server)) )
    return server

