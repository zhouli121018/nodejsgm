# coding=utf-8
import os
import re
import time
import json
import pymongo
import datetime
import random
from passlib.hash import md5_crypt
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.core.cache import cache
from django_redis import get_redis_connection
from django.template.defaultfilters import date as dateformat
from django.utils.translation import ugettext_lazy as _
from app.core.models import ( Customer, CoreLog, CoreArea, CoreLoginAreaIp, CustomerOrder, CustomerInvoice, Pricing, Invoice,
                              CustomerContentRel, CustomerWayRel, CoreNotice, CoreNoticeLog, CoreNotification, CoreLogAutoReturn, Services, Prefs )
from app.address.models import ComplaintList
from app.core.configs import ( ACTION_TYPE, ORDER_STATUS, INVOICE_TYPE,
                               ESTIMATE_SELECT, CONTENT_SELECT, INDUSTRY_SELECT, WAY_SELECT, NOTIFICATION_TYPE )
from app.setting.models import NoticeSetting, TokenSetting, NoticeSettingDetail
from app.setting.configs import AREA_CONF_SHENGSHI
from app.setting.templatetags.setting_tags import show_token
from app.address.tools import check_qq_addr
from app.address.models import RecipientBlacklist
from app.address.forms import RecipientBlacklistForm, RecipientBlacklistBatchForm
from app.setting.utils import caches
from lib.IpSearch import IpSearch
from lib.common import get_object, get_service_obj_check
from lib.template import create_filepath
from app.utils.caches.decorators import cache_response, set_delete_cache_withpost

# ##  账户信息  ###
@login_required
def customer_account(request):
    if request.method == "POST":
        obj = Customer.objects.get(id=request.user.id)
        homepage = request.POST.get('homepage', '').strip()
        estimate = request.POST.get('estimate', '')
        industry = request.POST.get('industry', '')
        obj.homepage = homepage
        obj.estimate = estimate
        obj.industry = industry
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

        # redis = get_redis_connection()
        # redis.rpush('edm_web_notice_queue', json.dumps(
        #     {
        #         "type": "6",
        #         'customer_id': '{}'.format(request.user.id),
        #         "area": '',
        #         'point': '',
        #         'domain': '',
        #         'task': '',
        #     }
        # ))

        messages.add_message(request, messages.SUCCESS, _(u'修改详细信息成功'))
        return HttpResponseRedirect(reverse('account'))
    content_lists = CustomerContentRel.objects.filter(customer=request.user).values_list('content_type', flat=True)
    way_lists = CustomerWayRel.objects.filter(customer=request.user).values_list('way_type', flat=True)

    point, _created = Prefs.objects.get_or_create(name='register_credit')
    register_credit = int(point.value) if point.value else None
    if not register_credit:
        register_credit = 700

    return render(request, template_name='setting/customer_account.html', context={
        'content_lists': content_lists,
        'way_lists': way_lists,
        'estimate_selects': ESTIMATE_SELECT,
        'content_selects': CONTENT_SELECT,
        'industry_selects': INDUSTRY_SELECT,
        'way_selects': WAY_SELECT,
        'estimate_value_list': [ value[0] for value in ESTIMATE_SELECT ],
        'industry_value_list': [ value[0] for value in INDUSTRY_SELECT ],
        'register_credit': register_credit
    })

# 其它设置
@login_required
@cache_response(timeout=300)
def other_settings(request):
    if request.method == "POST":
        is_autoremove = request.POST.get('is_autoremove', '')
        is_auto_duplicate = request.POST.get('is_auto_duplicate', '')
        is_autoremove = True if is_autoremove.lower() in ('true', 'on') else False
        is_auto_duplicate = True if is_auto_duplicate.lower() in ('true', 'on') else False

        duplicate_type = request.POST.get('duplicate_type', '')
        obj = request.user.service()
        obj.is_autoremove = is_autoremove
        obj.is_auto_duplicate = is_auto_duplicate
        obj.duplicate_type = duplicate_type
        obj.save()

        if is_auto_duplicate:
            redis = get_redis_connection()
            # 客户地址池去重队列
            EDM_WEB_MAIL_DUPLICATE_QUEUE = 'edm_web_mail_duplicate_queue'
            redis.rpush(EDM_WEB_MAIL_DUPLICATE_QUEUE, int(request.user.id))

        messages.add_message(request, messages.SUCCESS, _(u'其他设置修改成功'))
        return HttpResponseRedirect(reverse('other_settings'))
    return render(request, template_name='setting/other_settings.html', context={
    })

@login_required
def customer_bind(request):
    return render(request, template_name='setting/customer_bind.html', context={
    })


@login_required
def wx_check_info(request):
    res = 0
    action = request.GET.get('action')
    if action == 'is_bind':
        if request.user.openid:
            res = 1
    return HttpResponse(json.dumps({'res': res}), content_type="application/json")


@login_required
def customer_bind_success(request):
    messages.add_message(request, messages.SUCCESS, _(u'绑定成功'))
    return HttpResponseRedirect(reverse('account'))


@login_required
def customer_unbind_success(request):
    messages.add_message(request, messages.SUCCESS, _(u'解除绑定成功'))
    return HttpResponseRedirect(reverse('account'))


