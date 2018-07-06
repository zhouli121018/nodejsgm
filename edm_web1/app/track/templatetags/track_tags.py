# coding=utf-8
from django import template
from django.template.defaultfilters import date as dateformat

register = template.Library()

@register.filter
def show_trak_datetime(value):
    while value:
        return dateformat(value, "Y-m-d H:i:s")
    return "0000-00-00 00:00:00"

@register.filter
def show_trak_date(value):
    while value:
        return dateformat(value, "Y-m-d")
    return "0000-00-00"

@register.filter
def show_click_datetime(value):
    while value:
        return dateformat(value, "Y-m-d H:i:s")
    return "-"

@register.filter
def show_click_date(value):
    while value:
        return dateformat(value, "Y-m-d")
    return "-"

@register.filter
def get_rate(unique, total):
    while total:
        return "{}%".format(round( ( unique*100.00/total ), 2) )
    return '0%'
