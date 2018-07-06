# coding=utf-8

import re
import os
import base64

import json
import uuid
import time
import random
import datetime
import hashlib
from binascii import a2b_hex

from Crypto.Cipher import DES
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.auth.views import deprecate_current_app
from django.template.response import TemplateResponse
from django.http import HttpResponse, Http404
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.contrib.auth.views import auth_login
from django.contrib.auth import authenticate
from django.template.defaultfilters import date as dateformat
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _lazy
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import update_last_login
from django_redis import get_redis_connection

from app.core.models import ( CoreSuggest, Customer, CorePasswordAlter, CustomerContentRel,
                              CustomerWayRel, Manager, Services, CustomerDomain, CustomerMailbox )
from app.suggest.models import Suggest, SuggestDetail
from lib.template import MulTemplateEmail, smtp_send_email
from lib.common import get_smtp_acct
from app.core.models import CoreUrlRemark, AliCustomer, Prefs, CoreVerifyAli, CoreBrowserConfig
from app.core.configs import (ESTIMATE_SELECT, CONTENT_SELECT, INDUSTRY_SELECT, WAY_SELECT, NOTIFICATION_TYPE)

from lib import sms_code, tools, common


def set_language_session(sender, user, **kwargs):
    """
    A signal receiver which updates the last_login date for
    the user logging in.
    """
    kwargs['request'].session['_language'] = user.lang_code
user_logged_in.connect(set_language_session)

@login_required
def set_lang(request):
    # from django.conf.urls import i18n
    # from django.utils.http import is_safe_url, urlunquote
    from django.utils.translation import check_for_language
    next = request.META.get('HTTP_REFERER', None)
    if not next or next.endswith("lang/set/"):
        next = '/'

    # next = request.POST.get('next', request.GET.get('next'))
    # print '---------1-------', next
    # if (next or not request.is_ajax()) and not is_safe_url(url=next, host=request.get_host()):
    #     print '---------2-------', next, request.is_ajax()
    #     next = request.META.get('HTTP_REFERER')
    #     print '---------3-------', next
    #     if next:
    #         next = urlunquote(next)  # HTTP_REFERER may be encoded.
    #         print '---------4-------', next
    #     if not is_safe_url(url=next, host=request.get_host()) or next.endswith("/lang/set/"):
    #         next = '/'
    #         print '---------5-------', next

    response = HttpResponseRedirect(next)
    lang_code = request.POST.get('language_code', None)
    if not lang_code:
        lang_code = request.LANGUAGE_CODE
    if not lang_code or lang_code not in ('en-us', 'zh-hans'):
        lang_code = settings.LANGUAGE_CODE
    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['_language'] = lang_code
        #max_age =  60*60*24*365
        #expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
        #response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code, max_age, expires)
        request.user.lang_code = lang_code
        request.user.save()
    return response

@never_cache
@deprecate_current_app
# @csrf_protect
def register(request, template_name='register.html'):
    try:
        cryp_obj = DES.new(settings.CRYP_KEY)
        ali_user_id, expired_time = cryp_obj.decrypt(a2b_hex(request.GET.get("key", ""))).split('----')
        if int(time.time()) - int(expired_time) > 600:
            raise Http404
        ali_customer = AliCustomer.objects.get(user_id=ali_user_id)
    except:
        raise Http404

    point, _created = Prefs.objects.get_or_create(name='register_point')
    register_point = int(point.value) if point.value else None
    if not register_point:
        register_point = 100

    if request.method == "POST":
        username = request.POST.get('username', '')
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        company = request.POST.get('company', '')
        linkman = request.POST.get('linkman', '')
        email = request.POST.get('email', '')
        im = request.POST.get('im', '')

        from passlib.hash import md5_crypt

        password = md5_crypt.hash(new_password)

        register_manager_lists = ['register_manager_1', 'register_manager_2', 'register_manager_3']
        manager, _created = Prefs.objects.get_or_create(name=random.choice(register_manager_lists))
        manager_id = int(manager.value) if manager.value else None
        if not manager_id:
            manager = Manager.objects.first()
            manager_id = manager.id

        obj = Customer.objects.create(
            username=username, password=password, company=company, linkman=linkman,
            mobile=username, email=email, im=im,
            ali_customer=ali_customer,
            is_new=False,
            manager_id=manager_id, is_register=True
        )

        Services.objects.create(customer=obj, qty_count=register_point, qty_valid=register_point, is_verify='0',
                                service_end='2099-12-31 23:59:59', server_type='6')

        # 随机分配一个smtp账号
        domain_lists = CustomerDomain.objects.filter(customer_id=0, is_register=True)
        if domain_lists:
            box_domain = random.choice(domain_lists).domain
            box_name, box_mailbox = tools.get_sys_smtp_mailbox(CustomerMailbox, box_domain)
            box_obj = CustomerMailbox(
                customer=obj,
                domain=box_domain,
                name=box_name,
                mailbox=box_mailbox,
                password=box_name,
                disabled='0',
                limit_qty=register_point,
            )
            box_obj.api_sync('add-mailbox')
            box_obj.save()

        # 删除短信验证记录
        try:
            CoreVerifyAli.objects.get(user_id=ali_customer.user_id).delete()
        except:
            pass

        msg = _lazy(u'注册成功')
        user = authenticate(username=obj.username, password='', t_password=obj.password)
        auth_login(request, user)
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect('/')

    return render(request, template_name, context={
        'ali_customer': ali_customer,
        'register_point': register_point,
    })


