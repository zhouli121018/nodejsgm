# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import json
import time
from socket   import error as socket_error

from django.shortcuts import render
from django.contrib import messages
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.db.transaction import atomic
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, get_list_or_404

from app.core.models import CoreTrustIP, CoreAlias, CoreBlacklist, CoreWhitelist, DomainAttr, Domain
from app.setting.models import ExtCfilterRuleNew, AccountTransfer, IMAPMoving, PostTransfer
from app.setting.forms import SystemSetForm, CoreAliasForm, ExtCfilterRuleNewForm, \
                                ExtCfilterConfigForm, SmtpSetForm, AccountTransferForm, \
                                IMAPMovingForm, IMAPMovingImportForm, PostTransferForm, \
                                MailTransferSenderForm
from lib import validators
from lib.tools import create_task_trigger, add_task_to_queue, clear_redis_cache
from lib.licence import licence_required
import constants

#########################################
# 设置
@licence_required
def systemSet(request):
    form = SystemSetForm()
    if request.method == "POST":
        form = SystemSetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'修改设置成功')
            return HttpResponseRedirect(reverse('system_set'))
    return render(request, "setting/sysset.html", context={
        "form": form,
    })


#########################################
# 信任IP
@licence_required
def trustip_set(request):
    if request.method == "POST":
        id = request.POST.get('id', "")
        ip = request.POST.get('ip', "").strip()
        status = request.POST.get('status', "")
        if status == "delete":
            obj = CoreTrustIP.objects.filter(pk=id).first()
            obj.delete()
            messages.add_message(request, messages.SUCCESS, u'删除成功')
        if status == "active":
            obj = CoreTrustIP.objects.filter(pk=id).first()
            obj.disabled=-1
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'启用成功')
        if status == "disabled":
            obj = CoreTrustIP.objects.filter(pk=id).first()
            obj.disabled=1
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'禁用成功')
        if status == "add":
            if not validators.check_ipaddr(ip):
                messages.add_message(request, messages.ERROR, u'不合法的IP或IP段: {}'.format(ip))
                return HttpResponseRedirect(reverse('trustip_set'))
            obj = CoreTrustIP.objects.filter(ip=ip).first()
            if obj:
                messages.add_message(request, messages.ERROR, u'重复添加，添加失败')
            else:
                CoreTrustIP.objects.create(ip=ip)
                messages.add_message(request, messages.SUCCESS, u'添加成功')
        return HttpResponseRedirect(reverse('trustip_set'))

    clear_redis_cache()
    return render(request, "setting/trustip_set.html", context={
    })

@licence_required
def ajax_trustip_set(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'ip', 'disabled']
    lists = CoreTrustIP.objects.all()
    if search:
        lists = lists.filter(ip__icontains=search)

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
        start_num = int(data.get('start', '0'))
        page = start_num / length + 1
    except ValueError:
        start_num = 0
        page = 1

    count = lists.count()
    if start_num >= count:
        page = 1
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page-1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'setting/ajax_trustip_set.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")


#########################################
def getBlack_or_Whitelist(request, model, ltype):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'type', 'email', 'add_time', 'disabled']
    lists = model.objects.filter(type=ltype)
    if search:
        lists = lists.filter(email__icontains=search)

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
        start_num = int(data.get('start', '0'))
        page = start_num / length + 1
    except ValueError:
        start_num = 0
        page = 1

    count = lists.count()
    if start_num >= count:
        page = 1
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)
    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page-1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'setting/ajax_black_whitelist.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")

