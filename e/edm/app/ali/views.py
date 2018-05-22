# coding=utf-8
import datetime

import urllib
import json
import time
import random
from binascii import b2a_hex, a2b_hex
from Crypto.Cipher import DES

from django.http.response import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import auth_login
from django.contrib.auth import authenticate
from app.core.models import CustomerOrder, CoreLog, AliCustomer, Prefs, Customer, CustomerDomain, CustomerMailbox, \
    Manager, Services
from alipay import create_direct_pay_by_user, notify_verify
from app.wechat.models import WeixinLog
from alipay_sdk import AliPay
from lib.tools import gen_len_chars, get_random_string, get_sys_smtp_mailbox
from django_redis import get_redis_connection
from lib.pushcrew import pushcrew_notice
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

ALI = AliPay(appid=settings.ALI_APPID, web_private_key_path=settings.ALI_PRIVATE_KEY_PATH,
             web_alipay_public_key_path=settings.ALI_PUBLIC_KEY_PATH, return_url=settings.ALI_RETURN_URL)
# 确认支付
@login_required
def pre_pay(request):
    id = request.GET.get('id', '')
    try:
        order = CustomerOrder.objects.get(orderno=id, customer=request.user)
    except ObjectDoesNotExist:
        raise Http404
    orderno = order.orderno
    subject = order.product_desc
    body = order.product_detail
    bank = ''
    tf = order.fee
    url = create_direct_pay_by_user(orderno, subject, body, bank, tf)
    # 去支付页面
    return HttpResponseRedirect(url)


# alipay异步通知
@csrf_exempt
def alipay_notify_url(request):
    data = request.POST
    if request.method == 'POST':
        # 商户网站订单号
        out_trade_no = data.get('out_trade_no', '')
        # 支付宝单号
        trade_no = data.get('trade_no', '')
        #返回支付状态
        trade_status = data.get('trade_status', '')
        #付款人
        buyer_id = data.get('buyer_id', '')
        #付款人
        buyer_email = data.get('buyer_email', '')
        # 时间
        notify_time = data.get('notify_time')
        is_sign = notify_verify(data)
        WeixinLog.objects.create(type='ali_notify', body=str(data), is_sign=is_sign)
        if is_sign:
            order = CustomerOrder.objects.get(orderno=out_trade_no)
            order.transaction_id = trade_no
            order.dt_pay = datetime.datetime.strptime(notify_time, '%Y-%m-%d %H:%M:%S')
            order.openid = buyer_id
            order.buyer = buyer_email
            if trade_status == 'TRADE_SUCCESS':
                order.status = 'paied'
                # 充值
                fee = order.fee
                qty_buy = order.qty_buy
                user = order.customer
                service = user.service()
                service.qty_count += qty_buy
                service.qty_valid += qty_buy
                service.qty_buytotal += qty_buy
                # 服务状态改变
                if service.disabled == "1":
                    service.disabled = '0'
                service.save()

                # 通知
                redis = get_redis_connection()
                redis.rpush('edm_web_notice_queue', json.dumps(
                    {
                        "type": "2",
                        'customer_id': '{}'.format(order.customer_id),
                        "area": '',
                        'point': '{}'.format(int(qty_buy)),
                        'domain': '',
                        'task': '',
                    }
                ))

                # 自主注册用户（支付宝） 转 支付宝正式用户
                if service.server_type == '6':
                    service.server_type = '0'
                    service.is_verify = '1'
                    service.save()

                # 日志
                CoreLog.objects.create(user=user, user_type='users', target=user, target_name=user,
                                       action='c_update_count', desc=u'{}元/{}点(支付宝充值)'.format(fee, qty_buy))
            order.save()
            return HttpResponse("success")
    return HttpResponse("fail")


# 同步通知
def alipay_return_url(request):
    data = request.GET
    is_sign = notify_verify(data)
    WeixinLog.objects.create(type='ali_return', body=str(data), is_sign=is_sign)
    if notify_verify(request.GET):
        orderno = request.GET.get('out_trade_no')
        return HttpResponseRedirect('{}?id={}'.format(reverse('pay_success'), orderno))
    return HttpResponseRedirect("/")


def ali_login(request):
    key = request.GET.get('key', 'login')
    return HttpResponseRedirect(ALI.user_info_auth(state=key))


