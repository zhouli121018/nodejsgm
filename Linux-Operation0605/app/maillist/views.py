# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import json
import time
import datetime
from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from .models import ExtList, ExtListMember
from .forms import ExtListForm, ExtListMemberForm, ExcelTxtImport
from app.core.models import Mailbox, Department, DepartmentMember
from app.utils.domain_session import get_domainid_bysession, get_session_domain
from app.utils.response.excel_response import ExcelResponse, FormatExcelResponse

@login_required
def maillist_list(request):
    if request.method == "POST":
        action = request.POST.get('action', '')
        if action == 'delete':
            list_id = request.POST.get('id', '')
            obj = ExtList.objects.filter(id=list_id).firs()
            if obj.is_everyone:
                messages.add_message(request, messages.ERROR, u'不能被删除')
            else:
                ExtListMember.objects.filter(list_id=list_id).delete()
                ExtList.objects.get(id=list_id).delete()
                messages.add_message(request, messages.SUCCESS, u'删除成功')
        return HttpResponseRedirect(reverse('maillist_list'))
    domain_id = get_domainid_bysession(request)
    lists = ExtList.objects.filter(domain_id=domain_id).order_by('-id')
    return render(request, "maillist/maillist_list.html", {'lists': lists})

@login_required
def maillist_add(request):
    obj=None
    domain_id = get_domainid_bysession(request)
    domain = get_session_domain(domain_id)
    form = ExtListForm(domain_id, domain, None, None, False)
    if request.method == "POST":
        form = ExtListForm(domain_id, domain, None, None, False, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'添加成功')
            return HttpResponseRedirect(reverse('maillist_list'))
    return render(request, "maillist/maillist_add.html",
                  { 'form': form, 'obj': obj, })

@login_required
def maillist_modify(request, list_id):
    obj = ExtList.objects.get(id=list_id)
    form = ExtListForm(obj.domain_id, obj.domain, obj.listname, obj.address, False, instance=obj)
    if request.method == "POST":
        form = ExtListForm(obj.domain_id, obj.domain, obj.listname, obj.address, False, request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'修改成功')
            return HttpResponseRedirect(reverse('maillist_list'))
    return render(request, "maillist/maillist_add.html",
                  { 'form': form, 'obj': obj, })


@login_required
def maillist_export(request):
    lists = [[u'邮件名称', u'邮件地址', u'说明信息', u'列表类型', u'域名']]
    file_name = u'邮件列表-{}'.format(datetime.datetime.now().strftime('%Y%m%d'))
    lists2 = ExtList.objects.all()
    for d in lists2:
        lists.append([d.listname, d.address, d.description, d.get_listtype_display(), d.domain])
    return ExcelResponse(lists, file_name, encoding='gbk')


