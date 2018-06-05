# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import json
import time
import uuid
import random
from django.shortcuts import render
from django.contrib import messages
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.db.transaction import atomic
from django.db.models import Q
from django_redis import get_redis_connection

from app.core.models import Mailbox, DomainAttr, Domain, CoreMonitor, CoreAlias, MailboxExtra
from app.domain.models import Signature, SecretMail
from app.domain.forms import DomainBasicForm, DomainRegLoginForm, DomainRegLoginWelcomeForm, DomainRegLoginAgreeForm, \
                                DomainSysRecvLimitForm, DomainSysSecurityForm, DomainSysRecvWhiteListForm, DomainSysSecurityPasswordForm, \
                                DomainSysPasswordForm, DomainSysInterfaceForm, DomainSysInterfaceAuthApiForm, DomainSysInterfaceIMApiForm, \
                                DomainSysOthersForm, DomainSysOthersCleanForm, DomainSysOthersAttachForm, \
                                DomainSignDomainForm, DomainSignPersonalForm, \
                                DomainModuleHomeForm, DomainModuleMailForm, DomainModuleSetForm, DomainModuleOtherForm, \
                                DomainSecretForm
import app.domain.constants as constants

from lib import validators
from lib.licence import licence_required
from lib.tools import generate_task_id, clear_redis_cache

def getDomainObj(request):
    domain_list = Domain.objects.all()
    domain = request.GET.get("domain","")
    if domain:
        obj = domain_list.filter(domain=domain).first()
    else:
        obj = domain_list.first()
    return obj, []
    return obj, domain_list

def domainHome(request):
    print "3333333333333333333"
    domain, domain_list = getDomainObj(request)
    if not domain:
        return HttpResponseRedirect(reverse('domain_home'))
    form = DomainBasicForm(domain_id=domain.id)
    return render(request, "domain/static.html", context={
        "page": "basic",
        "form": form,
        "domain_list": domain_list,
        "domain": domain,
    })

def domainBasic(request):
    domain, domain_list = getDomainObj(request)
    if not domain:
        return HttpResponseRedirect(reverse('domain_home'))
    form = DomainBasicForm(domain_id=domain.id)
    if request.method == "POST":
        form = DomainBasicForm(domain_id=domain.id, post=request.POST)
        if form.is_valid():
            form.save()
    return render(request, "domain/include/static_basic.html", context={
        "page": "basic",
        "form": form,
        "domain_list": domain_list,
        "domain": domain,
    })

def domainRegLogin(request):
    domain, domain_list = getDomainObj(request)
    if not domain:
        return HttpResponseRedirect(reverse('domain_home'))
    form = DomainRegLoginForm(domain_id=domain.id)
    form_welcome = DomainRegLoginWelcomeForm(domain_id=domain.id)
    form_agree = DomainRegLoginAgreeForm(domain_id=domain.id)
    print ">>>>>>>>>>>>>>>  domainRegLogin ", request.POST
    if request.method == "POST":
        action = request.POST.get('action', '')
        if action == "setting":
            form = DomainRegLoginForm(domain_id=domain.id, post=request.POST)
            form.checkSave()
        elif action == "welcome":
            form_welcome = DomainRegLoginWelcomeForm(domain_id=domain.id, post=request.POST)
            form_welcome.checkSave()
        elif action == "agreement":
            form_agree = DomainRegLoginAgreeForm(domain_id=domain.id, post=request.POST)
            form_agree.checkSave()
    return render(request, "domain/include/static_reg_login.html", context={
        "page": "reg_login",
        "form": form,
        "form_welcome": form_welcome,
        "form_agree"  : form_agree,
        "domain_list": domain_list,
        "domain": domain,
    })

