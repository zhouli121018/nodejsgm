# coding=utf-8
from django import template
from django.db import connections
from app.trigger.models import Trigger
from app.address.models import ShareMailList

register = template.Library()

@register.assignment_tag
def get_subscriber_count(list_id, user_id):
    try:
        cr = connections['mm-pool'].cursor()
        tablename = 'ml_subscriber_' + str(user_id)
        sql = "SELECT COUNT(1) FROM %s WHERE list_id=%d;" % (tablename, list_id)
        cr.execute(sql)
        data = cr.fetchone()
        count = data[0] if data else 0
    except:
        count = 0
    return count

@register.assignment_tag
def get_subscriber_true_count(list_id, user_id):
    try:
        cr = connections['mm-pool'].cursor()
        tablename = 'ml_subscriber_' + str(user_id)
        sql = "SELECT COUNT(1) FROM %s WHERE list_id=%d AND is_subscribe=1;" % (tablename, list_id)
        cr.execute(sql)
        data = cr.fetchone()
        count = data[0] if data else 0
    except:
        count = 0
    return count

@register.assignment_tag
def get_unsubscriber_count(list_id, user_id):
    try:
        cr = connections['mm-pool'].cursor()
        tablename = 'ml_unsubscribe_' + str(user_id)
        sql = "SELECT COUNT(1) FROM %s WHERE list_id=%d;" % (tablename, list_id)
        cr.execute(sql)
        data = cr.fetchone()
        count = data[0] if data else 0
    except:
        count = 0
    return count

@register.assignment_tag
def get_tr_odd_or_even(index):
    if index%2:
        return "odd"
    return "even"

@register.assignment_tag
def get_start_num(index, start_num):
    return int(index) + int(start_num) - 1

@register.filter
def get_trigger_for_list(list, user):
    return Trigger.getTriggerBylist(user.id, list.id)


@register.assignment_tag
def is_share_addrs(list_id, user_id):
    return ShareMailList.objects.filter(maillist_id=list_id, user_id=user_id).exists()
