# coding=utf-8
import datetime
import re
from django import template
from apps.mail.models import get_mail_model
from apps.core.models import ClusterIp, CustomerSetting

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
def get_mail_count(mail_obj, date):
    model = get_mail_model(date.replace('-', ''))
    mail_id = mail_obj.mail_id if mail_obj.mail_id else mail_obj.id
    return model.objects.filter(mail_id=mail_id).count() + 1


@register.filter
def get_cluster_from_ip(ip):
    objs = ClusterIp.objects.filter(ip=ip)
    res = ''
    if objs:
        res = objs[0].cluster.description
    return res if res else u'中继发送机'

@register.filter
def get_rate(part, total):
    try:
        part = float(part)
    except:
        part = 0.0
    if not total:
        return 0
    return '%.2f' % (part * 100 / float(total))

@register.filter
def can_view_msg(customer):
    obj = CustomerSetting.objects.get(customer=customer)
    return obj.can_view_mail
