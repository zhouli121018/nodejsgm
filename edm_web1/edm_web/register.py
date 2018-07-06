# coding=utf-8


import json
import time
import random
from binascii import b2a_hex, a2b_hex

from Crypto.Cipher import DES
from django.shortcuts import render, HttpResponseRedirect
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.auth.views import deprecate_current_app
from django.http import HttpResponse, Http404
from django.conf import settings
from django.contrib.auth.views import auth_login
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _lazy
from django.core.cache import cache
from django.core.urlresolvers import reverse

from app.core.models import (Customer, Manager, Services, CustomerDomain, CustomerMailbox, ApplyCustomer)
from lib.common import get_client_ip
from lib.tools import gen_len_chars, get_sys_smtp_mailbox
from app.core.models import Prefs
from lib import tools, sms_code

from django_redis import get_redis_connection

@never_cache
@deprecate_current_app
# @csrf_protect
def register_new(request, template_name='register_new.html'):
    if request.method == "POST":
        username = request.POST.get('username', '')
        new_password = request.POST.get('new_password', '')
        company = request.POST.get('company', '')
        linkman = request.POST.get('linkman', '')
        email = request.POST.get('email', '')
        protocal = request.POST.get('protocal', '')
        if not checksmscode(request) or not protocal or Customer.objects.filter(username=username):
            return HttpResponse(u'注册失败')

        from passlib.hash import md5_crypt

        password = md5_crypt.hash(new_password)

        obj = Customer.objects.create(
            username=username, password=password, linkman=linkman, company=company,
            mobile=username, email=email, manager_id=1,
            is_register=True, disabled="1"
        )

        try:
            register_point = int(Prefs.objects.get(name='register_point').value)
        except:
            register_point = 100

        # 随机分配一个smtp账号
        domain_lists = CustomerDomain.objects.filter(customer_id=0, is_register=True)
        if domain_lists:
            box_domain = random.choice(domain_lists).domain
            box_name, box_mailbox = get_sys_smtp_mailbox(CustomerMailbox, box_domain)
            box_obj = CustomerMailbox(
                customer=obj,
                domain=box_domain,
                name=box_name,
                mailbox=box_mailbox,
                password=box_name,
                disabled='0',
                limit_qty=register_point,
            )
            # box_obj.api_sync('add-mailbox')
            box_obj.save()

        Services.objects.create(customer=obj, service_end='2099-12-31 23:59:59', server_type='6', is_verify="1")

        # Services.objects.create(customer=obj, qty_count=register_point, qty_valid=register_point, is_verify='0',
        # service_end='2099-12-31 23:59:59', server_type='6')

        cryp_obj = DES.new(settings.CRYP_KEY)
        key = b2a_hex(cryp_obj.encrypt(gen_len_chars("{}----{}".format(obj.id, int(time.time())))))
        cache_key = 'register_key:{}'.format(key)
        cache.set(cache_key, obj.id, 60 * 60)

        # 支付宝注册完善资料， 如果5分钟还未注册就立即 发送 未通过验证的自注册提醒
        redis = get_redis_connection()
        redis.hset("pushcrew:zhifubao:register", obj.id, int(time.time()))

        return HttpResponseRedirect('http://{}{}?key={}'.format(settings.HOSTNAME, reverse('register_new_step2'), key))

    try:
        register_protocol = Prefs.objects.get(name='register_protocol').value
    except:
        register_protocol = ''
    return render(request, template_name, context={
        'register_protocol': register_protocol
    })


@never_cache
@deprecate_current_app
def register_new_step2(request, template_name='register_new_step2.html'):
    key = request.GET.get('key', '')
    try:
        cryp_obj = DES.new(settings.CRYP_KEY)
        ali_user_id, expired_time = cryp_obj.decrypt(a2b_hex(key)).split('----')
        if int(time.time()) - int(expired_time) > 3600:
            raise Http404
    except:
        raise Http404

    point, _created = Prefs.objects.get_or_create(name='register_point')
    register_point = int(point.value) if point.value else None
    if not register_point:
        register_point = 100

    point, _created = Prefs.objects.get_or_create(name='register_credit')
    register_credit = int(point.value) if point.value else None
    if not register_credit:
        register_credit = 700

    return render(request, template_name, context={
        'register_point': register_point,
        'register_credit': register_credit,
        'key': key
    })