def black_white_post(request, model, ltype, reverse_name):
    id = request.POST.get('id', "")
    email = request.POST.get('email', "")
    status = request.POST.get('status', "")
    if status == "delete":
        obj = model.objects.filter(pk=id, type=ltype).first()
        obj.delete()
        messages.add_message(request, messages.SUCCESS, u'删除成功')
    if status == "active":
        obj = model.objects.filter(pk=id, type=ltype).first()
        obj.disabled=-1
        obj.save()
        messages.add_message(request, messages.SUCCESS, u'启用成功')
    if status == "disabled":
        obj = model.objects.filter(pk=id, type=ltype).first()
        obj.disabled=1
        obj.save()
        messages.add_message(request, messages.SUCCESS, u'禁用成功')
    if status == "add":
        if not "*" in email:
            if not validators.check_email_ordomain(email):
                messages.add_message(request, messages.ERROR, u'不合法的邮箱或域名: {}'.format(email))
                return HttpResponseRedirect(reverse(reverse_name))

        obj = model.objects.filter(email=email, type=ltype).first()
        if obj:
            messages.add_message(request, messages.ERROR, u'重复添加，添加失败')
        else:
            model.objects.create(operator='sys', type=ltype, email=email, add_time=int(time.time()))
            messages.add_message(request, messages.SUCCESS, u'添加成功')
    clear_redis_cache()
    return HttpResponseRedirect(reverse(reverse_name))

# 发件人黑名单
@licence_required
def blacklist(request):
    if request.method == "POST":
        return black_white_post(request, CoreBlacklist, "send", "blacklist_set")
    return render(request, "setting/black_whitelist.html", context={
        "model": "black",
        "model_name": u"发件人黑名单",
    })

@licence_required
def ajax_blacklist(request):
    return getBlack_or_Whitelist(request, CoreBlacklist, 'send')

# 发件人白名单
@licence_required
def whitelist(request):
    if request.method == "POST":
        return black_white_post(request, CoreWhitelist, "send", "whitelist_set")
    return render(request, "setting/black_whitelist.html", context={
        "model": "white",
        "model_name": u"发件人白名单",
    })

@licence_required
def ajax_whitelist(request):
    return getBlack_or_Whitelist(request, CoreWhitelist, 'send')

# 收件人白名单
@licence_required
def whitelist_rcp(request):
    if request.method == "POST":
        return black_white_post(request, CoreWhitelist, "recv", "whitelist_rcp_set")
    return render(request, "setting/whitelist.html", context={
        "model": "white_rcp",
        "model_name": u"收件人白名单",
    })

@licence_required
def ajax_whitelist_rcp(request):
    return getBlack_or_Whitelist(request, CoreWhitelist, 'recv')

#########################################
# 邮件域别名
@licence_required
def domain_alias(request):
    if request.method == "POST":
        id = request.POST.get('id', "")
        status = request.POST.get('status', "")
        if status == "delete":
            obj = CoreAlias.objects.filter(pk=id).first()
            obj.delete()
            messages.add_message(request, messages.SUCCESS, u'删除成功')
        return HttpResponseRedirect(reverse('domain_alias_set'))
    return render(request, "setting/domain_alias.html", context={
    })

# 邮件域别名
@licence_required
def domain_alias_add(request):
    form = CoreAliasForm()
    if request.method == "POST":
        form = CoreAliasForm(post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'添加成功')
            return HttpResponseRedirect(reverse('domain_alias_set'))
    return render(request, "setting/domain_alias_add.html", context={
        "form": form,
    })

@licence_required
def domain_alias_modify(request, alias_id):
    obj = CoreAlias.objects.get(id=alias_id)
    form = CoreAliasForm(instance=obj)
    if request.method == "POST":
        form = CoreAliasForm(instance=obj, post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'修改成功')
            return HttpResponseRedirect(reverse('domain_alias_set'))
    return render(request, "setting/domain_alias_add.html", context={
        "form": form,
    })

# 邮件域别名
@licence_required
def ajax_domain_alias(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'source', 'target', 'disabled']
    lists = CoreAlias.objects.filter(type="domain")
    if search:
        lists = lists.filter( Q(source__icontains=search) | Q(target__icontains=search) )

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
        start_num = int(data.get('start', '0'))
        page = start_num / length + 1
    except ValueError:
        start_num = 0
        page = 1

    count = lists.count()
    if start_num >= count:
        page = 1
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)
    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page-1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'setting/ajax_domain_alias.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")


