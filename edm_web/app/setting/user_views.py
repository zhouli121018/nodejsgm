# coding=utf-8

import json
import datetime
import math
import hashlib
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.db.models import Q, Count, F
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.translation import ugettext_lazy as _

from passlib.hash import md5_crypt
from lib.IpSearch import IpSearch
from lib.common import get_client_ip
from lib.ipparse import split_ip_to_area_title
from app.core.models import Customer, Services, CoreLog, CustomerDomain, CustomerMailbox, CustomerDomainMailboxRel, SubAccoutManager
from app.setting.utils.children import get_customer_child_obj


@login_required
def sub_account(request):
    service_obj = request.user.service()
    qty_buytotal = service_obj.qty_buytotal
    if service_obj.is_share_flag in('2', '3', '4'):
        raise Http404

    if request.method == "POST":
        user_id = request.POST.get('id', '0')
        status = request.POST.get('status', '0')
        obj = get_customer_child_obj(request, int(user_id))
        if int(status) == 1:
            # 启用
            obj.disabled = '0'
            obj.save()

            sub_service_obj = obj.service()
            sub_service_obj.disabled = '0'
            sub_service_obj.save()
            messages.add_message(request, messages.SUCCESS, _('启用子账户成功'))
        if int(status) == 2:
            # 禁用
            obj.disabled = '1'
            obj.save()

            sub_service_obj = obj.service()
            sub_service_obj.disabled = '1'
            sub_service_obj.save()
            messages.add_message(request, messages.SUCCESS, _('禁用子账户成功'))

        if int(status) == 7:
            # 禁止导出跟踪地址
            sub_service_obj = obj.service()
            sub_service_obj.is_track_export=False
            sub_service_obj.save()
            messages.add_message(request, messages.SUCCESS, _('禁止导出跟踪地址设置成功'))
        if int(status) == 8:
            # 允许导出跟踪地址
            sub_service_obj = obj.service()
            sub_service_obj.is_track_export=True
            sub_service_obj.save()
            messages.add_message(request, messages.SUCCESS, _('允许导出跟踪地址设置成功'))
        return HttpResponseRedirect(reverse('sub_account'))

    limit_count = int(math.floor(float(qty_buytotal)/float(100000)))
    limit_count = 50 if limit_count>50 else limit_count
    lists = Customer.objects.filter(parent_id=request.user.id).order_by('id')
    subloging_auth = hashlib.md5('%s-%s' % (settings.WEB_API_AUTH_KEY, datetime.datetime.now().strftime("%Y%m%d"))).hexdigest()
    return render(request, template_name='setting/sub_account.html', context={
        'lists': lists,
        'limit_count': limit_count,
        'subloging_auth': subloging_auth,
    })

def generate_username(request, sub_count, limit_count):
    count = sub_count + 1
    end_count = limit_count + 1
    username = None
    for index in xrange(count, end_count):
        username = u'{}0{}'.format(request.user.username, index)
        if Customer.objects.filter(username=username).exists():
            continue
        break
    if not username:
        zero_count = u'00'
        for index in xrange(count, end_count):
            username = u'{}{}{}'.format(request.user.username, zero_count, index)
            if Customer.objects.filter(username=username).exists():
                continue
            break
    return username

