# coding=utf-8

import json
from django.db.models import Sum, Max
from django_redis import get_redis_connection
from app.address.models import MailList

# 地址池合并后去重操作队列
EMD_WEB_MAIL_MERGE_QUEUE = 'edm_web_mail_merge_queue'



# 合并到新分类
def mergeNewMaillist(user_id, list_ids, list_ids_str, merge_type, category_name):
    obj = MailList.objects.create(customer_id=user_id, subject=category_name)
    list_id = obj.id
    mergeMaillistCommon(user_id, list_id, list_ids, list_ids_str, merge_type)

# 合并分类
def mergeMaillist(user_id, list_id, list_ids, list_ids_str, merge_type):
    list_id = int(list_id)
    mergeMaillistCommon(user_id, list_id, list_ids, list_ids_str, merge_type)


def mergeMaillistCommon(user_id, list_id, list_ids, list_ids_str, merge_type):
    j = json.dumps({
        'user_id': user_id,
        'list_id': list_id,
        'list_ids': list_ids,
        'list_ids_str': list_ids_str,
        'merge_type': merge_type,
    })

    values = MailList.objects.filter(id__in=list_ids).aggregate(
        count_all=Sum('count_all'),
        count_err=Sum('count_err'),
        count_real=Max('count_real'),
        count_subscriber=Max('count_subscriber')
    )
    count_all = values['count_all']
    count_err = values['count_err']
    count_real = values['count_real']
    count_subscriber = values['count_subscriber']

    MailList.objects.filter(id=list_id).update(count_all=count_all, count_err=count_err, count_real=count_real, count_subscriber=count_subscriber)
    if merge_type == 2:
        MailList.objects.exclude(id=list_id).filter(id__in=list_ids).delete()
    # else:
    #     MailList.objects.exclude(id=list_id).filter(id__in=list_ids).update(count_all=0, count_err=0, count_real=0, count_subscriber=0, isvalid=False)

    redis = get_redis_connection()
    redis.rpush(EMD_WEB_MAIL_MERGE_QUEUE, j)
    return