@deprecate_current_app
@never_cache
def ajax_checkusername_and_smscode(request):
    # 目前mysql验证， 最好redis缓存
    status = 'Y'
    username = request.POST.get('username', '')
    ali_customer_id = request.POST.get('ali_customer_id', '')
    _exsited = Customer.objects.filter(username=username).exists()
    # 验证用户名是否存在
    if _exsited:
        return HttpResponse(json.dumps({'status': "N"}), content_type="application/json")

    obj, _created = CoreVerifyAli.objects.get_or_create(user_id=ali_customer_id)

    updated = obj.updated
    user_count = obj.user_count
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    updated = dateformat(updated, "Y-m-d")
    # 当天获取验证码次数
    if now == updated:
        if user_count >= 6:
            return HttpResponse(json.dumps({'status': "C"}), content_type="application/json")
    else:
        user_count = 0
    # 发送短信
    code, msg = sms_code.sms(username)
    if code == -1:
        return HttpResponse(json.dumps({'status': 'E'}), content_type="application/json")
    else:
        user_count += 1
        obj.phone = username
        obj.code = msg
        obj.expire_time = int(time.time())
        obj.user_count = user_count
        obj.save()
    return HttpResponse(json.dumps({'status': status}), content_type="application/json")


@deprecate_current_app
@never_cache
def ajax_checkusername_and_checksmscode(request):
    status = 'Y'
    username = request.POST.get('username', '')
    ali_customer_id = request.POST.get('ali_customer_id', '')
    smscode = request.POST.get('smscode', '')
    _exsited = Customer.objects.filter(username=username).exists()
    # 验证用户名是否存在
    if _exsited:
        status = 'N'

    obj, _created = CoreVerifyAli.objects.get_or_create(user_id=ali_customer_id)

    # 验证手机是否一致
    if obj.phone != username:
        return HttpResponse(json.dumps({'status': "C"}), content_type="application/json")

    # 验证验证码是否一致
    if obj.code != smscode:
        return HttpResponse(json.dumps({'status': "E"}), content_type="application/json")

    # 验证验证码有效性
    if int(time.time()) - obj.expire_time > sms_code.EXPIRE_TIME:
        return HttpResponse(json.dumps({'status': "F"}), content_type="application/json")

    return HttpResponse(json.dumps({'status': status}), content_type="application/json")