@never_cache
@deprecate_current_app
def register_new_step3(request, template_name='register_new_step3.html'):
    key = request.GET.get('key', '')
    result = request.GET.get('result', '')
    try:
        cryp_obj = DES.new(settings.CRYP_KEY)
        ali_user_id, expired_time = cryp_obj.decrypt(a2b_hex(key)).split('----')
        if int(time.time()) - int(expired_time) > 3600:
            raise Http404
    except:
        raise Http404

    return render(request, template_name, context={
        'key': key,
        'result': result,
    })

@deprecate_current_app
@never_cache
def ajax_smscode(request):
    status = 'Y'
    username = request.POST.get('username', '')
    not_check_username = request.POST.get('not_check_username', '')
    if not not_check_username:
        _exsited = Customer.objects.filter(username=username).exists()
        # 验证用户名是否存在
        if _exsited:
            return HttpResponse(json.dumps({'status': "N"}), content_type="application/json")
    client_ip = get_client_ip(request)
    cache_key = 'register_smscode:{}'.format(client_ip)
    codes = cache.get(cache_key)

    if codes is None:
        cache.set(cache_key, {}, 24 * 60 * 60)
        codes = {}

    # 当天获取验证码次数
    if sum([len(v) for k, v in codes.iteritems()]) >= 3:
        return HttpResponse(json.dumps({'status': "C"}), content_type="application/json")
    # 发送短信
    code, msg = sms_code.sms(username)
    # code, msg = 1, '1234'

    if code == -1:
        return HttpResponse(json.dumps({'status': 'E'}), content_type="application/json")
    else:
        codes.setdefault(username, []).append((int(time.time()), msg, 1))
        cache.set(cache_key, codes)
    return HttpResponse(json.dumps({'status': status}), content_type="application/json")

def checksmscode(request, is_ajax=True):
    smscode = request.POST.get('smscode', '')
    username = request.POST.get('username', '')
    client_ip = get_client_ip(request)
    cache_key = 'register_smscode:{}'.format(client_ip)
    try:
        dict_codes = cache.get(cache_key)
        codes = dict_codes.get(username, [])

        send_time, code, status = codes[-1]
        if int(time.time()) - int(send_time) > 120 or int(status) != 1:
            code = ''
    except:
        code = ''
    if smscode == code:
        if not is_ajax:
            send_time, code, status = codes.pop()
            codes.append([send_time, code, 0])
            dict_codes[username] = codes
            cache.set(cache_key, dict_codes)
        return True
    return False

@deprecate_current_app
@never_cache
def ajax_checksmscode(request):
    status = 'Y'
    # 验证验证码是否一致
    if not checksmscode(request):
        return HttpResponse(json.dumps({'status': "E"}), content_type="application/json")

    # 验证验证码有效性
    # if int(time.time()) - obj.expire_time > sms_code.EXPIRE_TIME:
    # return HttpResponse(json.dumps({'status': "F"}), content_type="application/json")

    return HttpResponse(json.dumps({'status': status}), content_type="application/json")

@never_cache
@deprecate_current_app
def register_login(request):
    key = request.GET.get('key', '')
    cache_key = 'register_key:{}'.format(key)
    if not cache.get(cache_key):
        raise Http404
    try:
        cryp_obj = DES.new(settings.CRYP_KEY)
        user_id, expired_time = cryp_obj.decrypt(a2b_hex(key)).split('----')
        if int(time.time()) - int(expired_time) > 3600:
            raise Http404
    except:
        raise Http404
    obj = Customer.objects.get(id=user_id)
    user = authenticate(username=obj.username, password='', t_password=obj.password)
    auth_login(request, user)
    return HttpResponseRedirect('/')


@never_cache
@deprecate_current_app
# @csrf_protect
def apply(request, template_name='apply.html'):
    if request.method == "POST":
        if not checksmscode(request, is_ajax=False):
            return HttpResponse(u'注册失败')
        username = request.POST.get('username', '')
        company = request.POST.get('company', '')
        linkman = request.POST.get('linkman', '')
        email = request.POST.get('email', '')
        qq = request.POST.get('qq', '')
        client_ip = get_client_ip(request)
        ApplyCustomer.objects.create(username=username, company=company, linkman=linkman, email=email, ip=client_ip, qq=qq)
        redis = get_redis_connection()
        redis.lpush('edm_web_apply_notice_queue', json.dumps({
            'username': username,
            'company': company,
            'linkman': linkman,
            'email': email,
            'ip': client_ip,
            'qq': qq,
            'time': time.strftime('%Y-%m-%d %H:%M:%S')
        }))
        return HttpResponseRedirect(reverse('apply_step2'))

    return render(request, template_name, context={
    })

def apply_step2(request, template_name='apply_step2.html'):
    return render(request, template_name, context={
    })
