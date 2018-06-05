# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import re
import json
import pytz
import datetime
import subprocess
try:
    import cStringIO as StringIO
except:
    import StringIO

from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.contrib import messages
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from wsgiref.util import FileWrapper
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page
from django_redis import get_redis_connection
from django.db.models import Q

from app.core.models import CoreConfig, DomainAttr
from app.maintain.tools import getLogDesc, LogFormat, BackupFormat, generateRedisTaskID
from app.maintain.models import ExtSquesterMail
from app.maintain.choices import ISOLATE_STATUS_R
from app.maintain.forms import BackupSetForm, MailSearchForm
from app.maintain import sslopts,choices
from lib import validators
from lib.tools import create_task_trigger
from lib.licence import licence_required

#########################################
# SSL加密
@licence_required
def sslView(request):
    # ssl开关
    sslobj = CoreConfig.getFuctionObj('ssl')
    # 私钥数据
    keyobj = DomainAttr.getAttrObj(item="ssl_privatekey")
    value = keyobj.value or None
    # 签名请求数据
    sigobj = DomainAttr.getAttrObj(item="ssl_signrequest")
    # 证书
    certobj = DomainAttr.getAttrObj(item="ssl_certificate")
    if request.method == "POST":
        status = request.POST.get("status", "")
        if status == "generate":
            # 系统生成私钥
            if value:
                messages.add_message(request, messages.ERROR, u'私钥已存在，设置私钥失败!')
                return HttpResponseRedirect(reverse("ssl_maintain"))
            else:
                try:
                    privkey = sslopts.genPrivKey()
                    keyobj.value = privkey
                    keyobj.save()
                    messages.add_message(request, messages.SUCCESS, u'生成私钥成功')
                    return HttpResponseRedirect(reverse("ssl_maintain"))
                except:
                    messages.add_message(request, messages.ERROR, u'生成私钥失败,请重新生成')
                    return HttpResponseRedirect(reverse("ssl_maintain"))

        if status == "clear":
            # 清除私钥
            keyobj.value = ""
            keyobj.save()
            # 清空证书签名请求
            DomainAttr.emptyAttrObjValue(item="ssl_signrequest")
            # 清除证书
            DomainAttr.emptyAttrObjValue(item="ssl_certificate")
            messages.add_message(request, messages.SUCCESS, u'清除私钥成功')
            return HttpResponseRedirect(reverse("ssl_maintain"))

        if status == "export-signature":
            # 导出签名请求
            sigvalue = sigobj.value or None
            if not sigvalue:
                messages.add_message(request, messages.ERROR, u'签名请求 不存在')
                return HttpResponseRedirect(reverse("ssl_maintain"))
            else:
                try:
                    wrapper = FileWrapper(StringIO.StringIO(sigvalue))
                    response = HttpResponse(wrapper, content_type='application/octet-stream')
                    response['Content-Length'] = len(value)
                    response['Content-Disposition'] = 'attachment; filename=%s' % "ssl_signrequest.csr"
                    return response
                except:
                    messages.add_message(request, messages.ERROR, u'导出签名请求失败，请重新导出')
                    return HttpResponseRedirect(reverse("ssl_maintain"))

        if status == "clear-signature":
            # 清除签名请求
            DomainAttr.emptyAttrObjValue(item="ssl_signrequest")
            messages.add_message(request, messages.SUCCESS, u'清除签名请求成功')
            return HttpResponseRedirect(reverse("ssl_maintain"))

        if status == "cert-export":
            # 导出证书
            certvalue = certobj.value or None
            if not certvalue:
                messages.add_message(request, messages.ERROR, u'证书 不存在')
                return HttpResponseRedirect(reverse("ssl_maintain"))
            else:
                try:
                    wrapper = FileWrapper(StringIO.StringIO(certvalue))
                    response = HttpResponse(wrapper, content_type='application/octet-stream')
                    response['Content-Length'] = len(value)
                    response['Content-Disposition'] = 'attachment; filename=%s' % "ssl_certificate.crt"
                    return response
                except:
                    messages.add_message(request, messages.ERROR, u'导出证书失败，请重新导出')
                    return HttpResponseRedirect(reverse("ssl_maintain"))

        if status == "cert-clear":
            # 清除证书
            DomainAttr.emptyAttrObjValue(item="ssl_certificate")
            messages.add_message(request, messages.SUCCESS, u'清除证书成功成功')
            return HttpResponseRedirect(reverse("ssl_maintain"))

    is_verify = False
    signature = DomainAttr.getSignatureCache()
    if sigobj.value:
        is_verify, signature2 = sslopts.parseSignature(sigobj.value)
        if is_verify: signature = signature2

    is_ca = False
    cert_subject, sert_issuer=None, None
    if certobj.value:
        is_ca = True
        cert_subject, sert_issuer = sslopts.parseCert(certobj.value)

    return render(request, "maintain/ssl.html", context={
        "sslobj": sslobj,
        "keyValue": sslopts.getPrivateKeySize(bytes(value)) if value else None,
        "is_verify": is_verify,
        "signature": signature,

        "is_ca": is_ca,
        "cert_subject": cert_subject,
        "sert_issuer": sert_issuer,
    })


