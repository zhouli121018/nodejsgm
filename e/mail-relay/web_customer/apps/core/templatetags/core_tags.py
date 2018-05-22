# coding=utf-8
from django import template
from lib.IpSearch import IpSearch

from apps.core.models import  Notification

register = template.Library()

@register.inclusion_tag('base_notice.html')
def show_notice(request):
    notices = Notification.objects.filter(customer=request.user, is_read=False).order_by('created')
    count = notices.count()
    return {
        'notices': notices,
        'count': count,
    }

@register.filter
def get_ip_area(ip):
    try:
        qqzeng = IpSearch()
        result = ' '.join(qqzeng.Find(ip).split('|')[:6])
    except:
        result = ''
    return result
