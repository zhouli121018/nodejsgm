# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import json
from django.shortcuts import render
from django.contrib import messages
from django.db.transaction import atomic
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Q

from app.distribute.models import ProxyServerConfig, ProxyServerList, ProxyServerStatus, ProxyAccountMove
from app.distribute.forms import ProxyServerConfigForm, ProxyServerListForm, ProxyAccountMoveForm
from app.distribute.tools import proxy_server_redis
from app.core.constants import PROXY_MOVE_TYPE, PROXY_MOVE_STATUS
from lib.validators import check_ip
from lib.licence import licence_required


@licence_required
def config(request):
    obj = ProxyServerConfig.proxy_open()
    form = ProxyServerConfigForm(instance=obj, get=request.GET)
    if request.method == "POST":
        form = ProxyServerConfigForm(instance=obj, get=request.GET, post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u"配置修改成功")
            return HttpResponseRedirect(reverse('proxy_open_config'))

    return render(request, template_name='distribute/config.html', context={
        'form': form,
    })


@licence_required
def distribute_list(request):
    local_obj = ProxyServerConfig.local_ip()
    if request.method == "POST":
        id = request.POST.get('id', False)
        status = request.POST.get('status', False)

        # 设置 本机IP
        if status == "local_ip":
            local_ip = request.POST.get('local_ip', False)
            if not check_ip(local_ip):
                messages.add_message(request, messages.ERROR, u'您输入的本机IP地址不合法！')
            else:
                local_obj.config_data = local_ip
                local_obj.save()
                messages.add_message(request, messages.SUCCESS, u'本机IP地址设置成功！')

        # 取消主服务器
        if status == "unmaster":
            with atomic():
                lists = ProxyServerList.objects.filter(pk=id)
                obj = lists.first()
                if obj.is_master:
                    lists.update(is_master=False)
                    proxy_server_redis("proxy_server_list")
            messages.add_message(request, messages.SUCCESS, u'取消主服务器成功')

        # 设为主服务器
        if status == "master":
            with atomic():
                ProxyServerList.objects.filter(pk=id).update(is_master=True)
                ProxyServerList.objects.exclude(pk=id).update(is_master=False)
                proxy_server_redis("proxy_server_list", int(id))
            messages.add_message(request, messages.SUCCESS, u'设为主服务器成功')

        # 启用
        if status == "active":
            with atomic():
                ProxyServerList.objects.filter(pk=id).update(disabled="-1")
                proxy_server_redis("proxy_server_list")
            messages.add_message(request, messages.SUCCESS, u'启用成功')

        # 禁用
        if status == "disabled":
            with atomic():
                ProxyServerList.objects.filter(pk=id).update(disabled="1")
                proxy_server_redis("proxy_server_list")
            messages.add_message(request, messages.SUCCESS, u'禁用成功')

        # 删除
        if status == "delete":
            with atomic():
                lists = ProxyServerList.objects.filter(pk=id)
                obj = lists.first()
                if obj and obj.is_master:
                    if ProxyServerList.objects.exclude(pk=id).exists():
                        messages.add_message(request, messages.ERROR, u'主服务器删除失败，如需删除主服务器，请先删除其他服务器。')
                    else:
                        lists.delete()
                        proxy_server_redis("proxy_server_list")
                        messages.add_message(request, messages.SUCCESS, u'主服务器删除成功')
                else:
                    lists.delete()
                    proxy_server_redis("proxy_server_list")
                    messages.add_message(request, messages.SUCCESS, u'删除成功')

        return HttpResponseRedirect(reverse('distribute_list'))

    return render(request, template_name='distribute/distribute.html', context={
        "local_obj": local_obj,
    })

