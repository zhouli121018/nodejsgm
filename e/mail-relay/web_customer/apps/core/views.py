# coding=utf-8
import json
import re
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template.response import TemplateResponse
from apps.core.models import Notification, CoreLog, ACTION_TYPE
from forms import CustomerForm, OperateLogSearchForm

from django.utils.translation import ugettext_lazy as _


@login_required
def customer_modify(request):
    form = CustomerForm(instance=request.user)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, _(u'信息修改成功'))
            return HttpResponseRedirect(reverse('home'))
    return render_to_response("core/customer_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def customer_password_modify(request):
    form = PasswordChangeForm(user=request.user)
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, _(u'信息修改成功'))
            return HttpResponseRedirect(reverse('home'))
    return render_to_response("core/customer_password_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def notice_list(request):
    notices = Notification.objects.filter(customer=request.user)
    id = request.GET.get('id', '')
    ajax = request.GET.get('ajax', '')
    if id:
        notices = notices.filter(id=id)
        if notices:
            n = notices[0]
            if not n.is_read:
                n.is_read = True
                n.save()
    if request.method == "POST":
        action = request.POST.get('action', '')
        if action == 'delete':
            id = request.POST.get('id', '')
            if id:
                Notification.objects.filter(customer=request.user, id=id).delete()
                messages.add_message(request, messages.SUCCESS, _(u'删除成功'))
                return HttpResponseRedirect(reverse('notice_list'))
    if ajax:
        return HttpResponse(json.dumps({}, ensure_ascii=False), content_type="application/json")
    else:
        return render_to_response("core/notice_list.html", {
            'notices': notices,
        }, context_instance=RequestContext(request))

def get_notices(data, user):
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    type = data.get('type', '')
    id = data.get('id', '')
    notices = Notification.objects.filter(customer=user)
    if id:
        notices = notices.filter(id=id)
    if search:
        notices = notices.filter(
            Q(subject__icontains=search) | Q(content__icontains=search))

    colums = ['id', 'subject', 'content', 'is_sms', 'is_email', 'created', 'id']

    if notices and order_column and int(order_column) < len(colums):
        col_name = colums[int(order_column)]
        if order_dir == 'desc':
            notices = notices.order_by('-%s' % col_name)
        else:
            notices = notices.order_by('%s' % col_name)

    return notices

@login_required
def ajax_get_notices(request):
    data = request.GET
    notices = get_notices(data, request.user)

    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        page = int(data.get('start', '0')) / length + 1
    except ValueError:
        page = 1

    count = len(notices)

    paginator = Paginator(notices, length)

    try:
        notices = paginator.page(page)
    except (EmptyPage, InvalidPage):
        notices = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    for n in notices.object_list:
        t = TemplateResponse(request, 'core/ajax_get_notices.html', {'n': n, 'type': type})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

###  操作日志列表  ###
@login_required
def operate_log(request):
    form = OperateLogSearchForm(request.GET)
    return render_to_response("core/operate_log.html", {
        'form': form
    }, context_instance=RequestContext(request))


@login_required
def ajax_operate_log(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    action = data.get('action', '')
    date_start = data.get('date_start', '')
    date_end = data.get('date_end', '')
    colums = ['id', 'action', 'datetime', 'desc', 'customer', 'ip']
    lists = CoreLog.objects.filter(customer=request.user)
    if action:
        lists = lists.filter(action=action)
    if date_start and date_end:
        lists = lists.filter(datetime__gte=date_start).filter(datetime__lte=date_end)
    elif date_start:
        lists = lists.filter(datetime__gte=date_start)
    elif date_end:
        lists = lists.filter(datetime__lte=date_end)
    if search:
        lists = lists.filter(desc__icontains=search)
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
        page = int(data.get('start', '0')) / length + 1
    except ValueError:
        page = 1

    count = len(lists)
    paginator = Paginator(lists, length)
    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page - 1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'core/ajax_operate_log.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")
