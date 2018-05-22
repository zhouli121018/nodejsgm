# coding=utf-8
from django import template

from apps.core.models import MyPermission, Notification

register = template.Library()

@register.inclusion_tag('nav.html')
def show_nav(perms):
    mypermissions = MyPermission.objects.filter(parent__isnull=True, is_nav=True).order_by('order')
    class_list = ['fa-sitemap', 'fa-bar-chart', 'fa-twitter-square', 'fa-bell', 'fa-umbrella', 'fa-paste', 'fa-lightbulb-o', 'fa-exchange', 'fa-cloud-upload']
    return {
        'perms': perms,
        'mypermissions': mypermissions,
        'class_list': class_list
    }


@register.filter
def permission_order_by(objs):
    return objs.order_by('-is_nav', 'order')

@register.filter
def get_index(list, index):
    length = len(list)
    index = int(index)
    while index >= length:
        index -= length
    return list[index]

@register.inclusion_tag('base_notice.html')
def show_notice(request):
    notices = Notification.objects.filter(manager=request.user, is_read=False).order_by('created')
    count = notices.count()
    return {
        'notices': notices,
        'count': count,
    }