#########################################
# 邮件过滤
@licence_required
def cfilter(request):
    if request.method == "POST":
        id = request.POST.get('id', "")
        status = request.POST.get('status', "")
        if status == "delete":
            obj = ExtCfilterRuleNew.objects.filter(pk=id).first()
            obj.delete()
            messages.add_message(request, messages.SUCCESS, u'删除成功')
        if status == "active":
            obj = ExtCfilterRuleNew.objects.filter(pk=id).first()
            obj.disabled=-1
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'启用成功')
        if status == "disabled":
            obj = ExtCfilterRuleNew.objects.filter(pk=id).first()
            obj.disabled=1
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'禁用成功')
        return HttpResponseRedirect(reverse('cfilter_set'))

    return render(request, "setting/cfilter.html", context={
    })

#目前没用了，改在webmail系统后台设置开关。 2018-01-19 lpx
@licence_required
def cfilter_config(request):
    obj = DomainAttr.getAttrObj(domain_id=0, type="system", item='sw_use_cfilter_new')
    form = ExtCfilterConfigForm(instance=obj)
    if request.method == "POST":
        form = ExtCfilterConfigForm(post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'修改开关成功')
            return HttpResponseRedirect(reverse("cfilter_config"))
    return render(request, "setting/cfilter_config.html", context={
        "form": form,
    })

@licence_required
def cfilter_add(request):
    form = ExtCfilterRuleNewForm()
    if request.method == "POST":
        form = ExtCfilterRuleNewForm(post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'添加成功')
            return HttpResponseRedirect(reverse('cfilter_set'))
    return render(request, "setting/cfilter_add.html", context={
        "form": form,
    })

@licence_required
def cfilter_modify(request, rule_id):
    obj = ExtCfilterRuleNew.objects.get(id=rule_id)
    form = ExtCfilterRuleNewForm(instance=obj)
    if request.method == "POST":
        form = ExtCfilterRuleNewForm(post=request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'修改成功')
            return HttpResponseRedirect(reverse('cfilter_set'))
    return render(request, "setting/cfilter_add.html", context={
        "form": form,
    })

@licence_required
def ajax_cfilter(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'name', 'type', 'logic', 'id', 'id', 'sequence', 'disabled']
    # lists = ExtCfilterRuleNew.objects.all()
    lists = ExtCfilterRuleNew.objects.filter(mailbox_id=0)
    if search:
        lists = lists.filter( name__icontains=search )

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
        start_num = int(data.get('start', '0'))
        page = start_num / length + 1
    except ValueError:
        start_num = 0
        page = 1

    count = lists.count()
    if start_num >= count:
        page = 1
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)
    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page-1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'setting/ajax_cfilter.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")

def smtp_verify_account(account):
    import smtplib

    if not account or "server" not in account or "account" not in account:
        return "FAIL", "缺少数据"
    status = "FAIL"
    msg = ""
    trans_server = account.get("server","")
    trans_account = account.get("account","")
    trans_password = account.get("password","")
    trans_ssl = account.get("ssl","")
    trans_auth = account.get("auth","")
    if not trans_ssl:
        trans_ssl = "-1"
    if not trans_auth:
        trans_auth = "1"
    try:
        #有些邮件服务器输入帐号名也能登录，我们应该要强制全名
        if not "@" in trans_account:
            status = "FAIL"
            msg = "不是合法邮箱帐号： %s"%trans_account
            return status,msg

        if ":" in trans_server:
            trans_server, port = trans_server.split(":")[:2]
        else:
            trans_server, port = trans_server, 25
        if trans_ssl == "1":
            smtpObj = smtplib.SMTP_SSL(host=trans_server,port=int(port),timeout=5)
        else:
            smtpObj = smtplib.SMTP(host=trans_server,port=int(port),timeout=5)

        status = "OK"
        if trans_auth == "1":
            msg = "服务器登录验证成功！"
            smtpObj.login( trans_account, trans_password )
    except smtplib.SMTPAuthenticationError,err:
        status = "FAIL"
        msg = "服务器验证失败： %s"%str(err)
    except Exception,err:
        status = "FAIL"
        msg = "服务器连接出错： %s"%str(err)
    return status, msg

