# coding=utf-8
import datetime
from django import template

register = template.Library()


@register.filter
def attr_from_domain_id(attrs, domain_id):
    attrs = attrs.filter(domain_id=domain_id)
    return attrs.first() if attrs else None