def ali_login_return(request):
    is_allow_register = False
    customer = None
    try:
        auth_code = request.GET.get('auth_code', '')
        state = request.GET.get('state', '')
        token_url = ALI.system_oauth_token(auth_code)
        res = json.loads(urllib.urlopen(token_url).read())
        data = res.get('alipay_system_oauth_token_response', {})
        access_token = data['access_token']
        user_info_url = ALI.user_info_share(access_token)
        user_info = json.loads(urllib.urlopen(user_info_url).read()).get('alipay_user_info_share_response', {})
        user_id = user_info['user_id']
        ali_customer, _created = AliCustomer.objects.get_or_create(user_id=user_id)
        # 支付宝登录
        if state == 'login':
            users = Customer.objects.filter(ali_customer=ali_customer, disabled=0)
            if users:
                user = users[0]
                user = authenticate(username=user.username, password='', t_password=user.password)
                auth_login(request, user)
                # 登录日志
                user.save_fast_login_log(request, mode='ali')
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])

                # 支付宝登录通知销售
                sss = user.service()
                if sss and sss.is_pushcrew:
                    action = "service"
                    title = u"支付宝登录提醒"
                    message = u"{}（ID: {}） 于 {} 时间登录平台".format(
                        user.company, user.id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    pushcrew_notice(action, title, message)

                return HttpResponseRedirect('http://{}{}'.format(settings.HOSTNAME, reverse('home')))
            else:
                messages.add_message(request, messages.ERROR, _(u'此支付宝并未于平台账号绑定，请先绑定账号!'))
                return HttpResponseRedirect('http://{}{}'.format(settings.HOSTNAME, reverse('home')))

        elif state == 'bind':
            customer = request.user
        else:
            #芝麻信用验证
            cryp_obj = DES.new(settings.CRYP_KEY)
            customer_id, expired_time = cryp_obj.decrypt(a2b_hex(state)).split('----')
            customer = Customer.objects.get(id=customer_id)

        for field in ['avatar', 'city', 'gender', 'is_certified', 'is_student_certified', 'province', 'user_status',
                      'user_type']:
            setattr(ali_customer, field, user_info.get(field, ''))
        transaction_id = time.strftime('%Y%m%d%H%M%S') + get_random_string(4).upper()
        try:
            min_score = int(Prefs.objects.get(name='register_credit').value)
        except:
            min_score = 630
        zhima_url = ALI.zhima_credit_score(access_token, transaction_id, user_id, min_score)
        zhima_info = json.loads(urllib.urlopen(zhima_url).read()).get('zhima_credit_score_brief_get_response', {})
        is_admittance = zhima_info.get('is_admittance', '')
        ali_customer.is_admittance = is_admittance
        ali_customer.save()
        if ali_customer.user_type == '1' and ali_customer.user_status == 'T':
            is_allow_register = True
        elif is_admittance == "N":
            msg = _(u'抱歉，您的芝麻信用未符合快捷注册条件,如需测试, 请联系客服,电话/企业QQ：400-8181-568！')
        elif is_admittance == "Y":
            is_allow_register = True
        else:
            msg = _(u'抱歉，系统获取您的芝麻信用失败，无法进行快捷注册登陆！')
    except:
        msg = _(u'支付宝接口异常，请稍后重试！')

    if customer and is_allow_register and not customer.is_bind_ali:
        try:
            register_point = int(Prefs.objects.get(name='register_point').value)
        except:
            register_point = 100

        if customer.is_register:
            register_manager_lists = ['register_manager_1', 'register_manager_2', 'register_manager_3']
            redis = get_redis_connection()
            find_next_manager = 'register_manager_1'
            find_next_count = None
            for key in register_manager_lists:
                count = redis.hget("edm_web_register_manager_hash", key=key)
                count = int(count) if count else 0
                if find_next_count is None or find_next_count >= count:
                    find_next_manager = key
                    find_next_count = count
            redis.hincrby("edm_web_register_manager_hash", find_next_manager, 1)

            # manager, _created = Prefs.objects.get_or_create(name=random.choice(register_manager_lists))
            manager, _created = Prefs.objects.get_or_create(name=find_next_manager)
            manager_id = int(manager.value) if manager.value else None
            if not manager_id:
                manager = Manager.objects.first()
                manager_id = manager.id
            customer.disabled = "0"
            customer.manager_id = manager_id
        service = customer.service()

        service.qty_valid += register_point
        service.qty_count += register_point
        customer.is_bind_ali = True
        service.save()

        # 支付宝注册通知销售
        action = "sale"
        title = u"注册提醒（验证通过）"
        message = u"{}（ID: {}） 于 {} 时间注册并登录平台".format(
            customer.company, customer.id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        pushcrew_notice(action, title, message, customer_id=customer.id)

        msg = _(u'恭喜您，芝麻信用验证通过，注册成功！')
    customer.ali_customer = ali_customer
    customer.save()
    if state == 'bind':
        messages.add_message(request, messages.SUCCESS, _(u'支付宝绑定成功'))
        return HttpResponseRedirect(reverse('account'))
    else:
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(
            '{}?result={}&key={}'.format(reverse('register_new_step3'), is_allow_register, state))