@licence_required
def ajax_smtpcheck(request):
    def get_smtp_account(data):
        result = {}
        field_list = {
        "action_value_smtptransfer_server"  :   "server",
        "action_value_smtptransfer_account" :   "account",
        "action_value_smtptransfer_password":   "password",
        "action_value_smtptransfer_ssl"       :   "ssl",
        "action_value_smtptransfer_auth"     :    "auth",
        }
        for key,value in data.iteritems():
            for field, field_trans in field_list.items():
                if key.startswith(field):
                    rule_id = key[len(field):]
                    #前端写得很乱很复杂，有BUG，这里暂时先堵住。
                    if not rule_id.isdigit():
                        continue
                    if not value.strip():
                        continue
                    acct_field = key[:len(field)]

                    result.setdefault(rule_id,{})
                    result[rule_id][field_trans] = value
        result2 = {}
        for rule_id, data in result.items():
            if not "server" in data or not data["server"]:
                continue
            result2[rule_id] = data
        return result2
    #end def

    import smtplib
    data = request.POST.get("data","")
    data = json.loads( data )
    account = {}
    if data:
        account = get_smtp_account(data)

    if not account:
        rs = {
            "status"   :   "OK",
            "msg"     :   "",
        }
        return HttpResponse(json.dumps(rs), content_type="application/json")

    status = "FAIL"
    msg = ""
    for rule_id,data in account.iteritems():
        status, msg = smtp_verify_account(data)
        if status != "OK":
            break
    rs = {
        "status"   :   status,
        "msg"     :   msg,
    }
    return HttpResponse(json.dumps(rs), content_type="application/json")

# 查看 条件或动作
@licence_required
def cfilter_view(request, rule_id):
    status = request.GET.get('status', '')
    obj = ExtCfilterRuleNew.objects.get(id=rule_id)
    if status == "option":
        lists = obj.getOptions()
    elif status == "action":
        lists= obj.getActions()
    else:
        lists=[]
    return render(request, "setting/cfilter_view.html", context={
        "obj": obj,
        "status": status,
        "lists": lists,
    })

#########################################
# Dkim
@licence_required
def dkim(request):
    domain_lists = Domain.objects.all()
    attrs = DomainAttr.objects.filter(item='dkim_privatekey', type='system')
    return render(request, "setting/dkim.html", context={
        'lists': domain_lists,
        'attrs': attrs,
    })