@licence_required
def sslEnableView(request):
    if request.method == "POST":
        ssl = request.POST.get("ssl", "-1")
        if ssl in ("1", "-1"):
            obj = CoreConfig.getFuctionObj('ssl')
            obj.enabled=ssl
            obj.save()

            redis = get_redis_connection()
            redis.rpush("task_queue:apply_setting", "ssl")
            messages.add_message(request, messages.SUCCESS, u'应用设置成功')
        else:
            messages.add_message(request, messages.ERROR, u'未知错误，操作失败!')
        return HttpResponseRedirect(reverse("ssl_maintain"))
    raise Http404


# 私钥导入导出
@licence_required
def sslPrivateView(request):
    if request.method == "POST":
        status = request.POST.get("sslkey_status", "")
        obj = DomainAttr.getAttrObj(item="ssl_privatekey")
        value = obj.value
        if status == "import":
            keywd = request.POST.get("sslkey_passwd_import", "").strip()
            keywd = keywd or None
            if value:
                messages.add_message(request, messages.ERROR, u'私钥已存在，设置私钥失败!')
                return HttpResponseRedirect(reverse("ssl_maintain"))
            else:
                try:
                    fileobj = request.FILES['sslkeyfile']
                    privkey = fileobj.read()
                    privkey = sslopts.importPrivKey(privkey, passwd=keywd)
                    obj.value = privkey
                    obj.save()
                    messages.add_message(request, messages.SUCCESS, u'导入私钥成功')
                    return HttpResponseRedirect(reverse("ssl_maintain"))
                except BaseException as e:
                    messages.add_message(request, messages.ERROR, u'导入私钥失败（保护密码错误、非密钥文件等）, 请重新导入！')
                    return HttpResponseRedirect(reverse("ssl_maintain"))
        if status == "export":
            keywd = request.POST.get("sslkey_passwd_export", "").strip()
            keywd = keywd or None
            if value:
                try:
                    privkey = sslopts.exportPrivKey(bytes(value), passwd=keywd)
                    wrapper = FileWrapper(StringIO.StringIO(privkey))
                    response = HttpResponse(wrapper, content_type='application/octet-stream')
                    response['Content-Length'] = sslopts.getPrivateKeySize(bytes(value))
                    response['Content-Disposition'] = 'attachment; filename=%s' % "ssl_private.key"
                    return response
                except BaseException as e:
                    messages.add_message(request, messages.ERROR, u'私钥不正确，请重新生成私钥导出!')
                    return HttpResponseRedirect(reverse("ssl_maintain"))
            else:
                messages.add_message(request, messages.ERROR, u'私钥不存在，导出失败!')
                return HttpResponseRedirect(reverse("ssl_maintain"))
        return HttpResponseRedirect(reverse("ssl_maintain"))
    raise Http404


