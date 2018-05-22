# coding=utf-8
import qrcode
import datetime
import random
import json
import urllib
import os
import requests
from StringIO import StringIO
from django.shortcuts import render
from django.conf import settings
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.views import auth_login
from django.contrib.auth import authenticate
from django_redis import get_redis_connection
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from wechat_sdk.basic import WechatBasic
from wechat_sdk.messages import TextMessage
from lib.weixin import WeixinAPI
from lib.weixin.pay import NativeLink_pub, UnifiedOrder_pub, Notify_pub
from app.core.models import WeixinCustomer, Customer, CustomerOrder, CoreLog
from app.wechat.models import WeixinLog
from app.core.models import Customer
from lib.pushcrew import pushcrew_notice

wechat_instance = WechatBasic(token=settings.MP_WX_TOKEN, appid=settings.MP_WX_APPID,
                              appsecret=settings.MP_WX_APPSECRET)


@csrf_exempt
def wechat(request):
    # 检验合法性 从 request 中提取基本信息 (signature, timestamp, nonce, xml)
    import sys
    import traceback

    try:
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        openid = request.GET.get('openid')
        if not wechat_instance.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
            return HttpResponseBadRequest('Verify Failed')
        if request.method == 'GET':
            return HttpResponse(request.GET.get('echostr', ''), content_type="text/plain")

        wechat_instance.parse_data(request.body)
        message = wechat_instance.message
        # qrscene_4499, 4499
        print >> sys.stderr, message.__dict__
        print >> sys.stderr, type(message)

        if isinstance(message, TextMessage):
            return HttpResponse(wechat_instance.response_text(_(u'如果您有任何问题，请咨询U-Mail客服。 QQ:4008181568 ,TEL:400-8181-568！')), content_type="text/plain")

        scene_id = int(message.key.split('_')[-1])
        print >> sys.stderr, 'scene_id', scene_id
        key = 'wx_{}'.format(scene_id)
        redis = get_redis_connection()
        user_info = wechat_instance.get_user_info(openid)
        user = Customer.objects.get(id=scene_id)
        if not user.weixin_customer:
            # refresh_token = api.exchange_refresh_token_for_access_token(refresh_token=auth_info['refresh_token'])
            unionid = user_info['unionid']
            headimgurl = user_info['headimgurl']
            weixin_user, _created = WeixinCustomer.objects.get_or_create(unionid=unionid)
            Customer.objects.filter(weixin_customer=weixin_user).exclude(id=request.user.id).update(
                weixin_customer=None)

            if headimgurl:
                filepath = os.path.join(settings.BASE_DIR, 'static', 'weixin_img')
                filename = '{}.png'.format(unionid)
                with open(os.path.join(filepath, filename), 'wb') as f:
                    try:
                        f.write(requests.get(headimgurl).content)
                        staticimgurl = '/static/weixin_img/{}'.format(filename)
                    except:
                        staticimgurl = None
                weixin_user.staticimgurl = staticimgurl

            weixin_user.openid = user_info['openid']
            weixin_user.province = user_info['province']
            weixin_user.headimgurl = headimgurl
            weixin_user.language = user_info['language']
            weixin_user.city = user_info['city']
            weixin_user.country = user_info['country']
            weixin_user.sex = user_info['sex']
            weixin_user.nickname = user_info['nickname']

            weixin_user.save()
            user.weixin_customer = weixin_user
            user.save()
        p = redis.pipeline()
        p.hset(key, 'is_dealed', 1)
        p.expire(key, 3600)
        p.execute()
        return HttpResponse(wechat_instance.response_text(_(u'感谢您的绑定与关注！')), content_type="text/plain")
    except:
        print >> sys.stderr, traceback.format_exc()
        return HttpResponse(wechat_instance.group_transfer_message(), content_type="text/plain")