@login_required
def sub_account_create(request):
    service_obj = request.user.service()
    qty_buytotal = service_obj.qty_buytotal
    if service_obj.is_share_flag in('2', '3', '4'):
        raise Http404
    if qty_buytotal < 100000:
        # messages.add_message(request, messages.ERROR, _('充值总量不足10万, 每充值10万封允许添加一个子账户。'))
        # return HttpResponseRedirect(reverse('sub_account'))
        # messages.add_message(request, messages.ERROR, _('充值总量不足10万, 每充值10万封允许添加一个子账户。'))
        # return redirect('sub_account')
        return render(request, template_name='setting/sub_account_create.html', context={
            "cannot_add": True,
        })

    limit_count = int(math.floor(float(qty_buytotal)/float(100000)))
    limit_count = 50 if limit_count>50 else limit_count
    sub_count = Customer.objects.filter(parent_id=request.user.id).count()
    if request.method == "POST":
        if sub_count >= limit_count:
            messages.add_message(request, messages.ERROR, _(u'添加子账户失败，已达到添加子账户的上限（%(limit_count)s）！') % {'limit_count': limit_count,})
            return HttpResponseRedirect(reverse('sub_account'))
        data = request.POST
        new_password2 = data.get('new_password2', None)
        password = md5_crypt.hash(new_password2)

        company = data.get('company', None)
        linkman = data.get('linkman', None)
        mobile = data.get('mobile', None)
        email = data.get('email', None)

        create_type  = data.get('create_type', '')
        if create_type == '1':  # 分配
            is_share_flag = '2'
            limit_qty = 0
            qty_count  = data.get('qty_count', '')
            qty_count= int(qty_count)
            if qty_count >= int(service_obj.qty_count):
                messages.add_message(request, messages.ERROR, _(u'分配的群发量已大于等于剩余群发量，添加子账户失败！'))
                return HttpResponseRedirect(reverse('sub_account'))
        else:
            qty_count = 0
            share_type = data.get('share_type', '')
            if share_type == '1': # 全部共享
                limit_qty = 0
                is_share_flag = '4'
            else:                # 部分共享
                is_share_flag = '3'
                limit_qty = int(data.get('limit_qty', '0'))

        username = generate_username(request, sub_count, limit_count)

        manager_id = request.user.manager_id if request.user.manager_id else None
        sub_obj = Customer.objects.create(
            username=username,
            password=password,
            company=company,
            linkman=linkman,
            mobile=mobile,
            email=email,
            is_new=True,

            parent=request.user,
            manager_id=manager_id,
            phone=request.user.phone,
            im=request.user.im,
            address=request.user.address,
            homepage=request.user.homepage,
            estimate=request.user.estimate,
            industry=request.user.industry,
            web_style=request.user.web_style,
            lang_code=request.user.lang_code,
        )

        sub_service_obj = Services.objects.create(
            customer=sub_obj,
            is_trial=service_obj.is_trial,
            is_verify=service_obj.is_verify,
            server_type=service_obj.server_type,
            send_type=service_obj.send_type,
            service_type=service_obj.service_type,
            service_end='2099-12-31 23:59:59',
            error_stat_ratio=service_obj.error_stat_ratio,
            refuse_error_stat_ratio=service_obj.refuse_error_stat_ratio,
            ws_rate_limit=service_obj.ws_rate_limit,
            addr_export=service_obj.addr_export,
            addr_export_max=service_obj.addr_export_max,
            timezone=service_obj.timezone,
            cannotview_html=service_obj.cannotview_html,
            unsubscribe_html=service_obj.unsubscribe_html,
            is_maintain=service_obj.is_maintain,
            is_high_quality=service_obj.is_high_quality,
            is_replace_sender=service_obj.is_replace_sender,
            is_allow_red_tpl=service_obj.is_allow_red_tpl,
            is_allow_cy_tpl=service_obj.is_allow_cy_tpl,
            maintain_rate=service_obj.maintain_rate,
            is_autoremove=service_obj.is_autoremove,
            is_auto_duplicate=service_obj.is_auto_duplicate,
            duplicate_type=service_obj.duplicate_type,
            is_stmp=service_obj.is_stmp,
            is_need_receipt=service_obj.is_need_receipt,
            is_open_accurate=service_obj.is_open_accurate,
            is_umail=service_obj.is_umail,

            qty_count=qty_count,
            qty_valid=qty_count,
            qty_buytotal=0,

            is_share_flag=is_share_flag,
            limit_qty=limit_qty,
            is_address=False,
            is_template=False,
            is_task=False,
        )
        client_ip = get_client_ip(request)
        if create_type == '1':
            service_obj.qty_count = F('qty_count') - qty_count
            service_obj.qty_valid = F('qty_valid') - qty_count
            # service_obj.qty_buytotal = F('qty_buytotal') - qty_count
            service_obj.save()

            CoreLogList = [
                CoreLog(
                    user=request.user, user_type='users', target=request.user,
                    target_name=u'{0} - {0}'.format(request.user.username),
                    action='add_subuser', ip=client_ip, desc=u'给子账户分配群发量：{}'.format(qty_count)
                ),
                CoreLog(
                    user=request.user, user_type='users', target=request.user,
                    target_name=u'{0} - {0}'.format(request.user.username),
                    action='recharge_subuser', ip=client_ip, desc=u'-{}（分配群发量）'.format(qty_count)
                ),
                CoreLog(
                    user=request.user, user_type='users', target=sub_obj,
                    target_name=u'{0} - {0}'.format(sub_obj.username),
                    action='add_subuser', ip=client_ip, desc=u'分配方式创建，获得群发量：{}'.format(qty_count)
                ),
                CoreLog(
                    user=request.user, user_type='users', target=sub_obj,
                    target_name=u'{0} - {0}'.format(request.user.username),
                    action='recharge_subuser', ip=client_ip, desc=u'+{}（分配群发量）'.format(qty_count)
                ),
            ]
            CoreLog.objects.bulk_create(CoreLogList)
        else:
            desc = u'全部共享' if share_type == '1' else u'部分共享，子账户最多可以使用母账户群发量为：{}'.format(limit_count)
            CoreLogList = [
                CoreLog(
                    user=request.user, user_type='users', target=request.user,
                    target_name=u'{0} - {0}'.format(request.user.username),
                    action='add_subuser', ip=client_ip, desc=desc
                ),
                CoreLog(
                    user=request.user, user_type='users', target=sub_obj,
                    target_name=u'{0} - {0}'.format(sub_obj.username),
                    action='add_subuser', ip=client_ip, desc=desc
                ),
            ]
            CoreLog.objects.bulk_create(CoreLogList)
        messages.add_message(request, messages.SUCCESS, _(u'添加子账户成功'))
        return HttpResponseRedirect(reverse('sub_account'))
    return render(request, template_name='setting/sub_account_create.html', context={
        'leave_qty': service_obj.qty_count,
    })

