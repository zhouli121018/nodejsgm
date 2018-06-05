# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import json
from app.utils.domain_session import get_domainid_bysession


from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template.response import TemplateResponse
from app.core.models import Mailbox, Domain, MailboxUser, Department
from app.maillist.models import ExtList
from app.utils.dept import display2


from forms import MailboxForm, MailboxUserForm


@login_required
def account(request, template_name='mailbox/emailAccounts.html'):
    return render(request, template_name=template_name, context={
    })

@login_required
def add_account(request, template_name='mailbox/add_account.html'):
    domain_id = get_domainid_bysession(request)
    domain = Domain.objects.get(id=domain_id)
    form = MailboxForm(domain)
    user_form = MailboxUserForm(domain)
    if request.method == 'POST':
        print request.POST
        form = MailboxForm(domain, request.POST)
        user_form = MailboxUserForm(domain, request.POST)
        if form.is_valid() and user_form.is_valid():
            obj = form.save()
            user_form.save(obj.id)
    depts = Department.objects.filter(parent_id=-1)
    dept_list = display2(depts)
    mail_list = ExtList.objects.filter(domain_id=domain_id).order_by('-id')
    return render(request, template_name=template_name, context={
        'form': form,
        'domain': domain,
        'user_form': user_form,
        'dept_list': dept_list,
        'mail_list': mail_list,
    })

@login_required
def batchadd_account(request, template_name='mailbox/batchadd_account.html'):
    return render(request, template_name=template_name, context={
    })

@login_required
def batchedit_account(request, template_name='mailbox/batchedit_account.html'):
    return render(request, template_name=template_name, context={
    })

@login_required
def delete_account(request, template_name='mailbox/delete_account.html'):
    return render(request, template_name=template_name, context={
    })

@login_required
def backup_account(request, template_name='mailbox/backup_account.html'):
    return render(request, template_name=template_name, context={
    })

@login_required
def edit_account(request, id, template_name='mailbox/edit_account.html'):
    domain_id = get_domainid_bysession(request)
    domain = Domain.objects.get(id=domain_id)
    obj = Mailbox.objects.get(id=id)
    user = MailboxUser.objects.get(id=id)
    form = MailboxForm(domain, instance=obj)
    user_form = MailboxUserForm(domain, instance=user)
    return render(request, template_name=template_name, context={
        'obj': obj,
        'form': form,
        'user': user,
        'user_form': user_form
    })

@login_required
def ajax_get_account(request):
    domain_id = get_domainid_bysession(request)
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'id', 'domain', 'name']
    lists = Mailbox.objects.filter(domain_id=domain_id)
    if search:
        lists = lists.filter(mailbox__mailbox__icontains=search)

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
    for l in lists.object_list:
        t = TemplateResponse(request, 'mailbox/ajax_get_account.html', {'l': l, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")

@login_required
def reply(request, id, template_name='mailbox/reply.html'):
    obj = Mailbox.objects.get(id=id)
    return render(request, template_name=template_name, context={
        'obj': obj
    })

@login_required
def forward(request, id, template_name='mailbox/forward.html'):
    obj = Mailbox.objects.get(id=id)
    return render(request, template_name=template_name, context={
        'obj': obj
    })