@login_required
def ajax_check_bind(request):
    redis = get_redis_connection()
    key = 'wx_{}'.format(request.user.id)
    is_dealed = -1
    if redis.exists(key):
        is_dealed = int(redis.hget(key, 'is_dealed'))
        if is_dealed == 1:
            messages.add_message(request, messages.SUCCESS, _(u'微信绑定成功'))
            redis.delete(key)
    return HttpResponse(json.dumps({'res': is_dealed}), content_type="application/json")


@login_required
def bind_wechat(request):
    redis = get_redis_connection()
    key = 'wx_{}'.format(request.user.id)
    p = redis.pipeline()
    p.hset(key, 'is_dealed', 0)
    p.expire(key, 3600)
    p.execute()
    return render(request, template_name='wechat/bind_wechat.html', context={
    })


@login_required
def bind_img(request):
    redis = get_redis_connection()
    # params = {"action_name": "QR_LIMIT_STR_SCENE", "action_info": {"scene": {"scene_str": "123"}}}
    # scene_id = random.randint(1, 100000)
    user_id = request.user.id
    key = 'wx_{}'.format(user_id)
    image_data = redis.hget(key, 'image_data')
    if not image_data:
        params = {"expire_seconds": 3600, "action_name": "QR_SCENE", "action_info": {"scene": {'scene_id': user_id}}}
        # qrcode = {u'url': u'http://weixin.qq.com/q/020Y8UUxf3fe11qYe6No1J', u'expire_seconds': 604800, u'ticket': u'gQH77zwAAAAAAAAAAS5odHRwOi8vd2VpeGluLnFxLmNvbS9xLzAyMFk4VVV4ZjNmZTExcVllNk5vMUoAAgQ8VD1YAwSAOgkA'}
        ticket = wechat_instance.create_qrcode(params).get('ticket', '')
        image_data = urllib.urlopen("https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket={}".format(ticket)).read()
        p = redis.pipeline()
        p.hset(key, 'ticket', ticket)
        p.hset(key, 'image_data', image_data)
        p.hset(key, 'is_dealed', 0)
        p.expire(key, 3600)
        p.execute()
    return HttpResponse(image_data, content_type="image/png")