@licence_required
def dkim_modify(request, domain_id):
    if domain_id == '0':
        domain = u'所有域名'
    else:
        try:
            domain = Domain.objects.get(id=domain_id)
        except Domain.DoesNotExist:
            raise Http404

    from lib.tools import generate_rsa
    if request.method == "POST":
        action = request.POST.get('action', '')
        # 自动设置
        if action == 'auto_set':
            private_key, publick_key = generate_rsa()
            attr, _ = DomainAttr.objects.get_or_create(item='dkim_privatekey', type='system', domain_id=domain_id)
            attr.value = private_key
            attr.save()
            messages.add_message(request, messages.SUCCESS, u'生成密钥成功')
        # 文件导入
        elif action == 'import_file':
            f = request.FILES.get('file', '')
            if not f:
                messages.add_message(request, messages.ERROR, u'请选择密钥文件导入')
            else:
                private_key = f.read()
                try:
                    private_key, public_key = generate_rsa(pkey=private_key)
                except:
                    messages.add_message(request, messages.ERROR, u'您导入的密钥格式不正确，请重新生成!')
                else:
                    attr, _ = DomainAttr.objects.get_or_create(item='dkim_privatekey', type='system', domain_id=domain_id)
                    attr.value = private_key
                    attr.save()
                    messages.add_message(request, messages.SUCCESS, u'导入密钥成功')
        elif action == 'delete':
            DomainAttr.objects.filter(item='dkim_privatekey', type='system', domain_id=domain_id).delete()
            messages.add_message(request, messages.SUCCESS, u'清除成功')
        elif action == 'export':
            try:
                attr = DomainAttr.objects.get(item='dkim_privatekey', type='system', domain_id=domain_id)
            except DomainAttr.DoesNotExist:
                raise Http404
            response = HttpResponse(content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename=dkim.key'
            response.write(attr.value)
            return response
        return HttpResponseRedirect(reverse('dkim_modify', args=(domain_id,)))

    attrs = DomainAttr.objects.filter(item='dkim_privatekey', type='system', domain_id=domain_id)
    attr = attrs.first() if attrs else None
    if attr:
        try:
            _, public_key = generate_rsa(pkey=attr.value)
        except:
            messages.add_message(request, messages.ERROR, u'您的密钥格式不正确，请清除后重新生成!')
        else:
            attr.public_key = 'k=rsa;p={}'.format(''.join(public_key.split('\n')[1:-1]).replace('\n', ''))
    return render(request, "setting/dkim_modify.html", context={
        'domain': domain,
        'attr': attr,
    })


#########################################
# smtp 重试
@licence_required
def smtp(request):
    form = SmtpSetForm(initial=DomainAttr.smtpSetValuetoDict())

    if request.method == "POST":
        form = SmtpSetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'修改设置成功!')
            return redirect('smtp_set')
    return render(request, template_name="setting/smtp.html", context={
        "form": form,
    })


@licence_required
def accountTransfer(request):
    form = AccountTransferForm()
    if request.method == "POST":
        id = request.POST.get('id', "")
        status = request.POST.get('status', "")
        if status == "delete":
            obj = AccountTransfer.objects.filter(pk=id).first()
            if obj:
                obj.delete()
                messages.add_message(request, messages.SUCCESS, u'删除成功')
    statustypes = dict(constants.ACCOUNT_TRANSFER_STATUS)
    return render(request, "setting/account_transfer.html", context={
        "form"          :   form,
        "statustypes"    :   statustypes,
    })

@licence_required
def accountTransferAdd(request):
    form = AccountTransferForm()
    if request.method == "POST":
        form = AccountTransferForm(post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'添加数据成功')
            return HttpResponseRedirect(reverse('account_transfer'))

    return render(request, "setting/account_transfer_set.html", context={
        "form"          :   form,
    })

@licence_required
def accountTransferModify(request, trans_id):
    obj = AccountTransfer.objects.filter(id=trans_id).first()
    if not obj:
        messages.add_message(request, messages.SUCCESS, u'试图修改的数据不存在')
        return HttpResponseRedirect(reverse('account_transfer'))

    form = AccountTransferForm(instance=obj)
    if request.method == "POST":
        form = AccountTransferForm(instance=obj, post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'修改数据成功')
            return HttpResponseRedirect(reverse('account_transfer'))

    return render(request, "setting/account_transfer_set.html", context={
        "form"          :   form,
    })

@licence_required
def ajax_accountTransfer(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'mailbox_id', 'mailbox', 'mailbox_to', 'mode', 'succ_del', 'status', 'last_update', 'desc_msg', 'disabled']

    lists = AccountTransfer.objects.all()
    if search:
        lists = lists.filter( Q(mailbox__icontains=search) | Q(mailbox_to__icontains=search) )

    if lists and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            lists = lists.order_by('-%s' % colums[int(order_column)])
        else:
            lists = lists.order_by('%s' % colums[int(order_column)])
    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        start_num = int(data.get('start', '0'))
        page = start_num / length + 1
    except ValueError:
        start_num = 0
        page = 1

    count = len(lists)
    if start_num >= count:
        page = 1
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)
    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page-1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'setting/ajax_account_transfer.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1

    return HttpResponse(json.dumps(rs), content_type="application/json")