@login_required
def home(request, template_name='home.html'):
    agent = request.META.get('HTTP_USER_AGENT', None)
    conflists = CoreBrowserConfig.objects.all().order_by('id')
    is_latest_browser = tools.get_browser_version(agent, conflists)
    if request.method == "POST":
        data = request.POST
        status = int(data.get('status', '0'))
        action = data.get('action', '')
        style_id = data.get('style_id', '')
        home_new = data.get('home_new', '')  # 客户完善资料
        if action == 'change_style':
            request.user.web_style = style_id
            request.user.save()
            return HttpResponse(json.dumps({}), content_type="application/json")
        if status == 2:
            suggest = data.get('suggest', '')
            if not suggest:
                msg = _lazy(u'没有评论，提交失败')
                messages.add_message(request, messages.ERROR, msg)
                return HttpResponseRedirect('/')
            obj = Suggest.objects.filter(path='/').first()
            SuggestDetail.objects.create(suggest=obj, customer=request.user, remark=suggest)
            # score = int(data.get('score', '1'))
            # obj = CoreSuggest(customer_id=request.user.id, score=score, suggest=suggest)
            # obj.save()
            msg = _lazy(u'评论成功提交')
        if home_new == 'cplt_mtl':  # 客户完善资料
            obj = Customer.objects.get(id=request.user.id)
            homepage = request.POST.get('homepage', '').strip()
            estimate = request.POST.get('estimate', '')
            industry = request.POST.get('industry', '')
            if obj.is_remaintain:
                linkman = request.POST.get('linkman', '')
                mobile = request.POST.get('mobile', '')
                phone = request.POST.get('phone', '')
                email = request.POST.get('email', '')
                im = request.POST.get('im', '')
                obj.linkman = linkman
                obj.mobile = mobile
                obj.phone = phone
                obj.email = email
                obj.im = im
                obj.is_remaintain = False
            obj.homepage = homepage
            obj.estimate = estimate
            obj.industry = industry
            obj.is_new = True
            obj.save()

            content_list = request.POST.getlist('content_type', '')
            way_list = request.POST.getlist('way_type', '')
            content_list = content_list if content_list else []
            way_list = way_list if way_list else []
            CustomerContentRel.objects.filter(customer=request.user).delete()
            CustomerWayRel.objects.filter(customer=request.user).delete()

            bulk_c = []
            for rel in content_list:
                bulk_c.append(CustomerContentRel(customer=request.user, content_type=rel))
            CustomerContentRel.objects.bulk_create(bulk_c)

            bulk_w = []
            for rel in way_list:
                bulk_w.append(CustomerWayRel(customer=request.user, way_type=rel))
            CustomerWayRel.objects.bulk_create(bulk_w)
            msg = _lazy(u'资料完善成功')

        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect('/')
    """
    if not request.user.weixin_customer:
        wechat_instance = WechatBasic(token=settings.MP_WX_TOKEN, appid=settings.MP_WX_APPID,
                                      appsecret=settings.MP_WX_APPSECRET)
        redis = get_redis_connection()
        key = 'wx_{}'.format(request.user.id)
        params = {"expire_seconds": 3600, "action_name": "QR_SCENE",
                  "action_info": {"scene": {'scene_id': request.user.id}}}
        ticket = wechat_instance.create_qrcode(params).get('ticket', '')
        image_data = urllib.urlopen("https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket={}".format(ticket)).read()
        redis.hset(key, 'ticket', ticket)
        redis.hset(key, 'image_data', image_data)
        redis.hset(key, 'is_dealed', 0)
        redis.expire(key, 3600)
    """
    is_admin = request.session.get('is_admin', False)
    if request.user.is_new or is_admin:
        response = render(request, template_name, context={
            'is_latest_browser': is_latest_browser,
        })
        return response
    else:
        content_lists = CustomerContentRel.objects.filter(customer=request.user).values_list('content_type', flat=True)
        way_lists = CustomerWayRel.objects.filter(customer=request.user).values_list('way_type', flat=True)
        response = render(request, 'home_new.html', context={
            'content_lists': content_lists,
            'way_lists': way_lists,
            'estimate_selects': ESTIMATE_SELECT,
            'content_selects': CONTENT_SELECT,
            'industry_selects': INDUSTRY_SELECT,
            'way_selects': WAY_SELECT,
            'estimate_value_list': [value[0] for value in ESTIMATE_SELECT],
            'industry_value_list': [value[0] for value in INDUSTRY_SELECT],
        })
        return response

# 备注
# :django:proj:page:url:flag:user_id:task_id:
SUSTOMER_MESSAGE_CACHE_KEY = ":django:edmweb:all:all:remark:1:1:"
def get_remark_content(base_url):
    content = ""
    if base_url:
        if re.search(r'(\/\d+?\/)', base_url):
            base_url = re.sub(r'(\/\d+?\/)', '/modify/', base_url)
        redis = get_redis_connection()
        content = redis.hget(SUSTOMER_MESSAGE_CACHE_KEY, base_url)
        if not content:
            first = CoreUrlRemark.objects.filter(url=base_url).first()
            content = first and first.remark or  ""
            redis.hset(SUSTOMER_MESSAGE_CACHE_KEY, base_url, content)
    return {'remark': content }