# 重置密码
@login_required
def sub_account_reset(request, user_id):
    obj = get_customer_child_obj(request, user_id)
    if request.method == "POST":
        new_password2 = request.POST.get('new_password2', None)
        password = md5_crypt.hash(new_password2)
        obj.password = password
        obj.save()
        messages.add_message(request, messages.SUCCESS, _(u'密码修改成功'))
        return HttpResponseRedirect(reverse('sub_account'))

    return render(request, template_name='setting/sub_account_reset.html', context={
        'user_obj': obj,
        'user_id': user_id,
    })

# 设置权限
# <a data-toggle="modal" href="{% url 'sub_account_perm' d.id %}" data-target="#myModal" class="btn btn-outline btn-success btn-xs" data-whatever="">{% trans '设置权限' %}</a>
@login_required
def sub_account_perm(request, user_id):
    obj = get_customer_child_obj(request, user_id)
    sub_service_obj = obj.service()
    if request.method == "POST":
        is_address = request.POST.get('is_address', '')
        is_template = request.POST.get('is_template', '')
        is_task = request.POST.get('is_task', '')
        is_address = True if is_address.lower() in ('true', 'on') else False
        is_template = True if is_template.lower() in ('true', 'on') else False
        is_task = True if is_task.lower() in ('true', 'on') else False

        sub_service_obj.is_address = is_address
        sub_service_obj.is_template = is_template
        sub_service_obj.is_task = is_task
        sub_service_obj.save()

        messages.add_message(request, messages.SUCCESS, _(u'修改子账户权限成功'))
        return HttpResponseRedirect(reverse('sub_account'))
    return render(request, template_name='setting/sub_account_perm.html', context={
        'user_id': user_id,
        'sub_service_obj': sub_service_obj,
    })

