# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import json
from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.utils.translation import ugettext_lazy as _

from .models import CoreGroup, CoreGroupMember
from .forms import CoreGroupForms, CoreGroupMemberForm
from app.utils.domain_session import get_domainid_bysession, get_session_domain


@login_required
def groups(request):
    if request.method == "POST":
        action = request.POST.get('action', '')
        if action == 'delete':
            group_id = request.POST.get('id', '')
            CoreGroup.objects.get(id=group_id).delete()
            messages.add_message(request, messages.SUCCESS, u'删除成功')
        return HttpResponseRedirect(reverse('core_group_list'))
    domain_id = get_domainid_bysession(request)
    lists = CoreGroup.objects.filter(domain_id=domain_id).order_by('-id')
    return render(request, "group/groups.html",
                  {"lists": lists})

@login_required
def groups_add(request):
    domain_id = get_domainid_bysession(request)
    domain = get_session_domain(domain_id)
    form = CoreGroupForms(domain_id, domain)
    if request.method == "POST":
        form = CoreGroupForms(domain_id, domain, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'添加成功')
            return HttpResponseRedirect(reverse('core_group_list'))
    return render(request, "group/groups_add.html",
                  { 'form': form })

@login_required
def groups_modify(request, group_id):
    obj = CoreGroup.objects.get(id=group_id)
    form = CoreGroupForms(obj.domain_id, obj.domain, instance=obj)
    if request.method == "POST":
        form = CoreGroupForms(obj.domain_id, obj.domain, request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'添加成功')
            return HttpResponseRedirect(reverse('core_group_list'))
    return render(request, "group/groups_add.html",
                  { 'form': form })

@login_required
def groups_mem(request, group_id):
    obj = CoreGroup.objects.get(id=group_id)
    if request.method == "POST":
        action = request.POST.get('action', '')
        if action == 'delete':
            id = request.POST.get('id', '')
            CoreGroupMember.objects.get(id=id).delete()
            messages.add_message(request, messages.SUCCESS, u'删除成功')
        if action == 'deleteall':
            ids = request.POST.get('ids', '')
            ids = ids.split(',')
            CoreGroupMember.objects.filter(id__in=ids).delete()
            messages.add_message(request, messages.SUCCESS, u'删除成功')
        if action == 'add':
            everyone_addresses = request.POST.get('everyone_addresses', '')
            everyone_addresses = everyone_addresses.split(',')
            success, fail = 0, 0
            for addr in everyone_addresses:
                form = CoreGroupMemberForm(obj, {'group': obj, 'address': addr,})
                if form.is_valid():
                    form.save()
                    success += 1
                else:
                    fail += 1
            messages.add_message(request, messages.SUCCESS,
                                 _(u'批量添加成功%(success)s个, 失败%(fail)s个') % {"success": success, "fail": fail})
        if action == 'remark':
            mem_id = request.POST.get('mem_id', '')
            remark = request.POST.get('remark', '')
            mo = CoreGroupMember.objects.filter(id=mem_id).first()
            if mo:
                mo.remark=remark
                mo.save()
            return HttpResponse(json.dumps({'msg': 'ok'}), content_type="application/json")
        return HttpResponseRedirect(reverse('core_group_member', args=group_id))
    return render(request, "group/groups_mem.html",
                  {'obj': obj, 'group_id': group_id})

@login_required
def groups_mem_ajax(request, group_id):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')

    colums = ['id', 'id', 'address']
    lists = CoreGroupMember.objects.filter(group_id=group_id)
    if search:
        lists = lists.filter(address__icontains=search)

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
    number = length * (page - 1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'group/groups_mem_ajax.html', {'d': d, 'number': number })
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")

@login_required
def groups_mem_add(request, group_id):
    obj = CoreGroup.objects.get(id=group_id)
    return render(request, "group/groups_mem_add.html",
                  {'group_id': group_id, 'obj': obj})