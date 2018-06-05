# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ConfigParser
import re
import json
import os

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
from lib.tools import get_process_pid, restart_process, get_fail2ban_info, fail2ban_ip

from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.transaction import atomic
from django.db.models import Q
from django_redis import get_redis_connection

from app.fail2ban.forms import BanRuleForm, BanWhiteListForm, BanBlockListForm
from app.fail2ban.models import Fail2Ban, Fail2BanTrust, Fail2BanBlock

from lib import validators
from lib.tools import fail2ban_ip, get_redis_connection
from lib.licence import licence_required

def clear_fail2ban_cache():
    redis = get_redis_connection()
    for keyname in redis.keys("fail2ban_cache*") :
        redis.delete(keyname)

@licence_required
def fail2ban_rulelist(request):
    if request.method == "POST":
        id = request.POST.get('id', "")
        status = request.POST.get('status', "")
        if status == "delete":
            obj = Fail2Ban.objects.filter(pk=id).first()
            if obj:
                obj.delete()
                clear_fail2ban_cache()
                messages.add_message(request, messages.SUCCESS, u'删除成功')
    return render(request, "fail2ban/banned_rulelist.html",context={})

@licence_required
def ajax_fail2ban_rulelist(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'name', 'proto', 'internal','block_fail', 'block_unexists', 'block_minute', 'update_time', 'disabled',]

    lists = Fail2Ban.objects.all()
    if search:
        lists = lists.filter( Q(name__icontains=search) | Q(proto__icontains=search) )

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
        t = TemplateResponse(request, 'fail2ban/ajax_rulelist.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")

@licence_required
def fail2ban_rulemdf(request, mdf_id):
    obj = Fail2Ban.objects.filter(id=mdf_id).first()
    if not obj:
        messages.add_message(request, messages.SUCCESS, u'试图修改的数据不存在')
        return HttpResponseRedirect(reverse('fail2ban_home'))

    form = BanRuleForm(instance=obj)
    if request.method == "POST":
        form = BanRuleForm(instance=obj, post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'修改设置成功')
            return HttpResponseRedirect(reverse('fail2ban_home'))
    return render(request, "fail2ban/banned_rulemdf.html",context={"form":form})

@licence_required
def fail2ban_rulenew(request):
    form = BanRuleForm()
    if request.method == "POST":
        form = BanRuleForm(post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'添加设置成功')
            return HttpResponseRedirect(reverse('fail2ban_home'))
    return render(request, "fail2ban/banned_rulemdf.html",context={"form":form})

@licence_required
def fail2ban_blocklist(request):
    if request.method == "POST":
        id = request.POST.get('id', "")
        status = request.POST.get('status', "")
        if status == "delete":
            obj = Fail2BanBlock.objects.filter(pk=id).first()
            if obj:
                obj.delete()
                clear_fail2ban_cache()
                messages.add_message(request, messages.SUCCESS, u'删除成功')
    return render(request, "fail2ban/banned_blocklist.html",context={})

@licence_required
def ajax_fail2ban_blocklist(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'name', 'ip', 'expire_time', 'update_time', 'disabled',]

    lists = Fail2BanBlock.objects.all()
    if search:
        lists = lists.filter( Q(name__icontains=search) | Q(ip__icontains=search) )

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
        t = TemplateResponse(request, 'fail2ban/ajax_blocklist.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")

@licence_required
def fail2ban_blockmdf(request, mdf_id):
    obj = Fail2BanBlock.objects.filter(id=mdf_id).first()
    if not obj:
        messages.add_message(request, messages.SUCCESS, u'试图修改的数据不存在')
        return HttpResponseRedirect(reverse('fail2ban_blocklist'))

    form = BanBlockListForm(instance=obj)
    if request.method == "POST":
        form = BanBlockListForm(instance=obj, post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'修改设置成功')
            return HttpResponseRedirect(reverse('fail2ban_blocklist'))
    return render(request, "fail2ban/banned_blockmdf.html",context={"form":form})

@licence_required
def fail2ban_blocknew(request):
    form = BanBlockListForm()
    if request.method == "POST":
        form = BanBlockListForm(post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'添加设置成功')
            return HttpResponseRedirect(reverse('fail2ban_blocklist'))
    return render(request, "fail2ban/banned_blockmdf.html",context={"form":form})

@licence_required
def fail2ban_whitelist(request):
    if request.method == "POST":
        id = request.POST.get('id', "")
        status = request.POST.get('status', "")
        if status == "delete":
            obj = Fail2BanTrust.objects.filter(pk=id).first()
            if obj:
                obj.delete()
                clear_fail2ban_cache()
                messages.add_message(request, messages.SUCCESS, u'删除成功')
    return render(request, "fail2ban/banned_whitelist.html",context={})

@licence_required
def fail2ban_whitemdf(request, mdf_id):
    obj = Fail2BanTrust.objects.filter(id=mdf_id).first()
    if not obj:
        messages.add_message(request, messages.SUCCESS, u'试图修改的数据不存在')
        return HttpResponseRedirect(reverse('fail2ban_whitelist'))

    form = BanWhiteListForm(instance=obj)
    if request.method == "POST":
        form = BanWhiteListForm(instance=obj, post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'修改设置成功')
            return HttpResponseRedirect(reverse('fail2ban_whitelist'))
    return render(request, "fail2ban/banned_whitemdf.html",context={"form":form})

@licence_required
def fail2ban_whitenew(request):
    form = BanWhiteListForm()
    if request.method == "POST":
        form = BanWhiteListForm(post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'添加设置成功')
            return HttpResponseRedirect(reverse('fail2ban_home'))
    return render(request, "fail2ban/banned_whitemdf.html",context={"form":form})

@licence_required
def ajax_fail2ban_whitelist(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'ip', 'name', 'disabled',]

    lists = Fail2BanTrust.objects.all()
    if search:
        lists = lists.filter( Q(name__icontains=search) | Q(ip__icontains=search) )

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
        t = TemplateResponse(request, 'fail2ban/ajax_whitelist.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")