@login_required
def ajax_get_remark_base(request):
    base_url = request.GET.get('base_url', '').strip('')
    res = get_remark_content(base_url)
    return HttpResponse( json.dumps(res, ensure_ascii=False ), content_type="application/json")

@login_required
def ajax_save_remark_base(request):
    base_url = request.POST.get('base_url', '').strip('')
    remark = request.POST.get('remark', '').strip('')
    if base_url:
        if re.search(r'(\/\d+?\/)', base_url):
            base_url = re.sub(r'(\/\d+?\/)', '/modify/', base_url)
        obj, bool = CoreUrlRemark.objects.get_or_create(url=base_url)
        obj.remark = remark
        obj.save()
        redis = get_redis_connection()
        redis.hset(SUSTOMER_MESSAGE_CACHE_KEY, base_url, remark)
    return HttpResponse(json.dumps({'msg': _lazy(u"成功修改备注")%{}}), content_type="application/json")

@deprecate_current_app
@never_cache
def password_reset(request, template_name='password_reset_form.html'):
    if request.method == 'POST':
        loginName = request.POST.get('loginName', '')
        obj = Customer.objects.filter(username=loginName)[0]
        email = obj.email
        _email = email.split('@')
        encrypt_email = _email[0][0] + u'***@' + _email[-1]

        customer_id = obj.id
        uuids = uuid.uuid1()
        token = make_password(loginName, None, 'unsalted_md5')
        p_obj, _created = CorePasswordAlter.objects.get_or_create(customer_id=customer_id)
        p_obj.uuid = uuids
        p_obj.token = token
        p_obj.isvalid = True
        p_obj.expire_time = time.time() + 86400
        p_obj.save()

        host, port, account, password = get_smtp_acct(email)

        passwd_link = settings.EDM_WEB_URL + u'/passwd/set?uuid={}&token={}'.format(uuids, token)
        replace_list = [
            ('{USERNAME}', loginName),
            ('{RESET_TIME}', datetime.datetime.now().strftime(u'%Y-%m-%d %H:%M:%S')),
            ('{PASSWD_LINK}', passwd_link),
            ('{MAIL_ADDRESS}', account),
        ]
        content = u'''<table id="bodyTable" class="ke-zeroborder" width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" align="center"><tbody><tr><td id="bodyCell" valign="top" align="center"><table id="templateContainer" class="ke-zeroborder" width="600" cellspacing="0" cellpadding="0" border="0"><tbody><tr><td valign="top" align="center"><table id="templateHeader" class="ke-zeroborder" width="100%" cellspacing="0" cellpadding="0" border="0"><tbody><tr><td valign="top" align="center"><table class="templateContainer ke-zeroborder" width="600" cellspacing="0" cellpadding="0" border="0"><tbody><tr><td class="headerContainer tpl-container dragTarget" data-container="header" valign="top"><div class="block tpl-block text-block"><div data-attach-point="containerNode"><table class="textBlock ke-zeroborder" width="100%" cellspacing="0" cellpadding="0" border="0"><tbody class="textBlockOuter"><tr><td class="textBlockInner" valign="top"><table class="textContentContainer ke-zeroborder" width="600" cellspacing="0" cellpadding="0" border="0" align="left"><tbody><tr><td class="textContent" style="padding-top:9px;padding-right:18px;padding-bottom:9px;padding-left:18px;background-color:#ffffff;" valign="top"><div style="box-sizing:border-box;margin:0px 0px 10px;font-family:'Microsoft YaHei', Helvetica, Arial, sans-serif;font-size:14px;line-height:20px;"><p>尊敬的用户：{USERNAME}</p><p>您好！</p><p style="height:20px;">&nbsp;</p><p>您在<span style="border-bottom:1px dashed #CCCCCC;position:relative;" t="5" times=" 08:11" isout="0">{RESET_TIME}</span>申请重置密码，</p><p>请点击下面的链接修改用户 {USERNAME} 的密码：<br /> <a href="{PASSWD_LINK}" target="_blank">{PASSWD_LINK}</a></p><p>为了保证您帐号的安全性，该链接有效期为24小时，并且点击一次后将失效!</p></div></td></tr></tbody></table></td></tr></tbody></table></div></div><div class="tpl-block tpl-text" style="margin-top:0px;margin-bottom:0px;border:0px solid #000000;border-radius:0px;"><div data-attach-point="containerNode"><table class="textBlock ke-zeroborder" width="100%" cellspacing="0" cellpadding="0" border="0"><tbody class="textBlockOuter"><tr><td class="textBlockInner" valign="top"><table class="textContentContainer ke-zeroborder" width="100%" cellspacing="0" cellpadding="0" border="0" align="left"><tbody><tr><td class="textContent" style="padding:10px 0px;text-align:left;background:#FFFFFF;" valign="top" align="center"><div style="text-align:center;"><strong><span style="color:#317bcf;"><span style="font-family:microsoft yahei;">U-Mail运营团队</span></span></strong></div></td></tr></tbody></table></td></tr></tbody></table></div></div></td></tr></tbody></table></td></tr></tbody></table></td></tr><tr><td valign="top" align="center"><table id="templateBody" class="ke-zeroborder" width="100%" cellspacing="0" cellpadding="0" border="0"><tbody><tr><td valign="top" align="center"><table class="templateContainer ke-zeroborder" width="600" cellspacing="0" cellpadding="0" border="0"><tbody><tr><td class="bodyContainer tpl-container dragTarget" data-container="body" valign="top"><div class="ghost-source">&nbsp;</div><div class="tpl-block tpl-divider" style="margin-top:0px;margin-bottom:0px;border:0px solid #000000;border-radius:0px;"><div data-attach-point="containerNode"><table class="dividerBlock ke-zeroborder" width="100%" cellspacing="0" cellpadding="0" border="0"><tbody class="dividerBlockOuter"><tr><td class="dividerBlockInner"><table class="dividerContentContainer ke-zeroborder" width="100%" cellspacing="0" cellpadding="0" border="0"><tbody><tr><td class="dividerContent" style="margin-top:10px;margin-bottom:15px;padding:10px 20px;text-align:start;background-color:#FFFFFF;" align="center"><div style="width:100%;height:1px;background:#999999;">&nbsp;</div></td></tr></tbody></table></td></tr></tbody></table></div></div></td></tr></tbody></table></td></tr></tbody></table></td></tr><tr><td valign="top" align="center"><table id="templateFooter" class="ke-zeroborder" width="100%" cellspacing="0" cellpadding="0" border="0"><tbody><tr><td valign="top" align="center"><table class="templateContainer ke-zeroborder" width="600" cellspacing="0" cellpadding="0" border="0"><tbody><tr><td class="footerContainer tpl-container dragTarget" data-container="footer" valign="top"><div class="block tpl-block text-block"><div data-attach-point="containerNode"><table class="textBlock ke-zeroborder" width="100%" cellspacing="0" cellpadding="0" border="0"><tbody class="textBlockOuter"><tr><td class="textBlockInner" valign="top"><table class="textContentContainer ke-zeroborder" width="600" cellspacing="0" cellpadding="0" border="0" align="left"><tbody><tr><td class="textContent" style="padding-top:9px;padding-right:18px;padding-bottom:9px;padding-left:18px;background-color:#ffffff;" valign="top"><div style="line-height:20.7999992370605px;text-align:center;"><span style="font-family:'microsoft yahei';">系统发信，请勿回复</span><br /> </div><div style="line-height:20.7999992370605px;text-align:center;"><span style="font-family:'microsoft yahei';"><span class="bigger-120"><span class="blue bolder">Copyright &copy; U-Mail</span></span>, All rights reserved.<br /> <strong style="line-height:20.7999992370605px;">Our mailing address is:</strong><br style="line-height:20.7999992370605px;" /> <span style="line-height:20.7999992370605px;"><a href="mailto:{MAIL_ADDRESS}" target="_blank">{MAIL_ADDRESS}</a></span></span></div></td></tr></tbody></table></td></tr></tbody></table></div></div></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table>'''
        for k, v in replace_list:
            content = content.replace(k, v)
        m = MulTemplateEmail(
            content_type=1, character='utf-8', encoding='base64',
            mail_from=account, mail_to=email, reply_to=account,
            subject=u'U-Mail重置密码', content=content, attachment=[]
        )
        message = m.get_message()
        code, msg = smtp_send_email(
            host=host,
            port=port,
            account=account,
            password=password,
            sender=account,
            receivers=[email],
            message=message
        )
        # code, msg_str, deliver_ip, receive_ip = send_template(
        # host='127.0.0.1', port=10027, use_ssl=None,
        # sender=sender, receiver=email, message=message
        # )
        return HttpResponseRedirect('/passwd/done?email={}'.format(encrypt_email))
    return TemplateResponse(request, template_name, {})