@csrf_exempt
def callback(request):
    """
    info = {u'openid': u'oMaZnwp6MCKAxjBi0anwBsMKf3pw',
            u'access_token': u'8amyiVIWd3Ssafb08HED-8xNIB5DDDsFm6QW-bIwMaKPmFJUFA9X6X7i3rNnazqOTGNeA7jNBs8X8S-4cd9moIMZsKaT0BAFj_LjteX_Yxk',
            u'unionid': u'oh8S_wRSPZ5PfCeFnoDlPV8V1H2M', u'expires_in': 7200, u'scope': u'snsapi_login',
            u'refresh_token': u'pEbXllcSyDPMmFe4X7wmxcvmMU8A_5DfAmISaTSlYvf9cCoO6AlknluOu-2NmfdUfUMunMlrgj3bGMeR0FRctAl3mxJMUbUkJux0zl-fXu4'}
    user_info = {u'province': u'Guangdong', u'openid': u'oMaZnwp6MCKAxjBi0anwBsMKf3pw',
     u'headimgurl': u'http://wx.qlogo.cn/mmopen/PiajxSqBRaEJHPI6VNY6HmnSibI23ahh1024IYGEnYtcUxjvHDuqapdXKiacYt0lZWte9dbkVye1RJqXoDx5vI6Pw/0',
     u'language': u'zh_CN', u'city': u'Shenzhen', u'country': u'CN', u'sex': 1,
     u'unionid': u'oh8S_wRSPZ5PfCeFnoDlPV8V1H2M', u'privilege': [], u'nickname': u'\u6728\u5b50\u5a01'}
     wechat/callback?code=031OnCTU0JGrJW1239SU0GFyTU0OnCTy&state=a17c532afc204a88
     """
    user = request.user
    code = request.GET.get('code', '')
    if not code:
        return HttpResponse('callback')

    api = WeixinAPI(appid=settings.OPEN_WX_APPID, app_secret=settings.OPEN_WX_KEY,
                    redirect_uri=settings.OPEN_WX_LOGIN_URI)
    auth_info = api.exchange_code_for_access_token(code=code)
    unionid = auth_info['unionid']
    # 如果是登陆情况 且没有进行绑定操作　则进行绑定操
    if user.is_authenticated:
        if not user.weixin_customer:
            # refresh_token = api.exchange_refresh_token_for_access_token(refresh_token=auth_info['refresh_token'])
            weixin_user, bool = WeixinCustomer.objects.get_or_create(unionid=unionid)
            if bool:
                print 'get weixin user info'
                api = WeixinAPI(access_token=auth_info['access_token'])
                user_info = api.user(openid=auth_info['openid'])

                headimgurl = user_info['headimgurl']
                openid = user_info['openid']
                filepath = os.path.join(settings.BASE_DIR, 'static', 'weixin_img')
                filename = '{}.png'.format(openid)
                with open(os.path.join(filepath, filename), 'wb') as f:
                    f.write(requests.get(headimgurl).content)
                staticimgurl = '/static/weixin_img/{}'.format(filename)

                weixin_user.openid = openid
                weixin_user.access_token = auth_info['access_token']
                weixin_user.refresh_token = auth_info['refresh_token']
                weixin_user.province = user_info['province']
                weixin_user.headimgurl = headimgurl
                weixin_user.staticimgurl = staticimgurl
                weixin_user.language = user_info['language']
                weixin_user.city = user_info['city']
                weixin_user.country = user_info['country']
                weixin_user.sex = user_info['sex']
                weixin_user.nickname = user_info['nickname']
                weixin_user.save()
            else:
                Customer.objects.filter(weixin_customer=weixin_user).exclude(id=request.user.id).update(
                    weixin_customer=None)
            user.weixin_customer = weixin_user
            user.save()
            messages.add_message(request, messages.SUCCESS, _(u'微信绑定成功'))
        else:
            messages.add_message(request, messages.ERROR, _(u'您有绑定其他微信，请先解除绑定!'))
        return HttpResponseRedirect('http://{}{}'.format(settings.HOSTNAME, reverse('account')))
    else:
        weixin_users = WeixinCustomer.objects.filter(unionid=unionid)
        users = Customer.objects.filter(weixin_customer=weixin_users[0]) if weixin_users else []
        # 如果找到相应绑定客户，进行扫描登陆
        if users:
            user = users[0]
            if user.disabled == "1":
                messages.add_message(request, messages.ERROR, _(u'此账户已被冻结！'))
                return HttpResponseRedirect('http://{}{}'.format(settings.HOSTNAME, reverse('home')))
            else:
                user = authenticate(username=user.username, password='', t_password=user.password)
                auth_login(request, user)
                # 登录日志
                user.save_fast_login_log(request, mode='wechat')
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])

                # 支付宝登录通知销售
                sss = user.service()
                if sss and sss.is_pushcrew:
                    action = "service"
                    title = u"微信登录提醒"
                    message = u"{}（ID: {}） 于 {} 时间登录平台".format(
                        user.company, user.id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    pushcrew_notice(action, title, message)

                return HttpResponseRedirect('http://{}{}'.format(settings.HOSTNAME, reverse('home')))
        else:
            messages.add_message(request, messages.ERROR, _(u'此微信号并未于平台账号绑定，请先绑定账号!'))
            return HttpResponseRedirect('http://{}{}'.format(settings.HOSTNAME, reverse('home')))


@login_required
def pre_pay(request):
    id = request.GET.get('id', '')
    order = CustomerOrder.objects.get(orderno=id, customer=request.user)
    return render(request, template_name='wechat/pre_pay.html', context={
        'order': order
    })


@login_required
def pay_qrcode(request, product_id):
    order = CustomerOrder.objects.get(orderno=product_id, customer=request.user)
    n = UnifiedOrder_pub()
    n.setParameter('product_id', order.orderno)
    n.setParameter("body", u"群发点数充值")  # 商品描述
    n.setParameter("out_trade_no", order.orderno)  # 商户订单号
    n.setParameter("total_fee", str(int(order.fee) * 100))  # 总金额
    n.setParameter("trade_type", "NATIVE")  # 交易类型
    url = n.getCodeUrl()
    WeixinLog.objects.create(type='UnifiedOrder', body=n.response)
    buf = StringIO()
    img = qrcode.make(url)
    img.save(buf)
    return HttpResponse(buf.getvalue(), content_type="image/jpeg")


@csrf_exempt
def payback(request):
    """
    微信支付回调函数
    :param request:
    :return:
    """
    return HttpResponse('payback')


@login_required
def pay_success(request):
    id = request.GET.get('id', '')
    order = CustomerOrder.objects.get(orderno=id, customer=request.user)
    messages.add_message(request, messages.SUCCESS, _(u'订单(%(orderno)s)　支付成功!') % {'orderno': order.orderno})
    return HttpResponseRedirect(reverse('order'))


@csrf_exempt
def pay_notify(request):
    """
    微信支付通知函数
    :param request:
    :return:
    """
    body = request.body
    n = Notify_pub()
    n.saveData(body)
    data = n.getData()
    id = data.get('out_trade_no', '')
    order = CustomerOrder.objects.get(orderno=id)
    is_sign = n.checkSign()
    WeixinLog.objects.create(type='PayNotify', body=body, is_sign=is_sign)
    if order.status == 'paied':
        return HttpResponse(n.returnSuccessXml())
    if n.checkSign():
        order.openid = data.get('openid', '')
        is_subscribe = data.get('is_subscribe', 'N')
        order.is_subscribe = True if is_subscribe == 'Y' else False
        order.transaction_id = data.get('transaction_id', '')
        order.return_code = data.get('return_code', '')
        order.return_msg = data.get('return_msg', '')
        order.result_code = data.get('result_code', '')
        order.bank_type = data.get('bank_type', '')
        time_end = data.get('time_end', '')
        if time_end:
            order.dt_pay = datetime.datetime.strptime(time_end, '%Y%m%d%H%M%S')
        if order.result_code == 'SUCCESS':
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
                                   action='c_update_count', desc=u'{}元/{}点(微信充值)'.format(fee, qty_buy))
        order.save()
        return HttpResponse(n.returnSuccessXml())
    return HttpResponse(n.returnXml())


def create_menu(request):
    menu = {
        'button': [
            {
                'name': '关于我们',
                'sub_button': [
                    {
                        'type': 'view',
                        'name': '产品介绍',
                        'url': 'http://wap.magvision.com/mail/'
                    },
                    {
                        'type': 'view',
                        'name': '公司介绍',
                        'url': 'http://wap.magvision.com/about/'
                    },
                    {
                        'type': 'view',
                        'name': '联系方式',
                        'url': 'http://wap.magvision.com/contact'
                    },
                ]
            },
            {
                'name': '营销知识',
                'sub_button': [
                    {
                        'type': 'view',
                        'name': '营销技巧',
                        'url': 'http://wap.magvision.com/view/'
                    },
                    {
                        'type': 'view',
                        'name': '常见问题',
                        'url': 'http://wap.magvision.com/problem/'
                    },
                    {
                        'type': 'view',
                        'name': '营销案例',
                        'url': 'http://wap.magvision.com/case/'
                    },
                ]
            },
            {
                'name': '申请试用',
                'type': 'view',
                'url': 'http://app.magvision.com/register_new/'
            }
        ]}
    wechat_instance.create_menu(menu)
    return HttpResponse('create menu')