@login_required
def ajax_alter_customer_field(request):
    if request.user.service().is_umail:
        return HttpResponse(json.dumps({'res': 'notok'}), content_type="application/json")
    data = request.POST
    field = data.get('name', '')
    field_var = data.get('value', '')
    obj = Customer.objects.get(id=request.user.id)
    if field == 'linkman':
        obj.linkman = field_var
        obj.save()
    elif field == 'mobile':
        obj.mobile = field_var
        obj.save()
    elif field == 'email':
        obj.email = field_var
        obj.save()
    elif field == 'im':
        obj.im = field_var
        obj.save()
    elif field == 'company':
        obj.company = field_var
        obj.save()
    elif field == 'weixin_customer':
        if not field_var:
            field_var = None
        obj.weixin_customer = field_var
        obj.save()
    elif field == 'ali_customer':
        if not field_var:
            field_var = None
        obj.ali_customer = field_var
        obj.save()
    return HttpResponse(json.dumps({'res': 'ok'}), content_type="application/json")


###  安全设置  ###
@login_required
def customer_security(request):
    return render(request, template_name='setting/customer_security.html', context={})

###  密码修改  ###
@login_required
def core_password_modify(request):
    obj = Customer.objects.get(id=request.user.id)
    is_admin = request.session.get('is_admin', False)
    if request.method == "POST":
        if is_admin:
            messages.add_message(request, messages.ERROR, u'你没有权限操作!')
            return HttpResponseRedirect(reverse('security'))
        if request.user.service().is_umail:
            messages.add_message(request, messages.ERROR, _(u'测试帐号不允许此类操作!'))
            return HttpResponseRedirect(reverse('security'))
        data = request.POST
        new_password2 = data.get('new_password2', None)
        password = md5_crypt.hash(new_password2)
        obj.password = password
        obj.save()
        messages.add_message(request, messages.SUCCESS, _(u'密码修改成功'))
        return HttpResponseRedirect(reverse('security'))
    return render(request, template_name='setting/core_password_modify.html', context={})


@login_required
def ajax_check_paasswd(request):
    data = request.POST
    raw_password = data.get('old_password', '')
    password = data.get('start_password', '')
    msg = {'msg': 'Y'}
    if not md5_crypt.verify(raw_password, password):
        msg = {'msg': 'N'}
    return HttpResponse(json.dumps(msg), content_type="application/json")


@login_required
def core_login_safe_set(request):
    obj, _created = CoreLoginAreaIp.objects.get_or_create(user_id=request.user.id)
    is_admin = request.session.get('is_admin', False)
    if request.method == "POST":
        if not request.user.weixin_customer:
            messages.add_message(request, messages.ERROR, _(u'请先去账户信息里绑定微信，再设置安全登录！'))
            return HttpResponseRedirect(reverse('security'))
        if is_admin:
            messages.add_message(request, messages.ERROR, u'你没有权限操作!')
            return HttpResponseRedirect(reverse('security'))
        if request.user.service().is_umail:
            messages.add_message(request, messages.ERROR, _(u'测试帐号不允许此类操作!'))
            return HttpResponseRedirect(reverse('security'))
        data = request.POST
        area_list = data.getlist('area_list[]', [])
        ip_list = data.getlist('ip_list[]', [])
        area_list_str = u','.join(area_list)
        ip_list_str = u','.join(ip_list)
        obj.area = area_list_str
        obj.ip = ip_list_str
        if area_list or ip_list:
            obj.is_open = True
            obj.save()
            msg = _(u'登录保护开启成功')
        else:
            obj.is_open = False
            obj.save()
            msg = _(u'登录保护未开启')
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(reverse('security'))
    area, ip = obj.area, obj.ip
    area_list, ip_list = [], []
    if area: area_list = area.split(',')
    if ip:   ip_list = ip.split(',')
    return render(request, template_name='setting/core_login_safe_set.html', context={
        # 'area_confs': AREA_CONF,
        "area_confs": AREA_CONF_SHENGSHI,
        'area_list': area_list,
        'ip_list': ip_list,
    })


@login_required
def ajax_check_login_ip(request):
    data = request.POST
    ip = data.get('ip', '')
    ip_search = IpSearch()
    ip_info = ip_search.Find(ip)
    msg = {'msg': 'Y'}
    if ip_info == u'N/A':
        msg = {'msg': 'N'}
    return HttpResponse(json.dumps(msg), content_type="application/json")


@login_required
def customer_token(request):
    if request.method == 'POST':
        id = request.POST.get('id', False)
        status = int(request.POST.get('status', False))
        if status == -1:
            TokenSetting.objects.get(id=id, customer=request.user).delete()
            messages.add_message(request, messages.SUCCESS, _(u'成功删除'))
        return HttpResponseRedirect(reverse('customer_token'))
    return render(request, template_name='setting/customer_token.html', context={})


