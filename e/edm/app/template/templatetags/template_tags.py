# coding=utf-8
import time
from django import template
from app.template.models import ShareTemplte
from app.template.utils import formats
from django.utils.translation import ugettext_lazy as _
register = template.Library()

@register.filter
def show_content_type(content_type):
    if content_type == 1:
        return 'html'
    elif content_type == 2:
        return 'eml'
    else:
        return ''

@register.filter(is_safe=True)
def filesizeformat(bytes):
    return formats.filesizeformat(bytes)

@register.filter(is_safe=True)
def show_format_size(obj):
    size = 0
    if obj.content:
        size += len(obj.content)
    if obj.text_content:
        size += len(obj.text_content)
    return filesizeformat(size)

@register.filter
def get_subject_ids(subject_objs):
    subject_ids = ''
    for obj in subject_objs:
        if subject_ids:
            subject_ids = subject_ids + ',' + str(obj.id)
        else:
            subject_ids = str(obj.id)
    return subject_ids

@register.filter
def show_test_time(test_time):
    if test_time:
        test_time = int(test_time)
        test_time += 3600 * 8 # 数据库取出时间戳 需加8个小时
        return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(test_time))
    return ''

@register.filter
def show_template_name(obj):
    if obj.name:
        return obj.name
    return _(u'未命名模板')

@register.assignment_tag
def is_share_template(template_id, user_id):
    return ShareTemplte.objects.filter(template_id=template_id, user_id=user_id).exists()