def domainSys(request):
    domain, domain_list = getDomainObj(request)
    if not domain:
        return HttpResponseRedirect(reverse('domain_home'))
    form_limit = DomainSysRecvLimitForm(domain_id=domain.id)
    form_security = DomainSysSecurityForm(domain_id=domain.id)
    form_password = DomainSysPasswordForm(domain_id=domain.id)
    form_interface = DomainSysInterfaceForm(domain_id=domain.id)
    form_others = DomainSysOthersForm(domain_id=domain.id)

    form_send_limit_white = DomainSysRecvWhiteListForm(type="send", domain_id=domain.id)
    form_recv_limit_white = DomainSysRecvWhiteListForm(type="recv", domain_id=domain.id)

    form_security_letter = DomainSysSecurityPasswordForm(domain_id=domain.id)

    form_auth_api = DomainSysInterfaceAuthApiForm(domain_id=domain.id)
    form_im_api = DomainSysInterfaceIMApiForm(domain_id=domain.id)

    form_space_clean = DomainSysOthersCleanForm(domain_id=domain.id)
    form_client_attach = DomainSysOthersAttachForm(domain_id=domain.id)

    print ">>>>>>>>>>>  domainSys   request.POST = ",request.POST
    if request.method == "POST":
        action = request.POST.get('action', '')
        if action == "limit":
            form_limit = DomainSysRecvLimitForm(domain_id=domain.id, post=request.POST)
            form_limit.checkSave()
        elif action == "security":
            form_security = DomainSysSecurityForm(domain_id=domain.id, post=request.POST)
            form_security.checkSave()
        elif action == "password":
            form_password = DomainSysPasswordForm(domain_id=domain.id, post=request.POST)
            form_password.checkSave()
        elif action == "interface":
            form_interface = DomainSysInterfaceForm(domain_id=domain.id, post=request.POST)
            form_interface.checkSave()
        elif action == "others":
            form_others = DomainSysOthersForm(domain_id=domain.id, post=request.POST)
            form_others.checkSave()

        elif action == "send_limit_white":
            form_send_limit_white = DomainSysRecvWhiteListForm(type="send", domain_id=domain.id, post=request.POST)
            form_send_limit_white.checkSave()
        elif action == "recv_limit_white":
            form_recv_limit_white = DomainSysRecvWhiteListForm(type="recv", domain_id=domain.id, post=request.POST)
            form_recv_limit_white.checkSave()
        elif action == "security_letter":
            form_security_letter = DomainSysSecurityPasswordForm(domain_id=domain.id, post=request.POST)
            form_security_letter.checkSave()
        elif action == "auth_api":
            form_auth_api = DomainSysInterfaceAuthApiForm(domain_id=domain.id, post=request.POST)
            form_auth_api.checkSave()
        elif action == "im_api":
            form_im_api = DomainSysInterfaceIMApiForm(domain_id=domain.id, post=request.POST)
            form_im_api.checkSave()
        elif action == "space_clean":
            form_space_clean = DomainSysOthersCleanForm(domain_id=domain.id, post=request.POST)
            form_space_clean.checkSave()
        elif action == "client_attach":
            form_client_attach = DomainSysOthersAttachForm(domain_id=domain.id, post=request.POST)
            form_client_attach.checkSave()
    return render(request, "domain/include/static_sys.html", context={
        "page": "sys",
        "domain_list": domain_list,
        "domain": domain,
        "form_limit": form_limit,
        "form_security": form_security,
        "form_password": form_password,
        "form_interface": form_interface,
        "form_others"   : form_others,

        "form_send_limit_white" :   form_send_limit_white,
        "form_recv_limit_white" :   form_recv_limit_white,
        "form_security_letter"  :   form_security_letter,

        "form_auth_api"          :   form_auth_api,
        "form_im_api"            :   form_im_api,

        "form_space_clean"      :   form_space_clean,
        "form_client_attach"    :   form_client_attach,
    })

#设置例外的密码规则用户
def domainSysPasswordExtra(request):
    """
    类型： POST
    {% url 'domain_sys_pwd_extra' %}
    删除
        domain/sys/pwd_extra?action=del&boxlist=anna@test.com|lindaiyu@test.com
    添加
        domain/sys/pwd_extra?action=add&boxlist=anna@test.com|lindaiyu@test.com
    返回值举例:
        {"reason": "", "result": 1}
        {"reason": " 'anna22222@test.com' not exists |  'lindaiyu2222@test.com' not exists", "result": 0}
    """
    domain, domain_list = getDomainObj(request)
    data = { "result" : 0, "reason" : "" }
    reasonList = []
    if request.method == "POST":
        action = request.POST.get('action', '')
        boxlist = request.POST.get('boxlist', '')
        boxlist = [box.strip() for box in boxlist.split("|") if box.strip()]
        extraType = u"password_extra_{}".format(domain.id)
        for box in boxlist:
            boxObj = Mailbox.objects.filter(mailbox=box).first()
            if not boxObj:
                reasonList.append(u" '{}' not exists".format(box))
                continue
            objExtra = MailboxExtra.objects.filter(mailbox_id=boxObj.id, type=extraType).first()
            if action == u"add":
                if objExtra:
                    objExtra.data = u"1"
                    obj.last_update = u"{}".format(time.strftime("%Y-%m-%d %H:%M:%S"))
                    objExtra.save()
                else:
                    MailboxExtra.objects.create(
                        mailbox_id = boxObj.id,
                        mailbox = boxObj.mailbox,
                        size = 0,
                        type = extraType,
                        data = u"1",
                        last_update = u"{}".format(time.strftime("%Y-%m-%d %H:%M:%S")),
                        )
                data["result"] = 1
            elif action == u"del":
                if objExtra:
                    objExtra.delete()
                data["result"] = 1
    data["reason"] = " | ".join( reasonList )
    return HttpResponse(json.dumps(data), content_type="application/json")

