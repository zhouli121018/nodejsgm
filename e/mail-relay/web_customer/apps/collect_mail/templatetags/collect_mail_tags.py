# coding=utf-8
from django import template
from apps.collect_mail.models import get_mail_model

register = template.Library()


@register.filter
def c_get_mail_count(mail_obj, date):
    model = get_mail_model(date.replace('-', ''))
    mail_id = mail_obj.mail_id if mail_obj.mail_id else mail_obj.id
    return model.objects.filter(mail_id=mail_id).count() + 1