@deprecate_current_app
@never_cache
def ajax_check_username(request):
    code = 'error'
    loginName = request.POST.get('loginName', '')
    if loginName and Customer.objects.filter(username=loginName).exists():
        code = 'ok'
    return HttpResponse(json.dumps({'code': code}), content_type="application/json")


@deprecate_current_app
@never_cache
def password_reset_done(request, template_name='password_reset_done.html'):
    email = request.GET.get('email', '')
    return TemplateResponse(request, template_name, {'email': email})


@deprecate_current_app
@never_cache
def password_set(request, template_name='password_set_form.html'):
    if request.method == "POST":
        data = request.POST
        customer_id = data.get('customer_id', '')
        new_password2 = data.get('new_password2', '')
        from passlib.hash import md5_crypt

        password = md5_crypt.hash(new_password2)
        obj = Customer.objects.get(id=customer_id)
        obj.password = password
        obj.save()

        CorePasswordAlter.objects.filter(customer_id=customer_id).update(isvalid=False)

        messages.add_message(request, messages.SUCCESS, _lazy(u'密码修改成功'))
        return HttpResponseRedirect('/login')

    uuids = request.GET.get('uuid', '')
    token = request.GET.get('token', '')
    try:
        p_obj = CorePasswordAlter.objects.get(uuid=uuids, token=token)
        customer_id = p_obj.customer_id
        expire_time = p_obj.expire_time
        isvalid = p_obj.isvalid
        if (time.time() > expire_time) or (not isvalid):
            return TemplateResponse(request, 'http404.html', {})
        else:
            return TemplateResponse(request, template_name, {
                'uuid': uuids,
                'token': token,
                'customer_id': customer_id,
            })
    except:
        return TemplateResponse(request, 'http404.html', {})