# 生成签名请求
@licence_required
def sslSignatureView(request):
    if request.method == "POST":
        obj = DomainAttr.getAttrObj(item="ssl_signrequest")
        keyobj = DomainAttr.getAttrObj(item="ssl_privatekey")
        keyvalue = keyobj.value
        if obj.value:
            messages.add_message(request, messages.ERROR, u'证书签名请求已存在，生成证书签名请求失败!')
            return HttpResponseRedirect(reverse("ssl_maintain"))
        else:
            sig_domain = request.POST.get("sig_domain", "").strip()
            sig_organization = request.POST.get("sig_organization", "").strip()
            sig_depart = request.POST.get("sig_depart", "").strip()
            sig_province = request.POST.get("sig_province", "").strip()
            sig_locale = request.POST.get("sig_locale", "").strip()
            j = {}
            msg = []
            if not validators.check_domain(u"@{}".format(sig_domain)):
                msg.append(u"域名 填写错误")
            j.update(sig_domain=sig_domain)

            if not sig_organization:
                msg.append(u"单位/组织 不能为空")
            elif  not validators.check_English(sig_organization):
                msg.append(u"单位/组织 只能填写英文字符")
            j.update(sig_organization=sig_organization)

            if sig_depart and not validators.check_English(sig_depart):
                msg.append(u"部门 只能填写英文字符")
            j.update(sig_depart=sig_depart)

            if not sig_province:
                msg.append(u"省/市/自治区 不能为空")
            elif not validators.check_English(sig_province):
                msg.append(u"省/市/自治区 只能填写英文字符")
            j.update(sig_province=sig_province)

            if not sig_locale:
                msg.append(u"所在地 不能为空")
            elif not validators.check_English(sig_locale):
                msg.append(u"所在地 只能填写英文字符")
            j.update(sig_locale=sig_locale)

            DomainAttr.saveAttrObjValue(item="ssl_signrequest_cache", value=json.dumps(j))
            if not keyvalue:
                messages.add_message(request, messages.ERROR, u'私钥不存在，请先设置私钥!')
                return HttpResponseRedirect(reverse("ssl_maintain"))
            if msg:
                messages.add_message(request, messages.ERROR, u"，".join(msg))
                return HttpResponseRedirect(reverse("ssl_maintain"))
            else:
                signature = sslopts.genSignature(
                    privkey=bytes(keyvalue), sig_domain=sig_domain, sig_depart=sig_depart,
                    sig_organization=sig_organization, sig_province=sig_province, sig_locale=sig_locale)
                obj.value = signature
                obj.save()
                messages.add_message(request, messages.SUCCESS, u'生成证书签名请求成功')
                return HttpResponseRedirect(reverse("ssl_maintain"))

        return HttpResponseRedirect(reverse("ssl_maintain"))
    raise Http404


# 设置证书
def sslCertView(request):
    if request.method == "POST":
        try:
            keyobj = DomainAttr.getAttrObj(item="ssl_privatekey")
            certobj = DomainAttr.getAttrObj(item="ssl_certificate")
            privkey = keyobj.value
            if not privkey:
                messages.add_message(request, messages.ERROR, u'私钥不存在，请先生成或导入!')
                return HttpResponseRedirect(reverse("ssl_maintain"))
            fileobj = request.FILES['certfile']
            certificate = fileobj.read()
            T = sslopts.checkCert(bytes(privkey), bytes(certificate))
            if not T:
                messages.add_message(request, messages.ERROR, u'证书与私钥不匹配，无法导入！')
                return HttpResponseRedirect(reverse("ssl_maintain"))
            certobj.value = certificate
            certobj.save()
            messages.add_message(request, messages.SUCCESS, u'导入证书成功！')
            return HttpResponseRedirect(reverse("ssl_maintain"))
        except BaseException as e:
            messages.add_message(request, messages.ERROR, u'无法解析证书，请检测证书文件！')
            return HttpResponseRedirect(reverse("ssl_maintain"))
    raise Http404