@licence_required
def imapMoving(request):
    form = IMAPMovingForm()
    if request.method == "POST":
        id = request.POST.get('id', "")
        status = request.POST.get('status', "")
        if status == "delete":
            obj = IMAPMoving.objects.filter(pk=id).first()
            if obj:
                obj.delete()
                messages.add_message(request, messages.SUCCESS, u'删除成功')
    return render(request, "setting/mail_moving.html", context={
        "form"          :   form,
    })

@licence_required
def imapMovingAdd(request):
    form = IMAPMovingForm()
    if request.method == "POST":
        form = IMAPMovingForm(post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'添加数据成功')
            return HttpResponseRedirect(reverse('mail_moving'))

    return render(request, "setting/mail_moving_set.html", context={
        "form"          :   form,
    })

@licence_required
def imapMovingImport(request):
    form = IMAPMovingImportForm()
    if request.method == "POST":
        form = IMAPMovingImportForm(post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'导入数据成功')
    return render(request, "setting/mail_moving_import.html", context={
        "form"          :   form,
    })

@licence_required
def imapMovingModify(request, trans_id):
    obj = IMAPMoving.objects.filter(id=trans_id).first()
    if not obj:
        messages.add_message(request, messages.SUCCESS, u'试图修改的数据不存在')
        return HttpResponseRedirect(reverse('mail_moving'))

    form = IMAPMovingForm(instance=obj)
    if request.method == "POST":
        form = IMAPMovingForm(instance=obj, post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'修改数据成功')
            return HttpResponseRedirect(reverse('mail_moving'))

    return render(request, "setting/mail_moving_set.html", context={
        "form"          :   form,
    })

@licence_required
def ajax_imapMoving(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'mailbox', 'src_mailbox', 'src_server', 'ssl', 'status', 'desc_msg', 'last_update', 'disabled']

    lists = IMAPMoving.objects.all()
    if search:
        lists = lists.filter( Q(mailbox__icontains=search) | Q(src_mailbox__icontains=search) | Q(src_server__icontains=search) )

    if lists and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            lists = lists.order_by('-%s' % colums[int(order_column)])
        else:
            lists = lists.order_by('%s' % colums[int(order_column)])
    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        start_num = int(data.get('start', '0'))
        page = start_num / length + 1
    except ValueError:
        start_num = 0
        page = 1

    count = len(lists)
    if start_num >= count:
        page = 1
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)
    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page-1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'setting/ajax_mail_moving.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1

    return HttpResponse(json.dumps(rs), content_type="application/json")

@licence_required
def ajax_imapCheck(request):
    import imaplib

    server = request.POST.get("server","")
    port = int(request.POST.get("port",0))
    account = request.POST.get("account","")
    password = request.POST.get("password","")
    ssl = int(request.POST.get("ssl","-1"))

    status = "FAIL"
    msg = ""
    if not port:
        port = imaplib.IMAP4_SSL_PORT if ssl==1 else imaplib.IMAP4_PORT
    try :
        client = imaplib.IMAP4_SSL(server, port) if ssl==1 else imaplib.IMAP4(server, port)
        client.login(account, password)
        status = "OK"
        try:
            if not client.logout():
                client.shutdown()
        except:
            pass
    except Exception, err :
        msg = "连接服务器失败： %s"%str(err)

    rs = {
        "status"    :   status,
        "msg"      :   msg,
    }
    return HttpResponse(json.dumps(rs), content_type="application/json")

@licence_required
def ajax_imapRecv(request):
    imap_id = int(request.POST.get("id",0))

    status = "FAIL"
    msg = ""
    try :
        data = {
            "imap_id"  :  imap_id,
        }
        add_task_to_queue("imapmail",data)
        status = "OK"
        msg = ""
    except Exception, err :
        msg = "任务注册失败： %s"%str(err)

    rs = {
        "status"    :   status,
        "msg"      :   msg,
    }
    return HttpResponse(json.dumps(rs), content_type="application/json")