@login_required
def maillist_import(request):
    form = ExcelTxtImport()
    domain_id = get_domainid_bysession(request)
    domain = get_session_domain(domain_id)
    if request.method == "POST":
        form = ExcelTxtImport(data=request.POST, files=request.FILES)
        if form.is_valid():
            success, fail = 0, 0
            if form.file_ext == 'txt':
                lines = form.file_obj.readlines()
                for line in lines:
                    line = line.replace('\n', '').replace('\r', '').replace('\000', '')
                    elem = line.strip().replace(u'，', '\t').replace(',', '\t').replace(u'；', '\t').replace(';', '\t').split('\t')
                    length = len(elem)
                    listname = elem[0] if length>1 else ''
                    address = elem[1] if length>2 else ''
                    description = elem[2] if length>3 else ''
                    form = ExtListForm(domain_id, domain, None, None, True, {
                        'domain_id': domain_id, 'listname': listname,
                        'address': address, 'description': description,
                        'permission': 'public', 'disabled': '1',
                    })
                    if form.is_valid():
                        form.save()
                        success += 1
                    else:
                        fail += 1
            if form.file_ext == 'csv':
                import csv
                lines = list(csv.reader(form.file_obj))
                for elem in lines:
                    length = len(elem)
                    listname = elem[0] if length > 1 else ''
                    address = elem[1] if length > 2 else ''
                    description = elem[2] if length > 3 else ''
                    form = ExtListForm(domain_id, domain, None, None, True, {
                        'domain_id': domain_id, 'listname': listname,
                        'address': address, 'description': description,
                        'permission': 'public', 'disabled': '1',
                    })
                    if form.is_valid():
                        form.save()
                        success += 1
                    else:
                        fail += 1
            if form.file_ext in ('xls', 'xlxs'):
                import xlrd
                content = form.file_obj.read()
                workbook = xlrd.open_workbook(filename=None, file_contents=content)
                table = workbook.sheets()[0]
                for line in xrange(table.nrows):
                    elem = table.row_values(line)
                    listname = elem[0] if elem else ''
                    address = elem[1] if elem else ''
                    description = elem[2] if elem else ''
                    form = ExtListForm(domain_id, domain, None, None, True, {
                        'domain_id':domain_id, 'listname':listname,
                        'address':address, 'description':description,
                        'permission': 'public', 'disabled': '1',
                    })
                    if form.is_valid():
                        form.save()
                        success += 1
                    else:
                        fail += 1
            messages.add_message(request, messages.SUCCESS,
                                 _(u'批量添加成功%(success)s个, 失败%(fail)s个') % {"success": success, "fail": fail})
            return HttpResponseRedirect(reverse('maillist_list'))
    return render(request, "maillist/maillist_import.html", {'form': form,})

@login_required
def maillist_template(request):
    data = request.GET
    file_ext = data.get('ext', '').strip()
    lists = [[u'邮件列表名称', u'邮件列表地址', u'说明信息', u'权限类型'], [u'test', u'test', u'test', u'说明']]
    if file_ext == 'csv':
        force_csv = True
        mimetype = 'text/csv'
        response = FormatExcelResponse(
            data=lists, output_name='maillist', force_csv=force_csv,
            encoding='gbk', mimetype=mimetype, file_ext=file_ext
        )
    elif file_ext == 'txt':
        force_csv = False
        mimetype = 'text/plain'
        response = FormatExcelResponse(
            data=lists, output_name='maillist', force_csv=force_csv,
            encoding='gbk', mimetype=mimetype, file_ext=file_ext
        )
    elif file_ext == 'xls':
        force_csv = False
        mimetype = 'application/vnd.ms-excel'
        response = FormatExcelResponse(
            data=lists, output_name='maillist', force_csv=force_csv,
            encoding='gbk', mimetype=mimetype, file_ext=file_ext
        )
    elif file_ext == 'xlsx':
        force_csv = False
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = FormatExcelResponse(
            data=lists, output_name='maillist', force_csv=force_csv,
            encoding='gbk', mimetype=mimetype, file_ext=file_ext
        )
    return response

# ------------------------------------------
# 维护列表
@login_required
def maillist_maintain(request, list_id):
    lobj = ExtList.objects.get(id=list_id)
    if request.method == "POST":
        action = request.POST.get('action', '')
        if action == 'delete':
            id = request.POST.get('id', '')
            ExtListMember.objects.get(id=id).delete()
            messages.add_message(request, messages.SUCCESS, u'删除成功')
        if action == 'deleteall':
            ids = request.POST.get('ids', '')
            ids = ids.split(',')
            ExtListMember.objects.filter(id__in=ids).delete()
            messages.add_message(request, messages.SUCCESS, u'删除成功')
        if action == 'everyone':
            everyone_addresses = request.POST.get('everyone_addresses', '')
            everyone_addresses = everyone_addresses.split(',')
            success, fail = 0, 0
            update_time = int(time.time())
            for addr in everyone_addresses:
                form = ExtListMemberForm(list_id, lobj, {
                    'address': addr, 'permit': '1', 'list_id': list_id, 'update_time': update_time})
                if form.is_valid():
                    form.save()
                    success += 1
                else:
                    fail += 1
            messages.add_message(request, messages.SUCCESS,
                                 _(u'批量添加成功%(success)s个, 失败%(fail)s个') % {"success": success, "fail": fail})
        return HttpResponseRedirect(reverse('maillist_maintain', args=list_id))
    return render(request, "maillist/maillist_maintain.html",
                  { 'list_id': list_id, 'lobj': lobj })

