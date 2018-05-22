# -*- coding: utf-8 -*-

import json
import time
import datetime
import hashlib
from django.http import HttpResponse, HttpResponseNotFound
from .models import get_mail_model

#认证的KEY
ASSET_AUTH_KEY = 'abcc7aee-7824-11e7-b733-b8aeedeaf1f5'
# 认证头
ASSET_AUTH_HEADER_NAME = 'HTTP_AUTH_KEY'
# 超时时间
ASSET_AUTH_TIME = 600
#存放认证过的key
ENCRYPT_LIST  = []

def api_auth(auth_key):
    if not auth_key:
        return -1

    sp = auth_key.split('|')
    if len(sp) != 2:
        return -1

    encrypt, timestamp = sp
    timestamp = float(timestamp)    # str换成float
    limit_timestamp = time.time() - ASSET_AUTH_TIME
    if limit_timestamp > timestamp:     # 当前程序时间与客户端时间戳对比 超时
        return -1
    ha = hashlib.md5(ASSET_AUTH_KEY.encode('utf-8'))
    ha.update(bytes("%s|%f" % (ASSET_AUTH_KEY, timestamp)))
    result = ha.hexdigest()
    if encrypt != result:           # md5值校验
        return -1
    return 1

def get_search_list(data):
    mail_to = data.get('mail_to', '').strip()
    search_date = data.get('search_date', '').strip()
    mail_from = data.get('mail_from', '').strip()
    search_hour = data.get('search_hour', '').strip()
    state = data.get('state', '').strip()
    error_type = data.get('error_type', '').strip()
    subject = data.get('subject', '').strip()
    client_ip = data.get('client_ip', '').strip()
    mail_to_list = data.get('mail_to_list', '').strip()
    try:
        search_date = datetime.datetime.strptime(search_date, '%Y-%m-%d').strftime('%Y%m%d')
    except:
        search_date = datetime.datetime.today().strftime('%Y%m%d')

    try:
        mail_model = get_mail_model(search_date)
        lists = mail_model.objects.all()
        if state:
            lists = lists.filter(state__in=state.split(','))
        if mail_to_list:
            mail_to_list = mail_to_list.split(',')
            lists = lists.filter(mail_to__in=mail_to_list)
        if mail_to:
            lists = lists.filter(mail_to__icontains=mail_to)
        if mail_from:
            lists = lists.filter(mail_from__icontains=mail_from)
        if error_type:
            lists = lists.filter(error_type=error_type)
        if subject:
            lists = lists.filter(subject__icontains=subject)
        if client_ip:
            lists = lists.filter(client_ip=client_ip)
        if search_hour:
            try:
                search_hour = int(search_hour)
            except:
                search_hour = 0
            _created = '%s %02d:00:00' % (
                datetime.datetime.strptime(search_date, '%Y%m%d').strftime('%Y-%m-%d'),
                int(search_hour)
            )
            lists = lists.filter(created__gte=_created)
        lists = lists.order_by('-id').values_list(
            'id', 'mail_from', 'mail_to', 'subject', 'return_code', 'return_message',
            'state', 'deliver_ip', 'error_type', 'created', 'deliver_time'
        )
        fields = ['id', 'mail_from', 'mail_to', 'subject', 'return_code', 'return_message', 'state', 'deliver_ip', 'error_type', 'created', 'deliver_time']
        return_list = []
        for res in lists:
            res_l = list(res)
            created = res_l[9].strftime('%Y-%m-%d %H:%M:%S') if res_l[9] else time.strftime('%Y-%m-%d %H:%M:%S')
            deliver_time = res_l[10].strftime('%Y-%m-%d %H:%M:%S') if res_l[10] else ""
            return_list.append(
                dict(zip(fields, res_l[0:9] + [created, deliver_time]))
            )
        return return_list
    except BaseException as e:
        return []

def mail_search_status(request):
    """
    :param request:
    :return:
    中继平台的数据查询接口，不仅是群发平台要用，
    客户的邮件系统通过中继平台发送的邮件也要查询，邮件系统晚些会增加邮件发送状态查询
    """

    # 验证
    # 密钥串+时间戳发送进行认证，超过超时时间认证失败，认证过的密钥过时清空
    auth_key = request.META.get(ASSET_AUTH_HEADER_NAME)

    if api_auth(auth_key) == -1:
        return HttpResponseNotFound(u'验证失败！')
    data = request.GET
    return_list = get_search_list(data)

    return HttpResponse(
        json.dumps({
            'return_code': 'success',
            'return_list': return_list,
        }, ensure_ascii=False ),
        content_type="application/json"
    )