def js_oauth_verify(request):
    return HttpResponse('qtROZ0sDp2gDeaQI')


def php_login(request):
    from django.contrib.auth.views import logout

    auth = request.POST.get('auth', '')
    customer_id = request.POST.get('customer_id', '')
    admin_id = request.POST.get('admin_id', '')
    if auth == hashlib.md5('%s-%s' % (
            settings.WEB_API_AUTH_KEY,
            datetime.datetime.now().strftime("%Y%m%d"))).hexdigest() and admin_id and customer_id:
        logout(request)
        obj = Customer.objects.get(id=customer_id)
        user = authenticate(username=obj.username, password='', t_password=obj.password)
        request.session['is_admin'] = True
        request.session['admin_id'] = admin_id
        user_logged_in.disconnect(update_last_login)
        auth_login(request, user)
        return HttpResponseRedirect(reverse('home'))
    raise Http404


def ajax_get_captcha(request):
    uuids = str(uuid.uuid1())
    redis = get_redis_connection()
    key = 'captcha:{}'.format(uuids)
    captch_path = os.path.join(settings.BASE_DIR, 'edm_web', 'captcha_img')
    file_id = random.choice(os.listdir(captch_path)).split('.')[0]
    p = redis.pipeline()
    p.hset(key, 'file_id', file_id)
    p.expire(key, 120)
    p.execute()
    return HttpResponse(json.dumps({'key': uuids}), content_type="application/json")


def captch_img(request, file_id):
    try:
        uuids, file_type = file_id.split('.')
        key = 'captcha:{}'.format(uuids)
        redis = get_redis_connection()
        captch_file = os.path.join(settings.BASE_DIR, 'edm_web', 'captcha_img', '{}.{}'.format(redis.hget(key, 'file_id'), file_type))
        return HttpResponse(file(captch_file, 'rb').read(), content_type='image/{}'.format(file_type))
    except:
        raise Http404


def ajax_check_captcha(request):
    redis = get_redis_connection()
    id = request.GET.get('id', '')
    value = request.GET.get('value', '')
    key = 'captcha:{}'.format(id)
    try:
        res = abs(float(redis.hget(key, 'file_id')) - float(value)) <= 5
    except:
        res = False
    if res:
        p = redis.pipeline()
        p.hset(key, 'res', res)
        p.expire(key, 120)
        p.execute()
    else:
        p = redis.pipeline()
        p.hincrby(key, 'error')
        p.expire(key, 120)
        p.execute()
        if int(redis.hget(key, 'error')) > 2:
            redis.delete(key)
    return HttpResponse(json.dumps({'res': res}), content_type="application/json")