def domainWebmail(request):
    domain, domain_list = getDomainObj(request)
    if not domain:
        return HttpResponseRedirect(reverse('domain_home'))
    form = DomainBasicForm(domain_id=domain.id)
    if request.method == "POST":
        form = DomainBasicForm(domain_id=domain.id, post=request.POST)
        if form.is_valid():
            form.save()
    return render(request, "domain/include/static_webmail.html", context={
        "page": "webmail",
        "form": form,
        "domain_list": domain_list,
        "domain": domain,
    })

def domainSign(request):
    domain, domain_list = getDomainObj(request)
    if not domain:
        return HttpResponseRedirect(reverse('domain_home'))
    form_domain = DomainSignDomainForm(domain_id=domain.id)
    form_personal = DomainSignPersonalForm(domain_id=domain.id)
    print ">>>>>>>>>>>>>>  domainSign   ",request.POST
    if request.method == "POST":
        action = request.POST.get('action', '')
        if action == "domain_sign":
            form_domain = DomainSignDomainForm(domain_id=domain.id, post=request.POST)
            form_domain.checkSave()
        elif action == "personal_sign":
            form_personal = DomainSignPersonalForm(domain_id=domain.id, post=request.POST)
            form_personal.checkSave()
        elif action == "personal_sign_apply":
            form_personal = DomainSignPersonalForm(domain_id=domain.id, post=request.POST)
            if form_personal.checkSave():
                form_personal.applyAll()
    return render(request, "domain/include/static_sign.html", context={
        "page": "sign",
        "domain": domain,
        "domain_list": domain_list,
        "form_domain"   :  form_domain,
        "form_personal" :  form_personal,
    })

def domainModule(request):
    domain, domain_list = getDomainObj(request)
    if not domain:
        return HttpResponseRedirect(reverse('domain_home'))
    form_home = DomainModuleHomeForm(domain_id=domain.id)
    form_mail = DomainModuleMailForm(domain_id=domain.id)
    form_set = DomainModuleSetForm(domain_id=domain.id)
    form_other = DomainModuleOtherForm(domain_id=domain.id)
    if request.method == "POST":
        action = request.POST.get('action', '')
        if action == "home":
            form_home = DomainModuleHomeForm(domain_id=domain.id, post=request.POST)
            form_home.checkSave()
        elif action == "mail":
            form_mail = DomainModuleMailForm(domain_id=domain.id, post=request.POST)
            form_mail.checkSave()
        elif action == "set":
            form_set = DomainModuleSetForm(domain_id=domain.id, post=request.POST)
            form_set.checkSave()
        elif action == "other":
            form_other = DomainModuleOtherForm(domain_id=domain.id, post=request.POST)
            form_other.checkSave()
    return render(request, "domain/include/static_module.html", context={
        "page": "module",
        "domain_list": domain_list,
        "domain": domain,
        "form_home"     :  form_home,
        "form_mail"     :  form_mail,
        "form_set"      :  form_set,
        "form_other"    :  form_other,
    })

def domainPublicList(request):
    domain, domain_list = getDomainObj(request)
    if not domain:
        return HttpResponseRedirect(reverse('domain_home'))
    form = DomainBasicForm(domain_id=domain.id)
    if request.method == "POST":
        form = DomainBasicForm(domain_id=domain.id, post=request.POST)
        if form.is_valid():
            form.save()
    return render(request, "domain/include/static_public_list.html", context={
        "page": "public",
        "form": form,
        "domain_list": domain_list,
        "domain": domain,
    })

def domainSecret(request):
    domain, domain_list = getDomainObj(request)
    if not domain:
        return HttpResponseRedirect(reverse('domain_home'))
    if request.method == "POST":
        action = request.POST.get('action', '')
        data = {}
        result = 1
        reason = u""
        if action == u"new":
            form = DomainSecretForm(post=request.POST)
            if form.is_valid():
                form.save()
            else:
                result = 0
                reason = form.error
        if action == u"del":
            form = DomainSecretForm(post=request.POST)
            if form.is_valid():
                form.save()
            else:
                result = 0
                reason = form.error
        form = DomainSecretForm(post=request.POST)
        grade = request.POST.get(u"grade", constants.DOMAIN_SECRET_GRADE_1)
        data = DomainSecretForm.getBoxListByGrade(grade)
        data = {
            "result"    :   result,
            "data"      :   data,
            "reason"    :   reason,
            "gradeNum_1": form.gradeNum_1,
            "gradeNum_2": form.gradeNum_2,
            "gradeNum_3": form.gradeNum_3,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")

    form = DomainSecretForm()
    return render(request, "domain/include/static_secret.html", context={
        "page": "secret",
        "form": form,
        "domain_list": domain_list,
        "domain": domain,
    })