#########################################
# 数据备份
@licence_required
def backupView(request):
    backuppath = CoreConfig.getInitBackupParam()["path"]
    if request.method == 'POST':
        auto_status = request.POST.get('auto_status',"")
        if auto_status:
            auto_status = "1" if auto_status=="1" else "-1"
            instance = CoreConfig.getFuctionObj("auto_backup")
            CoreConfig.saveFuction("auto_backup", auto_status, instance.param)
        else:
            name = request.POST.get('name')
            status = request.POST.get('status')
            redis = get_redis_connection()
            if redis.exists("task_trigger:backup"):
                messages.add_message(request, messages.ERROR, u'正在执行备份操作，操作失败!')
                return redirect('backup_maintain')
            if redis.exists("task_trigger:restore"):
                messages.add_message(request, messages.ERROR, u'正在执行数据恢复操作，操作失败!')
                return redirect('backup_maintain')

            if status == "backup":
                redis.set("task_trigger:backup", 1)
                messages.add_message(request, messages.SUCCESS, u'正在备份数据，请耐心等待!')
            if status == "delete":
                path = os.path.join(backuppath, name)
                if os.path.exists(path):
                    cmd = "sudo /usr/local/u-mail/app/exec/backup delete {}".format(name)
                    child = subprocess.Popen(cmd, shell=True)
                    # child.communicate()
                    messages.add_message(request, messages.SUCCESS, u'正在删除备份数据，请耐心等待!')
                else:
                    messages.add_message(request, messages.ERROR, u'备份数据文件不存在，操作失败!')
            if status == "restore":
                task_id = generateRedisTaskID()
                d = json.dumps({ "backup_name":name, })
                p = redis.pipeline()
                p.set("task_trigger:restore", 1)
                p.rpush("task_queue:restore", task_id)
                p.hset("task_data:restore", task_id, d)
                p.execute()
                messages.add_message(request, messages.SUCCESS, u'已提交数据恢复任务，请耐心等待数据恢复完成!')
        return redirect('backup_maintain')

    index = 0
    lists = []
    listsa = []
    if os.path.exists( backuppath ):
        listsa = os.listdir(backuppath)
    listsa.sort()
    for f in listsa:
        if f.startswith("umail_"):
            size = 0
            times=""
            names=[]
            path = os.path.join(backuppath, f)
            for ff in os.listdir(path):
                filepath = os.path.join(path, ff)
                if ff.startswith("database"):
                    names.append(u"数据库")
                if ff.startswith("licence"):
                    timestamp = os.path.getmtime(filepath)
                    dt = datetime.datetime.fromtimestamp( timestamp, pytz.timezone('Asia/Shanghai') )
                    times = dt.strftime("%Y:%m:%d %H:%M:%S")
                if os.path.isfile(filepath):
                    size += os.path.getsize( filepath )

            maildata = os.path.join(path, "maildata")
            if os.path.exists(maildata):
                names.append(u"邮件数据")
                for ff in os.listdir(maildata):
                    filepath = os.path.join(maildata, ff)
                    if os.path.isfile(filepath):
                        size += os.path.getsize( filepath )

            netdisk = os.path.join(path, "netdisk")
            if os.path.exists(netdisk):
                names.append(u"网盘数据")
                for ff in os.listdir(netdisk):
                    filepath = os.path.join(netdisk, ff)
                    if os.path.isfile(filepath):
                        size += os.path.getsize( filepath )
            if names:
                index += 1
                lists.append(
                    BackupFormat._make( [index, f, u"，".join(names), size, times] )
                )

    backupstatus=None
    redis = get_redis_connection()
    if redis.exists("task_trigger:restore"):
        backupstatus=u"数据恢复"
    if redis.exists("task_trigger:backup"):
        backupstatus=u"数据备份"

    auto_backup = int(CoreConfig.getFuctionEnabled("auto_backup"))
    return render(request, "maintain/backup.html", context={
        "lists": lists,
        "backupstatus": backupstatus,
        "auto_backup": auto_backup,
    })

@licence_required
def backupSetView(request):
    form = BackupSetForm(CoreConfig.getInitBackupParam())
    if request.method == "POST":
        form = BackupSetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'设置成功!')
            return redirect('backup_maintain')
    return render(request, "maintain/backupset.html", context={
        "form": form,
    })