@login_required
def ajax_create_token(request):
    data = request.POST
    name = data.get('name', '').strip()
    obj, _created = TokenSetting.objects.get_or_create(customer_id=request.user.id, name=name)
    if _created:
        token_src = make_password(name, None, 'unsalted_md5')
        obj.token = show_token(token_src)
        obj.save()
        return HttpResponse(json.dumps({
            'msg': 'Y',
            'id': str(int(obj.id)),
            'name': name,
            'token': token_src,
            'created': dateformat(obj.created, "Y-m-d H:i:s"),
        }), content_type="application/json")
    else:
        return HttpResponse(json.dumps({
            'msg': 'N',
            'name': name,
        }), content_type="application/json")


@login_required
def ajax_customer_token(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'name', 'token', 'created']
    lists = TokenSetting.objects.filter(customer_id=request.user.id)
    if search:
        lists = lists.filter(name__icontains=search)
    if lists.exists() and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            lists = lists.order_by('-%s' % colums[int(order_column)])
        else:
            lists = lists.order_by('%s' % colums[int(order_column)])
    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        page = int(data.get('start', '0')) / length + 1
    except ValueError:
        page = 1

    count = lists.count()
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    for d in lists.object_list:
        t = TemplateResponse(request, 'setting/ajax_customer_token.html', {'d': d})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


###  通知设置  ###
@login_required
@cache_response(timeout=300)
def customer_notice(request):
    lists = NoticeSetting.objects.filter(customer_id=request.user.id).order_by("id")
    if request.method == "POST":
        data = request.POST
        id = data.get('id', '')
        status = data.get('status', '')
        if status == '-1':  # 单个删除
            if lists.exists():
                master_id = lists.first().id
                if int(master_id) == int(id):
                    messages.add_message(request, messages.ERROR, u"不能删除主要联系人")
                    return HttpResponseRedirect(reverse('notice'))
            obj = get_object(NoticeSetting, request.user, id)
            obj.delete()
            msg = _(u'删除设置成功')
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(reverse('notice'))


    customer_notice_created = True
    if lists.count() >= 2:
        customer_notice_created = False
    return render(request, template_name='setting/customer_notice.html', context={
        'lists': lists,
        'notice_types': NOTIFICATION_TYPE,
        'customer_notice_created': customer_notice_created,
    })

@login_required
def customer_notice_create(request):
    if request.method == "POST":
        data = request.POST
        name = data.get('name', '').strip()
        mobile = data.get('mobile', '').strip()
        email = data.get('email', '').strip()
        balance_alert_qty = data.get('balance_alert_qty', '')
        if NoticeSetting.objects.filter(customer_id=request.user.id).count() >= 2:
            messages.add_message(request, messages.ERROR, _(u'添加设置失败, 最多添加两个通知人'))
            return HttpResponseRedirect(reverse('notice'))
        obj = NoticeSetting.objects.create(
            customer_id=request.user.id, name=name,
            mobile=mobile, email=email, balance_alert_qty=balance_alert_qty,
        )
        for k, v in NOTIFICATION_TYPE:
            d_obj, _c = NoticeSettingDetail.objects.get_or_create(setting=obj, type=k)
            if k == '5':
                d_obj.is_email = False
                d_obj.is_sms = False
                d_obj.is_notice = False
                d_obj.save()
        messages.add_message(request, messages.SUCCESS, _(u'添加设置成功'))
        set_delete_cache_withpost(request, url=reverse('notice'))
        return HttpResponseRedirect(reverse('notice'))
    return render(request, template_name='setting/customer_notice_create.html', context={})

@login_required
def customer_notice_modify(request, notice_id):
    obj = get_object(NoticeSetting, request.user, notice_id)
    if request.method == "POST":
        data = request.POST
        name = data.get('name', '').strip()
        mobile = data.get('mobile', '').strip()
        email = data.get('email', '').strip()
        balance_alert_qty = data.get('balance_alert_qty', '')
        obj.name = name
        obj.mobile = mobile
        obj.email = email
        obj.balance_alert_qty = balance_alert_qty
        obj.save()
        messages.add_message(request, messages.SUCCESS, _(u'修改设置成功'))
        set_delete_cache_withpost(request, url=reverse('notice'))
        return HttpResponseRedirect(reverse('notice'))
    context = {
        'notice_id': notice_id,
        'notice_obj': obj,
    }
    return render(request, template_name='setting/customer_notice_modify.html', context=context)

@csrf_exempt
@login_required
def ajax_notice_detail(request):
    notice_id = request.POST.get('notice_id', '')
    notice_type = request.POST.get('notice_type', '')
    notice_mode = request.POST.get('notice_mode', '')
    notice_flag = request.POST.get('notice_flag', '')
    if notice_id and notice_flag and notice_type and notice_mode:
        notice_flag = True if notice_flag.lower() == 'true' else False
        notice_obj = NoticeSetting.objects.filter(id=notice_id, customer=request.user).first()
        if notice_obj:
            d_obj, _created = NoticeSettingDetail.objects.get_or_create(setting=notice_obj, type=notice_type)
            if notice_mode == '1':
                d_obj.is_notice = notice_flag
                d_obj.save()
            elif notice_mode == '2':
                d_obj.is_email = notice_flag
                d_obj.save()
            elif notice_mode == '3':
                d_obj.is_sms = notice_flag
                d_obj.save()
            return HttpResponse(json.dumps({'status': 'Y'}), content_type="application/json")
    return HttpResponse(json.dumps({'status': 'N'}), content_type="application/json")