# 共享发件人
@login_required
def sub_account_share(request, user_id):
    obj = get_customer_child_obj(request, user_id)
    if request.method == "POST":
        send_domain_id = request.POST.get('send_domain', '')
        mailbox_ids = request.POST.getlist('mailbox_ids[]', '')
        mailbox_ids = map(int, mailbox_ids)

        domain_obj = CustomerDomain.objects.filter(id=send_domain_id, customer=request.user).first()
        if not domain_obj:
            messages.add_message(request, messages.ERROR, _(u'共享发件人失败'))
            return HttpResponseRedirect(reverse('sub_account'))

        mailbox_lists = CustomerMailbox.objects.filter(customer=request.user, domain=domain_obj.domain, disabled='0', id__in=mailbox_ids)
        if not mailbox_lists:
            messages.add_message(request, messages.ERROR, _(u'共享发件人失败'))
            return HttpResponseRedirect(reverse('sub_account'))

        domain_ctype = ContentType.objects.get_for_model(domain_obj)
        box_ctype = ContentType.objects.get_for_model(mailbox_lists[0])
        bulk_lists = []
        if not CustomerDomainMailboxRel.objects.filter(customer_id=user_id, content_type=domain_ctype, object_id=send_domain_id).exists():
            bulk_lists.append(
                CustomerDomainMailboxRel(customer_id=user_id, content_type=domain_ctype, object_id=send_domain_id)
            )
        for box_obj in  mailbox_lists:
            box_id = box_obj.id
            if not CustomerDomainMailboxRel.objects.filter(customer_id=user_id, content_type=box_ctype, object_id=box_id).exists():
                bulk_lists.append(
                    CustomerDomainMailboxRel(customer_id=user_id, content_type=box_ctype, object_id=box_id)
                )
        if bulk_lists:
            CustomerDomainMailboxRel.objects.bulk_create(bulk_lists)

        messages.add_message(request, messages.SUCCESS, _(u'共享发件人成功'))
        return HttpResponseRedirect(reverse('sub_account'))
    # 获取域名
    domain_list = CustomerMailbox.objects.filter(
        customer=request.user, disabled='0').values_list('domain', flat=True).distinct()
    domain_objs = CustomerDomain.objects.filter(status='Y', customer=request.user, domain__in=list(domain_list))
    return render(request, template_name='setting/sub_account_share.html', context={
        'user_id': user_id,
        'user_obj': obj,
        'domain_objs': domain_objs,
    })

# 共享发件人 ajax
@login_required
def sub_account_share_ajax(request):
    user_id = request.GET.get('user_id', '')
    child_id = request.GET.get('child_id', '')
    domain_id = request.GET.get('domain_id', '')
    msg = 'N'
    info = ''
    share_info = ''
    if user_id and domain_id and child_id:
        obj = CustomerDomain.objects.filter(id=domain_id, customer_id=user_id).first()
        if obj:
            ctype = CustomerDomainMailboxRel.objects.get_content_type('mailbox')
            box_ids = CustomerDomainMailboxRel.objects.filter(customer_id=child_id, content_type=ctype).values_list('object_id', flat=True)
            share_box = CustomerMailbox.objects.filter(customer_id=user_id, domain=obj.domain, id__in=box_ids)
            share_index = 1
            for share_obj in share_box:
                share_info += u"""
                <tr class="" id="id_subdel_{}">
                    <td>{}</td>
					   <td>{}</td>
					   <td><button type="button" class="btn btn-outline btn-xs btn-danger" onclick="deleteSubbox('{}',  'sub_del', '{}', '{}');" title="收回发件人"><i class="fa fa-times"></i></button></td>
                 </tr>
                """.format(share_obj.id, share_index, share_obj.mailbox, share_obj.id, share_obj.mailbox, child_id)
                share_index += 1

            lists = CustomerMailbox.objects.filter(customer_id=user_id, domain=obj.domain).exclude(id__in=box_ids)
            index = 1
            for box_obj in lists:
                info += u"""
                <tr class="">
                    <td><input name="mailbox_ids[]" value="{}" type="checkbox"></td>
                    <td>{}</td>
					   <td>{}</td>
                 </tr>
                """.format(box_obj.id, index, box_obj.mailbox)
                index += 1
            msg = 'Y'
    return HttpResponse(json.dumps({'msg': msg, 'info': info, 'share_info': share_info,}), content_type="application/json")

