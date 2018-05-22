# coding=utf-8

from app.setting.models import NoticeSetting, NoticeSettingDetail

from django import template
register = template.Library()

@register.filter
def show_token(token):
    while token:
        return token[:12] + u'*******' + token[19:]
    return ''


@register.assignment_tag
def get_notice_flag(notice_id, notice_type):
    notice_obj = NoticeSetting.objects.filter(id=notice_id).first()
    if notice_obj:
        d_obj, _created = NoticeSettingDetail.objects.get_or_create(setting=notice_obj, type=notice_type)
        return {
            'is_notice': d_obj.is_notice,
            'is_email': d_obj.is_email,
            'is_sms': d_obj.is_sms,
        }
    return {
        'is_notice': False,
        'is_email': False,
        'is_sms': False,
    }

import re
from decimal import Decimal
from django.utils.encoding import force_text

@register.filter(is_safe=True)
def intcomma2(value, haserror=True):
    """
    Converts an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000' and 45000 becomes '45,000'.
    """
    if haserror:
        try:
            if not isinstance(value, (float, Decimal)):
                value = int(value)
        except (TypeError, ValueError):
            return intcomma2(value, False)
    orig = force_text(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', orig)
    if orig == new:
        return new
    else:
        return intcomma2(new, False)