@login_required
def ajax_customer_notice(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'id', 'name', 'id', 'mobile']
    lists = NoticeSetting.objects.filter(customer_id=request.user.id)
    if search:
        lists = lists.filter(name__icontains=search)
    if lists.exists() and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            lists = lists.order_by('-%s' % colums[int(order_column)])
        else:
            lists = lists.order_by('%s' % colums[int(order_column)])
    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        page = int(data.get('start', '0')) / length + 1
    except ValueError:
        page = 1

    count = lists.count()
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page - 1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'setting/ajax_customer_notice.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1

    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@csrf_exempt
@login_required
def ajax_check_notice_param(request):
    notice_id = request.POST.get('notice_id', '')
    notice_ids = [int(notice_id)] if notice_id else []
    name = request.POST.get('name', '').strip()
    mobile = request.POST.get('mobile', '').strip()
    email = request.POST.get('email', '').strip()
    lists = NoticeSetting.objects.filter(customer=request.user).exclude(id__in=notice_ids)
    _existed_name = lists.filter(name=name).exists() if name else None
    if _existed_name:
        return HttpResponse(json.dumps({'status': 'EN', 'msg': _(u'姓名(%(name)s)已存在通知列表中,请核对') % {'name': name}}), content_type="application/json")
    _existed_mobile = lists.filter(mobile=mobile).exists() if mobile else None
    if _existed_mobile:
        return HttpResponse(json.dumps({'status': 'EM', 'msg': _(u'手机(%(mobile)s)已存在通知列表中,请核对') % {'mobile': mobile}}), content_type="application/json")
    _existed_email = lists.filter(email=email).exists() if email else None
    if _existed_email:
        return HttpResponse(json.dumps({'status': 'EE', 'msg': _(u'邮箱(%(email)s)已存在通知列表中,请核对') % {'email': email}}), content_type="application/json")
    return HttpResponse(json.dumps({'status': 'N', 'msg': ''}), content_type="application/json")


###  我的订单  ###
@login_required
def customer_order(request):
    service_obj = get_service_obj_check(request)
    if request.method == "POST":
        id = request.POST.get('id', '')
        status = request.POST.get('status', '')
        if status == 'cancel':
            order = CustomerOrder.objects.get(id=id, customer=request.user)
            order.status = status
            order.save()
            messages.add_message(request, messages.SUCCESS, _(u'订单(%(orderno)s)取消成功！') % {'orderno': order.orderno})
        return HttpResponseRedirect(reverse('order'))

    orderStatus = request.GET.get('orderStatus', '')
    date_start = request.GET.get('date_start', '')
    date_end = request.GET.get('date_end', '')
    return render(request, template_name='setting/customer_order.html', context={
        'status_types': ORDER_STATUS,
        'orderStatus': orderStatus,
        'date_start': date_start,
        'date_end': date_end,
    })


