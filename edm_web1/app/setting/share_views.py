# coding=utf-8
import re
import json
from django.contrib import messages
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.utils.translation import ugettext_lazy as _
from app.address.models import MailList, ShareMailList
from app.template.models import SendTemplate, ShareTemplte
from app.setting.utils.children import get_customer_child_obj
from app.statistics.utils.tools import get_realcustomer_and_obj

#################################################
# 共享模板
@login_required
def sub_share_template(request, user_id):
    user_id, subobj = get_realcustomer_and_obj(request, user_id)
    if request.method == "POST":
        status = int(request.POST.get('status', '0'))
        if status == 1: # 共享
            template_id = int(request.POST.get('id', "0"))
            ShareTemplte.objects.get_or_create(template_id=template_id, user_id=user_id)
            messages.add_message(request, messages.SUCCESS, _(u'共享模板成功'))
        if status == 2: # 撤销
            template_id = int(request.POST.get('id', "0"))
            ShareTemplte.objects.filter(template_id=template_id, user_id=user_id).delete()
            messages.add_message(request, messages.SUCCESS, _(u'撤销共享模板成功'))
        if status == 3: # 批量共享
            ids = (request.POST.get('ids', False)).split(',')
            for template_id in ids:
                ShareTemplte.objects.get_or_create(template_id=template_id, user_id=user_id)
            messages.add_message(request, messages.SUCCESS, _(u'批量共享模板成功'))
        if status == 4: # 批量撤销
            ids = (request.POST.get('ids', False)).split(',')
            ShareTemplte.objects.filter(user_id=user_id, template_id__in=ids).delete()
            messages.add_message(request, messages.SUCCESS, _(u'批量撤销共享模板成功'))
        return HttpResponseRedirect(reverse("sub_share_template", args=(user_id,)))
    return render(request, template_name='setting/sub_share_template.html', context={
        "subobj": subobj,
        "user_id": user_id,})

@login_required
def sub_share_template_ajax(request, user_id):
    user_id, subobj = get_realcustomer_and_obj(request, user_id)
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'id', 'name', 'created', 'updated']
    lists = SendTemplate.objects.filter(
        user=request.user).filter(
        result__in=['green', 'yellow', 'red_pass']).filter(
        isvalid=True)
    if search:
        lists = lists.filter(name__icontains=search)
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
        t = TemplateResponse(request, 'setting/sub_share_template_ajax.html', {
            'd': d,
            'number': number,
            'user_id': user_id,
        })
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


#################################################
# 共享模板
@login_required
def sub_share_addr(request, user_id):
    user_id, subobj = get_realcustomer_and_obj(request, user_id)
    if request.method == "POST":
        status = int(request.POST.get('status', '0'))
        if status == 1: # 共享
            template_id = int(request.POST.get('id', "0"))
            ShareMailList.objects.get_or_create(maillist_id=template_id, user_id=user_id)
            messages.add_message(request, messages.SUCCESS, _(u'共享联系人成功'))
        if status == 2: # 撤销
            template_id = int(request.POST.get('id', "0"))
            ShareMailList.objects.filter(maillist_id=template_id, user_id=user_id).delete()
            messages.add_message(request, messages.SUCCESS, _(u'撤销共享联系人成功'))
        if status == 3: # 批量共享
            ids = (request.POST.get('ids', False)).split(',')
            for template_id in ids:
                ShareMailList.objects.get_or_create(maillist_id=template_id, user_id=user_id)
            messages.add_message(request, messages.SUCCESS, _(u'批量共享联系人成功'))
        if status == 4: # 批量撤销
            ids = (request.POST.get('ids', False)).split(',')
            ShareMailList.objects.filter(user_id=user_id, maillist_id__in=ids).delete()
            messages.add_message(request, messages.SUCCESS, _(u'批量撤销共享联系人成功'))
        return HttpResponseRedirect(reverse("sub_share_addr", args=(user_id,)))
    return render(request, template_name='setting/sub_share_addr.html', context={
        "subobj": subobj,
        "user_id": user_id,})

@login_required
def sub_share_addr_ajax(request, user_id):
    user_id, subobj = get_realcustomer_and_obj(request, user_id)
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'id', 'subject', 'subject', 'created', 'count_real']
    lists = MailList.objects.filter(
        customer=request.user).filter(
        isvalid=True).filter(is_smtp=False)
    if search:
        lists = lists.filter(name__icontains=search)
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
        t = TemplateResponse(request, 'setting/sub_share_addr_ajax.html', {
            'd': d,
            'number': number,
            'user_id': user_id,
        })
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")