@login_required
def sub_account_share_del_ajax(request):
    user_id = request.user.id
    delid = request.POST.get('delid', '')
    action = request.POST.get('action', '')
    mailbox = request.POST.get('mailbox', '')
    child_id = request.POST.get('child_id', '')
    if delid and action and mailbox and child_id:
        box_obj = CustomerMailbox.objects.get(customer_id=user_id, pk=delid)
        # count1 = CustomerMailbox.objects.filter(customer_id=user_id, domain=box_obj.domain).count()
        ctype = CustomerDomainMailboxRel.objects.get_content_type('mailbox')
        CustomerDomainMailboxRel.objects.filter(customer_id=child_id, content_type=ctype, object_id=delid).delete()
        # count2 = CustomerDomainMailboxRel.objects.filter(customer_id=child_id, content_type=ctype).count()
        info = u"""<tr class=""><td><input name="mailbox_ids[]" value="{}" type="checkbox"></td>
        <td>{}</td><td>{}</td></tr>""".format(box_obj.id, 'null', box_obj.mailbox)
        return HttpResponse(json.dumps({'info': info}), content_type="application/json")
    return HttpResponse(json.dumps({'info': ''}), content_type="application/json")

# 设置客户客服
def sub_account_setcus(request, user_id):
    obj = get_customer_child_obj(request, user_id)
    if request.method == "POST":
        data = request.POST
        fullname = data.get('fullname', None)
        mobile = data.get('mobile', None)
        im = data.get('im', None)

        subM, _created = SubAccoutManager.objects.get_or_create(customer_id=user_id)
        subM.fullname=fullname
        subM.mobile=mobile
        subM.im=im
        subM.save()
        msg = _(u'设置客服成功')
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(reverse('sub_account'))
    return render(request, template_name='setting/sub_account_setcus.html', context={
        'user_id': user_id,
        'user_obj': obj,
    })

# 修改群发量
@login_required
def sub_account_modify(request, user_id):
    obj = get_customer_child_obj(request, user_id)
    sub_service_obj = obj.service()
    if request.method == "POST":
        if sub_service_obj.is_share_flag == '2':
            service_obj = request.user.service()
            qty_count = int(request.POST.get('qty_count', '0'))
            if qty_count >= int(service_obj.qty_count):
                messages.add_message(request, messages.ERROR, _(u'分配的群发量已大于等于剩余群发量，分配群发量失败！'))
                return HttpResponseRedirect(reverse('sub_account'))

            service_obj.qty_count = F('qty_count') - qty_count
            service_obj.qty_valid = F('qty_valid') - qty_count
            # service_obj.qty_buytotal = F('qty_buytotal') - qty_count
            service_obj.save()

            sub_service_obj.qty_count = F('qty_count') + qty_count
            sub_service_obj.qty_valid = F('qty_valid') + qty_count
            # sub_service_obj.qty_buytotal = F('qty_buytotal') + qty_count
            # 服务状态改变
            if sub_service_obj.disabled == "1":
                sub_service_obj.disabled = '0'
            sub_service_obj.save()

            client_ip = get_client_ip(request)
            CoreLogList = [
                CoreLog(
                    user=request.user, user_type='users', target=request.user,
                    target_name=u'{0} - {0}'.format(request.user.username),
                    action='recharge_subuser', ip=client_ip, desc=u'-{}（分配群发量给子账户：{}）'.format(qty_count, obj.username)
                ),
                CoreLog(
                    user=request.user, user_type='users', target=obj,
                    target_name=u'{0} - {0}'.format(request.user.username),
                    action='recharge_subuser', ip=client_ip, desc=u'+{}（分配群发量）'.format(qty_count)
                ),
            ]
            CoreLog.objects.bulk_create(CoreLogList)
            msg = _(u'分配群发量成功')
        elif sub_service_obj.is_share_flag in ('3', '4'):
            share_type = request.POST.get('share_type', '')
            if share_type == '1': # 全部共享
                limit_qty = 0
                is_share_flag = '4'
            else:
                is_share_flag = '3'
                limit_qty  = int(request.POST.get('limit_qty', '0'))
            sub_service_obj.is_share_flag = is_share_flag
            sub_service_obj.limit_qty = limit_qty
            # 服务状态改变
            if sub_service_obj.disabled == "1":
                sub_service_obj.disabled = '0'
            sub_service_obj.save()
            msg = _(u'共享群发量成功')
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(reverse('sub_account'))
    return render(request, template_name='setting/sub_account_modify.html', context={
        'user_id': user_id,
        'user_obj': obj,
        'sub_service_obj': sub_service_obj,
    })