@licence_required
def imapMovingDisable(request):
    IMAPMoving.objects.all().update(disabled='1')
    messages.add_message(request, messages.SUCCESS, u'全部禁用成功')
    return HttpResponseRedirect(reverse('mail_moving'))

@licence_required
def imapMovingEnable(request):
    IMAPMoving.objects.all().update(disabled='-1')
    messages.add_message(request, messages.SUCCESS, u'全部启用成功')
    return HttpResponseRedirect(reverse('mail_moving'))

@licence_required
def imapMovingDelete(request):
    IMAPMoving.objects.all().delete()
    messages.add_message(request, messages.SUCCESS, u'全部删除成功')
    return HttpResponseRedirect(reverse('mail_moving'))

@licence_required
def mailTransfer(request):
    form = PostTransferForm()
    if request.method == "POST":
        id = request.POST.get('id', "")
        status = request.POST.get('status', "")
        if status == "delete":
            obj = PostTransfer.objects.filter(pk=id).first()
            if obj:
                obj.delete()
                messages.add_message(request, messages.SUCCESS, u'删除成功')
    return render(request, "setting/mail_transfer.html", context={
        "form"          :   form,
    })

@licence_required
def mailTransferSender(request):
    obj = DomainAttr.getAttrObj(domain_id=0, type="system", item='deliver_transfer_sender')
    form = MailTransferSenderForm(instance=obj)
    if request.method == "POST":
        form = MailTransferSenderForm(post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'添加数据成功')
            return HttpResponseRedirect(reverse('mail_transfer_sender'))

    return render(request, "setting/mail_transfer_sender.html", context={
        "form"          :   form,
    })

@licence_required
def postTransferAdd(request):
    form = PostTransferForm()
    if request.method == "POST":
        form = PostTransferForm(post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'添加数据成功')
            return HttpResponseRedirect(reverse('mail_transfer'))

    return render(request, "setting/include/mail_transfer_post_set.html", context={
        "form"          :   form,
    })

@licence_required
def postTransferModify(request, trans_id):
    obj = PostTransfer.objects.filter(id=trans_id).first()
    if not obj:
        messages.add_message(request, messages.SUCCESS, u'试图修改的数据不存在')
        return HttpResponseRedirect(reverse('mail_transfer'))

    form = PostTransferForm(instance=obj)
    if request.method == "POST":
        form = PostTransferForm(instance=obj, post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'修改数据成功')
            return HttpResponseRedirect(reverse('mail_transfer'))

    return render(request, "setting/include/mail_transfer_post_set.html", context={
        "form"          :   form,
    })

@licence_required
def ajax_postTransfer(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'mailbox', 'account', 'recipient', 'server', 'ssl', 'auth', 'fail_report', 'disabled']

    lists = PostTransfer.objects.all()
    if search:
        lists = lists.filter( Q(mailbox__icontains=search) | Q(account__icontains=search) | Q(recipient__icontains=search) | Q(server__icontains=search) )

    if lists and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            lists = lists.order_by('-%s' % colums[int(order_column)])
        else:
            lists = lists.order_by('%s' % colums[int(order_column)])
    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        start_num = int(data.get('start', '0'))
        page = start_num / length + 1
    except ValueError:
        start_num = 0
        page = 1

    count = len(lists)
    if start_num >= count:
        page = 1
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)
    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page-1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'setting/ajax_post_transfer.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1

    return HttpResponse(json.dumps(rs), content_type="application/json")

@licence_required
def ajax_smtpCheck(request):
    status, msg = smtp_verify_account(request.POST)
    rs = {
        "status"    :   status,
        "msg"      :   msg,
    }
    return HttpResponse(json.dumps(rs), content_type="application/json")