#########################################
# 程序日志
@cache_page(60 * 5)
@licence_required
def logView(request):
    logpath = "/usr/local/u-mail/log/app"
    if request.method == 'POST':
        name = request.POST.get('name')
        status = request.POST.get('status')
        if status == "download":
            filepath = os.path.join(logpath, name)
            if os.path.exists(filepath):
                wrapper = FileWrapper(file(filepath))
                response = HttpResponse(wrapper, content_type='application/octet-stream')
                response['Content-Length'] = os.path.getsize(filepath)
                response['Content-Disposition'] = 'attachment; filename=%s' % name
                return response
            else:
                messages.add_message(request, messages.ERROR, _(u'日志文件不存在'))
                return redirect("log_maintain")

    index = 0
    lists = []
    listsa = os.listdir(logpath)
    listsa.sort()
    for line in listsa:
        filepath = os.path.join(logpath, line)
        if os.path.isfile(filepath):
            size = os.path.getsize(filepath)
            desc = getLogDesc(line)
            index += 1
            lists.append(
                LogFormat._make( [index, line, desc, size] )
            )
    return render(request, "maintain/log.html", context={
        "lists": lists,
    })


#########################################
# 隔离邮件
@licence_required
def isolateView(request):
    form = MailSearchForm(request.GET)
    if request.method == "POST":
        ids = ( request.POST.get('ids', False) ).split(',')
        status = request.POST.get('status', False)
        if status == "permit":
            ExtSquesterMail.objects.filter(status="wait", id__in=ids).update(status="permit")
            messages.add_message(request, messages.SUCCESS, u"放行成功")
        if status == "whitelist":
            ExtSquesterMail.objects.filter(status="wait", id__in=ids).update(status="whitelist")
            messages.add_message(request, messages.SUCCESS, u"放行成功")
        if status == "whitelist2":
            ExtSquesterMail.objects.filter(status="wait", id__in=ids).update(status="whitelist2")
            messages.add_message(request, messages.SUCCESS, u"放行成功")
        if status == "reject":
            ExtSquesterMail.objects.filter(status="wait", id__in=ids).update(status="reject")
            messages.add_message(request, messages.SUCCESS, u"确认隔离成功")
        current_uri = "{}?mail_status=wait".format( reverse("isolate_maintain") )

        create_task_trigger("sequester")
        return HttpResponseRedirect(current_uri)
        # return HttpResponseRedirect(reverse("isolate_maintain", args=("wait", )))
        # return redirect()
    return render(request, "maintain/isolate.html", context={
        "form": form,
    })

@licence_required
def isolateAjaxView(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'id', 'datetime', 'sender', 'recipient', 'subject', 'reason', 'status']

    mail_status = data.get('mail_status', '')
    mail_sender = data.get('mail_sender', '')
    mail_sender_not = data.get('mail_sender_not', '')
    mail_recipient = data.get('mail_recipient', '')
    mail_subject = data.get('mail_subject', '')
    mail_reason = data.get('mail_reason', '')
    mail_detail = data.get('mail_detail', '')

    if mail_status not in dict(ISOLATE_STATUS_R):
        mail_status = "wait"
    lists = ExtSquesterMail.objects.all()
    if mail_status:
        lists = lists.filter( status=mail_status )
    if mail_sender:
        lists = lists.filter( sender__icontains=mail_sender )
    if mail_recipient:
        lists = lists.filter( recipient__icontains=mail_recipient )
    if mail_subject:
        lists = lists.filter( subject__icontains=mail_subject )
    if mail_reason:
        lists = lists.filter( reason__icontains=mail_reason )
    if mail_detail:
        lists = lists.filter( detail__icontains=mail_detail )
    if mail_sender_not:
        lists = lists.exclude( sender__icontains=mail_sender_not )

    if search:
        lists = lists.filter( subject__icontains=search )

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
        t = TemplateResponse(request, 'maintain/ajax_isolate.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")
