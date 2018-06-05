# coding=utf-8
from django import template
from app.perm.models import MyPermission
register = template.Library()

@register.inclusion_tag('perm/perm_nav.html')
def show_nav(perms):
    mypermissions = MyPermission.objects.filter(parent__isnull=True, is_nav=True).order_by('order_id')
    class_list = ['fa-sitemap', 'fa-globe', 'fa-tags', 'fa-bar-chart-o', 'fa-user', 'fa-legal', 'fa-gear', 'fa-envelope fa-cny', 'fa-lightbulb-o', 'fa-flag', 'fa-exchange', 'fa-cloud-upload', 'fa-dashboard']
    return {
        'perms': perms,
        'mypermissions': mypermissions,
        'class_list': class_list
    }

@register.filter
def permission_order_by(objs):
    return objs.order_by('-is_nav', 'order_id')

@register.filter
def get_index(list, index):
    length = len(list)
    index = int(index)
    while index >= length:
        index -= length
    return list[index]