@licence_required
def ajax_distribute_list(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')

    colums = ['id', 'server_name', 'server_ip', 'is_master', 'disabled']

    lists = ProxyServerList.objects.all()
    if search:
        lists = lists.filter(Q(server_name__icontains=search) | Q(server_ip__icontains=search))

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
        t = TemplateResponse(request, 'distribute/ajax_distribute.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")


@licence_required
def distribute_add(request):
    form = ProxyServerListForm()
    if request.method == "POST":
        form = ProxyServerListForm(post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'服务器 ({}) 添加成功'.format(form.server_name.value))
            return HttpResponseRedirect(reverse('distribute_list'))

    return render(request, template_name='distribute/distribute_modify.html', context={
        'form': form,
    })

@licence_required
def distribute_modify(request, proxy_id):
    obj = ProxyServerList.objects.get(pk=proxy_id)
    form = ProxyServerListForm(instance=obj)
    if request.method == "POST":
        form = ProxyServerListForm(post=request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'服务器 ({}) 修改成功'.format(form.server_name.value))
            return HttpResponseRedirect(reverse('distribute_list'))

    return render(request, template_name='distribute/distribute_modify.html', context={
        'form': form,
    })


@licence_required
def distribute_server_status(request):
    server_ids = ProxyServerList.objects.values_list("id", flat=True)
    lists = ProxyServerStatus.objects.filter(pk__in=server_ids).order_by("-last_update")
    return render(request, template_name='distribute/status.html', context={
        'lists': lists,
    })


@licence_required
def distribute_account_move(request):

    if request.method == "POST":
        id = request.POST.get('id', False)
        status = request.POST.get('status', False)
        if status == "delete":
            obj = ProxyAccountMove.objects.get(pk=id)
            if obj.status not in ("finish", "unvalid"):
                messages.add_message(request, messages.ERROR, u"不能删除该状态下的迁移")
            else:
                obj.delete()
                messages.add_message(request, messages.SUCCESS, u"删除成功")
        return HttpResponseRedirect(reverse('distribute_account_move'))

    return render(request, template_name='distribute/move.html', context={
        "movetypes":    PROXY_MOVE_TYPE,
        "statustypes":  PROXY_MOVE_STATUS,
    })

@licence_required
def ajax_distribute_move(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')

    movetype = data.get('movetype', '')
    statustype = data.get('statustype', '')
    movekey = data.get('movekey', '')

    colums = ['id', 'from_server', 'target_server',
              'mailbox', 'old_mailbox', 'move_type', 'status', 'sync_mail', 'last_update']

    lists = ProxyAccountMove.objects.all()
    if movetype:
        lists = lists.filter(move_type=movetype)
    if statustype:
        lists = lists.filter(status=statustype)
    if movekey:
        lists = lists.filter(Q(desc_msg__icontains=movekey) | Q(mailbox__icontains=movekey) | Q(old_mailbox__icontains=movekey))
    if search:
        lists = lists.filter(Q(desc_msg__icontains=search) | Q(mailbox__icontains=search) | Q(old_mailbox__icontains=search))

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
        t = TemplateResponse(request, 'distribute/ajax_distribute_move.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")

@licence_required
def distribute_move_add(request):
    form = ProxyAccountMoveForm()
    if request.method == "POST":
        form = ProxyAccountMoveForm(post=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'添加迁移成功')
            return HttpResponseRedirect(reverse('distribute_account_move'))

    return render(request, template_name='distribute/move_add.html', context={
        "form": form,
    })

@licence_required
def distribute_move_modify(request, move_id):
    obj = ProxyAccountMove.objects.get(pk=move_id)
    if obj.move_type == "to" and obj.status not in ("init", "wait", "sync", "accept", "ready", "backup"):
        messages.add_message(request, messages.ERROR, u"不能修改该状态下的迁移")
        return HttpResponseRedirect(reverse('distribute_account_move'))
    if obj.move_type == "from" and obj.status not in ("create", "done", "imap_recv"):
        messages.add_message(request, messages.ERROR, u"不能修改该状态下的迁移")
        return HttpResponseRedirect(reverse('distribute_account_move'))

    form = ProxyAccountMoveForm(instance=obj)
    if request.method == "POST":
        form = ProxyAccountMoveForm(post=request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'修改迁移成功')
            return HttpResponseRedirect(reverse('distribute_account_move'))

    return render(request, template_name='distribute/move_add.html', context={
        "form": form,
    })