@login_required
def ajax_order(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    orderStatus = data.get('orderStatus', '')
    date_start = data.get('date_start', '')
    date_end = data.get('date_end', '')
    colums = ['id', 'id', 'orderno', 'id', 'id', 'id', 'id', 'id', 'status']
    lists = CustomerOrder.objects.filter(customer=request.user)
    today = datetime.date.today()
    dt_pay = (today - datetime.timedelta(days=180)).strftime('%Y-%m-%d')
    if orderStatus == 'notapply':
        lists = lists.filter(status='paied', dt_pay__gte=dt_pay)  #半年之内具备开发票
    elif orderStatus:
        lists = lists.filter(status=orderStatus)
    if date_start and date_end:
        lists = lists.filter(created__gte=date_start).filter(created__lte=date_end)
    elif date_start:
        lists = lists.filter(created__gte=date_start)
    elif date_end:
        lists = lists.filter(created__lte=date_end)
    if search:
        lists = lists.filter(orderno__icontains=search)
    if lists.exists() and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            lists = lists.order_by('-%s' % colums[int(order_column)])
        else:
            lists = lists.order_by('%s' % colums[int(order_column)])
    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        page = int(data.get('start', '0')) / length + 1
    except ValueError:
        page = 1

    count = lists.count()
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page - 1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'setting/ajax_order.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def ajax_check_order_notapply(request):
    order_ids = request.POST.get('order_ids', '')
    lists = CustomerOrder.objects.filter(customer=request.user, id__in=order_ids.split(','), status='yesapply').values_list('id', flat=True)
    msg = {'msg':'Y'}
    if lists:
        msg = {'msg':'N', 'lists': list(lists)}
    return HttpResponse(json.dumps(msg), content_type="application/json")


###  创建发票  ###
@login_required
def customer_invoice_create(request):
    if request.method == 'POST':
        data = request.POST
        order_ids = data.get('order_ids', '')
        amount = data.get('amount', '')
        recipient = data.get('recipient', '')
        address = data.get('address', '')
        phone = data.get('phone', '')
        zipcode = data.get('zipcode', '')
        invoice_type = data.get('invoice_type', '')
        invoice_title = data.get('invoice_title', '')
        tax_number = data.get('tax_number', '')
        bank = data.get('bank', '')
        acc_number = data.get('acc_number', '')
        company_addr = data.get('company_addr', '')
        company_phone = data.get('company_phone', '')

        order_objs = CustomerOrder.objects.filter(customer=request.user, id__in=order_ids.split(','))
        amount = 0
        for d in order_objs:
            amount += d.fee

        invoice_obj, _created = Invoice.objects.get_or_create(customer=request.user)
        if not invoice_obj.tax_number:
            invoice_obj.tax_number = tax_number
            invoice_obj.save()
        if invoice_type == '2':
            if not invoice_obj.bank:
                invoice_obj.bank = bank
            if not invoice_obj.acc_number:
                invoice_obj.acc_number = acc_number
            if not invoice_obj.company_addr:
                invoice_obj.company_addr = company_addr
            if not invoice_obj.company_phone:
                invoice_obj.company_phone = company_phone
            invoice_obj.save()

        obj = CustomerInvoice.objects.create(
            customer=request.user, amount=float(amount), status='apply', invoice_type=invoice_type,
            invoice_title=invoice_title, recipient=recipient, address=address, phone=phone, zipcode=zipcode,
            tax_number=tax_number, bank=bank, acc_number=acc_number, company_addr=company_addr, company_phone=company_phone,
        )

        order_objs.update(status='yesapply', invoice=obj)
        messages.add_message(request, messages.SUCCESS, _(u'申请发票成功！'))
        return HttpResponseRedirect(reverse('invoice'))

    order_ids = request.GET.get('order_ids', '')
    amounts = request.GET.get('amounts', '')
    order_obj = CustomerOrder.objects.filter(customer=request.user, id__in=order_ids.split(','))
    invoice_obj, _created = Invoice.objects.get_or_create(customer=request.user)
    context={
        'order_obj': order_obj,
        'order_ids': order_ids,
        'amounts': amounts,
        'invoice_type': INVOICE_TYPE,
        'invoice_obj': invoice_obj,
    }
    return render(request, template_name='setting/customer_invoice_create.html', context=context)

###   查看发票  ###
@login_required
def customer_invoice_view(request, invoice_id):
    context = {}
    if int(invoice_id):
        invoice_obj = CustomerInvoice.objects.get(id=invoice_id, customer=request.user,)
        order_obj = CustomerOrder.objects.filter(invoice_id=invoice_id, customer=request.user)
        context={
            'invoice_id': invoice_id,
            'invoice_obj': invoice_obj,
            'order_obj': order_obj,
        }
    return render(request, template_name='setting/customer_invoice_view.html', context=context)

###  发票信息管理  ###
@login_required
def customer_invoice_baseinfo(request):
    service_obj = get_service_obj_check(request)
    obj, _created = Invoice.objects.get_or_create(customer=request.user)
    if request.method == 'POST':
        data = request.POST
        recipient = data.get('recipient', '')
        address = data.get('address', '')
        phone = data.get('phone', '')
        zipcode = data.get('zipcode', '')
        invoice_type = data.get('invoice_type', '')
        invoice_title = data.get('invoice_title', '')
        tax_number = data.get('tax_number', '')
        bank = data.get('bank', '')
        acc_number = data.get('acc_number', '')
        company_addr = data.get('company_addr', '')
        company_phone = data.get('company_phone', '')

        obj.recipient = recipient
        obj.address = address
        obj.phone = phone
        obj.zipcode = zipcode
        obj.invoice_type = invoice_type
        obj.invoice_title = invoice_title
        obj.tax_number = tax_number
        if invoice_type == '2':
            obj.bank = bank
            obj.acc_number = acc_number
            obj.company_addr = company_addr
            obj.company_phone = company_phone
        obj.isvalid = True
        obj.save()
        messages.add_message(request, messages.SUCCESS, _(u'发票信息维护成功！'))
        return HttpResponseRedirect(reverse('customer_invoice_baseinfo'))
    return render(request, template_name='setting/customer_invoice_baseinfo.html', context={
        'invoice_obj': obj,
    })

@csrf_exempt
def customer_invoice_upload(request):
    attachfile = request.FILES.get('filedata', None)
    if not attachfile:
        return HttpResponse(json.dumps({'status': 'N'}), content_type="application/json")
    user_id = request.GET.get('user_id', '')
    obj, _created = Invoice.objects.get_or_create(customer=user_id)
    try:
        file_type = attachfile.content_type
        file_name = attachfile.name
        suffix = file_name.split('.')[-1]
        ufile_name = '{}.{}'.format('certificate_{}'.format(user_id), suffix)

        tpl_path = settings.CERTIFICATR_PATH
        file_path = os.path.join(tpl_path, ufile_name)
        create_filepath(tpl_path)
        with open(file_path, 'w') as f:
            f.write(attachfile.read())
        obj.file_type = file_type
        obj.file_path = ufile_name
        obj.save()
        img_html = u'<img src="/setting/invoice/upload/view/?user_id={}&aid=1&random={}" height="100" width="100">'.format(user_id, time.time())
        return HttpResponse(json.dumps({'status': 'Y','img_html': img_html}), content_type="application/json")
    except BaseException as e:
        return HttpResponse(json.dumps({'status': 'F'}), content_type="application/json")

# @login_required
def customer_invoice_upload_view(request):
    user_id = request.GET.get('user_id', '')
    aid = request.GET.get('aid', '')
    if aid in ('1', '2'):
        obj, _created = Invoice.objects.get_or_create(customer=user_id)
        file_type = obj.file_type
        file_path = os.path.join(settings.CERTIFICATR_PATH, obj.file_path)
        with open(file_path, 'r') as f:
            content = f.read()
        if aid == '1':
            return HttpResponse(content, content_type=file_type)
        else:
            return HttpResponse('<img src="{1}/setting/invoice/upload/view/?user_id={0}&aid=1">'.format(user_id, settings.EDM_WEB_URL), charset='utf-8')
    else:
        raise Http404

###  发票管理  ###
@login_required
def customer_invoice(request):
    service_obj = get_service_obj_check(request)
    return render(request, template_name='setting/customer_invoice.html', context={})


@login_required
def ajax_invoice(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    colums = ['id', 'id', 'amount', 'id', 'created', 'status']
    lists = CustomerInvoice.objects.filter(customer=request.user)
    if lists.exists() and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            lists = lists.order_by('-%s' % colums[int(order_column)])
        else:
            lists = lists.order_by('%s' % colums[int(order_column)])
    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        page = int(data.get('start', '0')) / length + 1
    except ValueError:
        page = 1

    count = lists.count()
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page - 1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'setting/ajax_invoice.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


###  操作日志列表  ###
@login_required
def customer_operate_log(request):
    data = request.GET
    action = data.get('action', '')
    date_start = data.get('date_start', '')
    date_end = data.get('date_end', '')
    return render(request, template_name='setting/customer_operate_log.html', context={
        'action_types': ACTION_TYPE,
        'action': action,
        'date_start': date_start,
        'date_end': date_end,
    })


@login_required
def ajax_operate_log(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    action = data.get('action', '')
    date_start = data.get('date_start', '')
    date_end = data.get('date_end', '')
    colums = ['id', 'action', 'datetime', 'desc', 'user_id', 'ip']
    lists = CoreLog.objects.filter(target=request.user)
    if action:
        lists = lists.filter(action=action)
    if date_start and date_end:
        lists = lists.filter(datetime__gte=date_start).filter(datetime__lte=date_end)
    elif date_start:
        lists = lists.filter(datetime__gte=date_start)
    elif date_end:
        lists = lists.filter(datetime__lte=date_end)
    if search:
        lists = lists.filter(desc__icontains=search)
    if lists.exists() and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            lists = lists.order_by('-%s' % colums[int(order_column)])
        else:
            lists = lists.order_by('%s' % colums[int(order_column)])
    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        page = int(data.get('start', '0')) / length + 1
    except ValueError:
        page = 1

    count = lists.count()
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page - 1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'setting/ajax_operate_log.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

###  系统自动返量  ###
@login_required
def customer_operate_log_return(request):
    data = request.GET
    daytime = data.get('daytime', '')
    try:
        lists = CoreLogAutoReturn.objects.filter(customer=request.user, datetime__gte='{} 00:00:00'.format(daytime), datetime__lte='{} 23:59:59'.format(daytime))
    except:
        raise Http404
    return render(request, template_name='setting/customer_operate_log_return.html', context={
        'lists': lists,
    })

mongo_cfg = {
    'host': settings.MONGO_HOST,
    'port': settings.MONGO_PORT,
    'username': settings.MONGO_USER,
    'dbname': settings.MONGO_DBNAME,
    'password': settings.MONGO_PWD,
}

# 无效地址
@login_required
def customer_invalid_address(request):
    mongo = pymongo.MongoClient(host='mongodb://{username}:{password}@{host}:{port}/{dbname}'.format(**mongo_cfg))
    db = mongo['mm-mc'].badmail
    db2 = mongo['mm-mc'].invalidqq
    key = ":django:edmweb:invalid_address:customer_invalid_address:count::"
    count = cache.get(key, None)
    # count = None
    if not count:
        invalid_qty = db.count()
        invalid_qty2 = db2.count()
        count = invalid_qty+invalid_qty2
        cache.set(key, count, 1800)

    # 跟新时间 随机选择一个
    # db.link.find().sort({"topic_id":1}).limit(1)   ## topic_id最小的doc
    # db.link.find().sort({"topic_id":-1}).limit(1)  ## topic_id最大的doc
    key2 = ":django:edmweb:invalid_address:customer_invalid_address:updatetime::"
    updatetime = cache.get(key2, None)
    if not updatetime:
        choice = random.choice(xrange(60, 3600))
        updatetime = datetime.datetime.now() - datetime.timedelta(seconds=choice)
        cache.set(key2, updatetime, 600)

    # 查询
    addresses = request.GET.get('addresses', '').lower()
    lists,addresses2 = [],''
    if addresses:
        address = addresses.split(',')
        addresses2 = addresses.replace(',', '\r\n')
        res = db.find({'addr': {"$in": tuple(address)}})
        lists1 = [one['addr'] for one in res]
        res = db2.find({'addr': {"$in": tuple(address)}})
        lists2 = [one['addr'] for one in res]
        lists = list(set(lists1)|set(lists2))
    return render(request, template_name='setting/customer_invalid_address.html', context={
        'invalid_qty': count,
        'updatetime': updatetime,
        'addresses': addresses2,
        'lists': lists,
    })

# 删除 无效地址
@login_required
def ajax_delete_invalid_address(request):
    addr = request.POST.get('addr', '').strip()
    mongo = pymongo.MongoClient(host='mongodb://{username}:{password}@{host}:{port}/{dbname}'.format(**mongo_cfg))
    db = mongo['mm-mc'].badmail
    db.remove({'addr': addr})
    if check_qq_addr(addr):
        db2 = mongo['mm-mc'].invalidqq
        db2.remove({'addr': addr})
    return HttpResponse(json.dumps({'msg': 'Y', }), content_type="application/json")

@login_required
def ajax_add_order(request):
    pricing_id = request.POST.get('pricing', '')
    payway = request.POST.get('payway', '')
    pricings = Pricing.objects.filter(disabled=False, id=pricing_id)
    if not pricings:
        raise Http404
    pricing_obj = pricings[0]
    obj = CustomerOrder.objects.create(
        fee=pricing_obj.pricing, product_detail=u'群发点数充值',
        product_desc=pricing_obj.name, qty_buy=pricing_obj.buy_count,
        customer=request.user, payway=payway
    )
    return HttpResponse(json.dumps({'url': obj.pre_pay_url}), content_type="application/json")


@login_required
def ajax_check_order(request):
    id = request.POST.get('id', '')
    obj = CustomerOrder.objects.get(orderno=id, customer=request.user)
    return HttpResponse(json.dumps({'status': obj.status}), content_type="application/json")


@login_required
def pricing(request):
    service_obj = get_service_obj_check(request)

    pricings = Pricing.objects.filter(disabled=False).order_by('buy_count')
    return render(request, template_name='setting/pricing.html', context={
        'pricings': pricings,
    })


@login_required
def modal_pre_pricing(request, id):
    pricings = Pricing.objects.filter(disabled=False, id=id)
    if not pricings:
        raise Http404

    obj = pricings[0]
    return render(request, template_name='setting/modal_pre_pricing.html', context={
        'obj': obj,
    })

@login_required
@cache_response(timeout=300)
def customer_complaint(request):
    return render(request, template_name='setting/customer_complaint.html', context={})

@login_required
@cache_response(timeout=300)
def ajax_complaint(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'address']
    lists = ComplaintList.objects.filter(customer=request.user)
    if search:
        lists = lists.filter(address__icontains=search)
    if lists.exists() and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            lists = lists.order_by('-%s' % colums[int(order_column)])
        else:
            lists = lists.order_by('%s' % colums[int(order_column)])
    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        page = int(data.get('start', '0')) / length + 1
    except ValueError:
        page = 1

    count = lists.count()
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page - 1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'setting/ajax_complaint.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

# 站内通知
@login_required
def customer_message(request):
    return HttpResponse( caches.customer_message(request) )

@login_required
def ajax_customer_message(request):
    content = caches.ajax_customer_message(request)
    return HttpResponse(json.dumps({"content":content}), content_type="application/json")

@csrf_exempt
@login_required
def ajax_customer_notice_active(request):
    lists = CoreNotice.objects.all().order_by('-id')
    msg_count = 0
    for obj in lists:
        _existed = CoreNoticeLog.objects.filter(notice_id=obj.id, customer_id=request.user.id).exists()
        if not _existed:
            msg_count += 1
    notify_count = CoreNotification.objects.filter(customer_id=request.user.id, is_read=False).count()
    count = msg_count + notify_count
    time = lists[0].start_time.strftime('%Y-%m-%d %H:%M:%S') if lists else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return HttpResponse(json.dumps({
        'msg_count': msg_count,
        'notify_count': notify_count,
        'count': count,
        'time': time,
    }), content_type="application/json")

# 站内公告
@login_required
def customer_message_log(request, notice_id):
    try:
        _obj = CoreNotice.objects.get(id=notice_id)
    except:
        return Http404

    lists = CoreNotice.objects.all()
    notice_ids = CoreNoticeLog.objects.filter(customer_id=request.user.id).values_list('notice_id', flat=True)
    not_lists = lists.exclude(id__in=notice_ids)
    for obj in not_lists:
        _existed = CoreNoticeLog.objects.filter(notice_id=obj.id, customer_id=request.user.id).exists()
        if not _existed:
            CoreNoticeLog.objects.create(notice_id=obj.id, customer_id=request.user.id, is_read=True)
    # _existed = CoreNoticeLog.objects.filter(notice_id=obj.id, customer_id=request.user.id).exists()
    # if not _existed:
    #     CoreNoticeLog.objects.create(notice_id=notice_id, customer_id=request.user.id, is_read=True)
    lists = lists.order_by('-id')
    return render(request, template_name='setting/customer_message_log.html', context={
        'lists': lists,
        # 'log_obj': obj,
    })

@login_required
def core_notification(request):
    return HttpResponse( caches.ajax_core_notification(request) )

@login_required
def ajax_core_notification(request):
    content = caches.ajax_core_notification(request)
    return HttpResponse(json.dumps({"content":content}), content_type="application/json")

@login_required
def core_notification_log(request, notify_id):
    try:
        obj = CoreNotification.objects.get(id=notify_id, customer=request.user)
    except:
        return Http404
    is_read = '' if obj.is_read else '0'
    CoreNotification.objects.filter(customer=request.user, is_read=False).update(is_read=True, is_notice=True)
    return render(request, template_name='setting/core_notification_lists.html', context={
        'is_read': is_read,
    })
    # if not obj.is_read:
    #     obj.is_read = True
    #     obj.is_notice = True
    #     obj.save()
    # return render(request, template_name='setting/core_notification_log.html', context={
    #     'notify_obj': obj,
    # })

@login_required
@cache_response(timeout=300)
def core_notification_lists(request):
    is_read = request.GET.get('is_read', '')
    return render(request, template_name='setting/core_notification_lists.html', context={
        'notice_types': NOTIFICATION_TYPE,
        'is_read': is_read,
    })

@login_required
@cache_response(timeout=300)
def ajax_core_notification_lists(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')

    is_read = data.get('is_read', '')
    type = data.get('type', '')

    colums = ['id', 'type', 'subject', 'created']
    lists = CoreNotification.objects.filter(customer=request.user)
    if is_read:
        is_read = False if is_read=='0' else True
        lists = lists.filter(is_read=is_read)
    if type:
        lists = lists.filter(type=type)
    # if search:
    #     lists = lists.filter(desc__icontains=search)
    if lists.exists() and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            lists = lists.order_by('-is_read', '-%s' % colums[int(order_column)])
        else:
            lists = lists.order_by('-is_read', '%s' % colums[int(order_column)])
    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        page = int(data.get('start', '0')) / length + 1
    except ValueError:
        page = 1

    count = lists.count()
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page - 1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'setting/ajax_core_notification_lists.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


################################
# 发件人黑名单
@login_required
@cache_response(timeout=300)
def rcpblack(request):
    if request.method == "POST":
        status = request.POST.get('status', False)
        if status == "delete":
            id = request.POST.get('id', False)
            obj = get_object(RecipientBlacklist, request.user, id)
            obj.delete()
            messages.add_message(request, messages.SUCCESS, _(u'删除成功'))
        if status == "batchdelete":
            ids = request.POST.get('ids', False)
            ids = ids.split(',')
            RecipientBlacklist.objects.filter(user=request.user, id__in=ids).delete()
            messages.add_message(request, messages.SUCCESS, _(u'删除成功'))
        return HttpResponseRedirect(reverse('rcpblack'))
    return render(request, template_name='setting/rcpblack.html', context={
    })

@login_required
@cache_response(timeout=300)
def ajax_rcpblack(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'id', 'addr', 'created']
    lists = RecipientBlacklist.objects.filter(user=request.user)
    if search:
        lists = lists.filter(addr__icontains=search)
    if order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            lists = lists.order_by('-%s' % colums[int(order_column)])
        else:
            lists = lists.order_by('%s' % colums[int(order_column)])

    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        page = int(data.get('start', '0')) / length + 1
    except ValueError:
        page = 1

    count = lists.count()
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page - 1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'setting/ajax_rcpblack.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

@login_required
def rcpblack_add(request):
    form = RecipientBlacklistForm(request.user)
    if request.method == "POST":
        form = RecipientBlacklistForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            set_delete_cache_withpost(request, url=reverse('rcpblack'))
            messages.add_message(request, messages.SUCCESS, _(u'黑名单添加成功'))
            return HttpResponseRedirect(reverse('rcpblack'))
    return render(request, 'setting/rcpblack_add.html', context={
        'form': form,
        'rcpblack_flag': 'add',
    })

@login_required
def rcpblack_batchadd(request):
    form = RecipientBlacklistBatchForm()
    if request.method == "POST":
        words = request.POST.get('addrs', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form2 = RecipientBlacklistForm(request.user, { 'addr': w.replace('\r', '') })
            if form2.is_valid():
                success += 1
                form2.save()
            else:
                fail += 1
            set_delete_cache_withpost(request, url=reverse('rcpblack'))
        messages.add_message(request, messages.SUCCESS, _(u'批量添加成功%(success)s个, 失败%(fail)s个') % {"success": success, "fail": fail})
        return HttpResponseRedirect(reverse('rcpblack'))
    return render(request, 'setting/rcpblack_add.html', context={
        'form': form,
        'rcpblack_flag': 'batchadd',
    })

@login_required
def rcpblack_modify(request, black_id):
    obj = RecipientBlacklist.objects.get(id=black_id)
    form = RecipientBlacklistForm(request.user, instance=obj)
    if request.method == "POST":
        form = RecipientBlacklistForm(request.user, request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('rcpblack'))
    return render(request, 'setting/rcpblack_add.html', context={
        'form': form,
        'rcpblack_flag': 'modify',
    })
