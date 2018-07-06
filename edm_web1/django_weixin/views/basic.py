# -*- coding: utf-8 -*-

import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from django_weixin.api_errors import Http200
from django_weixin.models.basic import ( AccessToken, TextMessage)
from django_weixin.WXBizMsgCrypt import WXBizMsgCrypt
from django_weixin.utils.utils import get_xml_text_by_property
from app.core.models import Customer


# Create your views here.

@csrf_exempt
def index(request):
    if request.method == "GET":
        # atoken = AccessToken.objects.get(id=1)
        corpid = settings.APP_ID
        aeskey = settings.AES_KEY
        token = settings.WX_TOKEN
        wx = WXBizMsgCrypt(token, aeskey, corpid)
        timestamp = request.GET['timestamp']
        msg_signature = request.GET['signature']
        nonce = request.GET['nonce']
        echostr = request.GET['echostr']
        ret, return_token = wx.VerifyURL(msg_signature, timestamp, nonce, echostr)
        if request.GET.has_key('echostr'):
            return HttpResponse(return_token)
        else:
            return HttpResponse('validate page')

    elif request.method == "POST":
        to_user_name = get_xml_text_by_property(request.body, "ToUserName")
        from_user_name = get_xml_text_by_property(request.body, "FromUserName")
        message_type = get_xml_text_by_property(request.body, "MsgType")
        create_time = get_xml_text_by_property(request.body, "CreateTime")
        openid = request.GET.get('openid', '')
        if message_type == "event":  # 检测是不是event类型的消息
            event = get_xml_text_by_property(request.body, "Event")  # 获取event的类型
            if event.lower() in ['subscribe', 'scan']:
                event_key = get_xml_text_by_property(request.body, "EventKey")  # 获取event的类型
                bind_customer(event_key, openid)
                # 绑定用户
                #if event_key.startswith('bind_'):
                #    bind_customer(event_key.split('_')[-1], openid)
                message_content = u'已绑定'
            if event == "scancode_waitmsg":  # 扫码但是不跳转的事件
                message_content = get_xml_text_by_property(request.body, "ScanResult")
            if event == "LOCATION":
                message_content = ""

        xml_return_string = TextMessage.TextMessageTemplate.format(toUser=from_user_name, fromUser=to_user_name,
                                                                   create_time=create_time,
                                                                   message_content=message_content)
        # xml_return_string = KeFuMessage.KeFuMessageTemplate.format(toUser=from_user_name, fromUser=to_user_name,
        #                                                            create_time=create_time,
        #                                                            message_content=message_content)

        return HttpResponse(xml_return_string, content_type="text/xml")
    else:
        logging.info('...............other method.')
        return Http200(request)


def bind_customer(customer_id, openid):
    customer = Customer.objects.get(id=customer_id)
    customer.bind_openid(openid)


def get_access_token_view(request):
    new_token, _created = AccessToken.objects.get_or_create(pk=1)
    token = new_token.get_access_token()
    logging.info(token)
    context_data = {
        'access_token': token,
    }
    return render(request, 'get_access_token.html', context_data)


def admin_dashboard(request):
    access_token_url = settings.APP_URL + "/django-weixin/access/token/get/"
    qr_code_ticket = settings.APP_URL + "/django-weixin/show/ticket/"
    context_data = {
        "access_token_url": access_token_url,
        "qr_code_ticket": qr_code_ticket
    }
    return render(request, 'admin-dashboard.html', context_data)


def get_qr_code_ticket(request):
    from django_weixin.utils.utils import get_temp_qr_code, get_pergmanent_qr_code
    temp_url = get_temp_qr_code()
    pergmanent_url = get_pergmanent_qr_code()
    context_data = {
        'temp': temp_url,
        'permanent': pergmanent_url
    }
    return render(request, 'ticket.html', context_data)