# 收回群发量
@login_required
def sub_account_reback(request, user_id):
    obj = get_customer_child_obj(request, user_id)
    sub_service_obj = obj.service()
    if request.method == "POST":
        if sub_service_obj.is_share_flag == '2':
            service_obj = request.user.service()
            share_type = request.POST.get('share_type', '')
            qty_count = sub_service_obj.qty_count
            if qty_count<=0:
                messages.add_message(request, messages.ERROR, _(u'收回群发量失败，子账户已经没有群发量'))
                return HttpResponseRedirect(reverse('sub_account'))

            if share_type == '1': # 全部共享
                limit_qty = qty_count
            else:
                limit_qty  = int(request.POST.get('limit_qty', '0'))
                if limit_qty<=0:
                    limit_qty=0
                if limit_qty>qty_count:
                    limit_qty=qty_count
            if limit_qty<=0:
                messages.add_message(request, messages.ERROR, _(u'收回群发量失败，群发量不能填写小于等于0'))
                return HttpResponseRedirect(reverse('sub_account'))

            service_obj.qty_count = F('qty_count') + limit_qty
            service_obj.qty_valid = F('qty_valid') + limit_qty
            # 服务状态改变
            if service_obj.disabled == "1":
                service_obj.disabled = '0'
            service_obj.save()

            sub_service_obj.qty_count = F('qty_count') - limit_qty
            sub_service_obj.qty_valid = F('qty_valid') - limit_qty
            sub_service_obj.save()

            client_ip = get_client_ip(request)
            CoreLogList = [
                CoreLog(
                    user=request.user, user_type='users', target=request.user,
                    target_name=u'{0} - {0}'.format(request.user.username),
                    action='recharge_subuser', ip=client_ip, desc=u'+{}（母账户收回子账户（{}）群发量）'.format(limit_qty, obj.username)
                ),
                CoreLog(
                    user=request.user, user_type='users', target=obj,
                    target_name=u'{0} - {0}'.format(request.user.username),
                    action='recharge_subuser', ip=client_ip, desc=u'-{}（子账户（{}）被母账户收回群发量）'.format(limit_qty, obj.username)
                ),
            ]
            CoreLog.objects.bulk_create(CoreLogList)
            messages.add_message(request, messages.SUCCESS, (u'收回群发量成功'))
        return HttpResponseRedirect(reverse('sub_account'))
    return render(request, template_name='setting/sub_account_reback.html', context={
        'user_id': user_id,
        'user_obj': obj,
        'sub_service_obj': sub_service_obj,
    })

# 一键登录子账户
@login_required
def sub_account_login(request):
    from django.contrib.auth.models import update_last_login
    from django.contrib.auth.views import logout, auth_login
    from django.contrib.auth import authenticate
    from django.contrib.auth.signals import user_logged_in

    parent_user_id = request.user.id
    client_ip = get_client_ip(request)
    agent = request.META.get('HTTP_USER_AGENT', None)
    ip_search = IpSearch()
    ip_info = ip_search.Find(client_ip)
    area, title = split_ip_to_area_title(ip_info)
    customer_id = request.POST.get('subloging_customer_id', '')
    auth = request.POST.get('subloging_auth', '')
    obj = get_customer_child_obj(request, customer_id)

    if auth == hashlib.md5('%s-%s' % (settings.WEB_API_AUTH_KEY, datetime.datetime.now().strftime("%Y%m%d"))).hexdigest():
        logout(request)
        CoreLog.objects.create(
            user_id=parent_user_id, user_type='users', target_id=customer_id,
            target_name=u'{0} - {0}'.format(obj.username), action='user_login',
            ip=client_ip, desc=u'登录IP：{}<br>登录地区：{}<br>浏览器信息：{}'.format(client_ip, title, agent),
        )
        user = authenticate(username=obj.username, password='', t_password=obj.password)
        user_logged_in.disconnect(update_last_login)
        auth_login(request, user)
        user_logged_in.connect(update_last_login)
        return HttpResponseRedirect(reverse('home'))
    raise Http404