@login_required
def maillist_maintain_ajax(request, list_id):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')

    colums = ['id', 'id', 'address', 'permit', 'update_time']
    lists = ExtListMember.objects.filter(list_id=list_id)
    lobj = ExtList.objects.get(id=list_id)
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
        t = TemplateResponse(request, 'maillist/maillist_maintain_ajax.html', {'d': d, 'number': number, 'lobj': lobj,})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")

@login_required
def maillist_maintain_add(request, list_id):
    lobj = ExtList.objects.get(id=list_id)
    form = ExtListMemberForm(list_id, lobj)
    if request.method == "POST":
        form = ExtListMemberForm(list_id, lobj, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'添加成功')
            return HttpResponseRedirect(reverse('maillist_maintain', args=list_id))
    return render(request, "maillist/maillist_maintain_add.html",
                  { 'form': form, 'obj': None, 'list_id': list_id, 'lobj': lobj })

@login_required
def maillist_maintain_modify(request, list_id, member_id):
    obj = ExtListMember.objects.get(id=member_id)
    lobj = ExtList.objects.get(id=list_id)
    form = ExtListMemberForm(list_id, lobj, instance=obj)
    if request.method == "POST":
        form = ExtListMemberForm(list_id, lobj, request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'修改成功')
            return HttpResponseRedirect(reverse('maillist_maintain', args=list_id))
    return render(request, "maillist/maillist_maintain_add.html",
                  { 'form': form, 'obj': obj, 'list_id': list_id, 'lobj': lobj })

@login_required
def maillist_maintain_batchadd(request, list_id):
    lobj = ExtList.objects.get(id=list_id)
    if lobj.is_everyone:
        return render(request, "maillist/maillist_maintain_select_everyone.html",
                      { 'list_id': list_id, 'lobj': lobj })
    else:
        if request.method == "POST":
            addresses = request.POST.get('addresses', '')
            permit = request.POST.get('permit', '')
            addresses = addresses.split('\n')
            success, fail = 0, 0
            update_time = int(time.time())
            for addr in addresses:
                addr = addr.replace('\r', '')
                if not addr: continue
                form = ExtListMemberForm(list_id, lobj, {
                    'address': addr, 'permit': permit, 'list_id': list_id, 'update_time': update_time})
                if form.is_valid():
                    form.save()
                    success += 1
                else:
                    fail += 1
            messages.add_message(request, messages.SUCCESS,
                                 _(u'批量添加成功%(success)s个, 失败%(fail)s个') % {"success": success, "fail": fail})
            return HttpResponseRedirect(reverse('maillist_maintain', args=list_id))
        return render(request, "maillist/maillist_maintain_batchadd.html",
                      { 'list_id': list_id, 'lobj': lobj })

@login_required
def maillist_maintain_select(request):
    return render(request, "maillist/maillist_maintain_select.html")

@login_required
def maillist_maintain_select_ajax(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')

    colums = ['id', 'id', 'mailbox']
    lists = Mailbox.objects.all()

    if search:
        dids = Department.objects.filter(title__icontains=search).values_list('id')
        mailbox_ids = DepartmentMember.objects.filter(dept_id=dids).values_list('mailbox_id')
        lists = lists.filter(Q(mailbox__icontains=search) | Q(id__in=mailbox_ids))

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
        t = TemplateResponse(request, 'maillist/maillist_maintain_select_ajax.html', {'d': d, 'number': number })
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")

@login_required
def maillist_maintain_export(request, list_id):
    lobj = ExtList.objects.get(id=list_id)
    lists = [[u'邮箱地址', u'权限']]
    file_name = u'邮件列表地址({})-{}'.format(lobj.address, datetime.datetime.now().strftime('%Y%m%d'))
    if not lobj.is_everyone:
        lists2 = ExtListMember.objects.filter(list_id=list_id)
        for d in lists2:
            lists.append([d.address, d.get_permit_display()])
    return ExcelResponse(lists, file_name, encoding='gbk')
