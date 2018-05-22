
# coding=utf-8
import json
import re

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.db.models import Q, query
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template.response import TemplateResponse

from models import SenderCreditSettings, SenderCredit, SenderCreditLog
from forms import SenderCreditBaseSearchForm, SenderCreditSettingsForm, SenderCreditForm

@login_required
def sender_credit_settings(request):
    settings = SenderCreditSettings.objects.all()
    if settings:
        form = SenderCreditSettingsForm(instance=settings[0])
    else:
        form = SenderCreditSettingsForm()
    if request.method == "POST":
        if settings:
            form = SenderCreditSettingsForm(request.POST, instance=settings[0])
        else:
            form = SenderCreditSettingsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('csender_credit_settings'))
    return render_to_response("collect_mail/sender_credit_settings.html", {
        'form': form,
    }, context_instance=RequestContext(request))

def _get_sender_credit_data(data, flag=False):
    sender = data.get('sender', False)
    if flag:
        lists = SenderCredit.objects.all()
        if sender:
            lists = lists.filter(sender__icontains=sender)
    else:
        lists = SenderCreditLog.objects.all()
        if sender:
            lists = lists.filter(sender__icontains=sender)
    return lists

@login_required
def sender_credit(request):
    data = request.GET
    form = SenderCreditBaseSearchForm(data)
    lists = _get_sender_credit_data(data, flag=True)
    try:
        count = lists.count()
    except:
        count = len(lists)

    return render_to_response('collect_mail/sender_credit.html',{
        'form': form,
        'count': count,
    }, context_instance=RequestContext(request))

@login_required
def ajax_get_sender_credit(request):
    data = request.GET
    lists = _get_sender_credit_data(data, flag=True)
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    if search:
        lists = lists.filter( Q(sender__icontains=search) )

    colums = ['id', 'sender', 'credit', 'update_time', 'id']

    if isinstance(lists, query.QuerySet) and order_column and int(order_column) < len(colums):
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

    try:
        count = lists.count()
    except:
        count = len(lists)

    paginator = Paginator(lists, length)

    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    for m in lists.object_list:
        t = TemplateResponse(request, 'collect_mail/ajax_get_sender_credit.html', {'d': m})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

@login_required
def sender_credit_modify(request, sender_credit_id):
    obj = SenderCredit.objects.get(id=sender_credit_id)
    form = SenderCreditForm(instance=obj)
    if request.method == 'POST':
        form = SenderCreditForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('csender_credit'))
    return render_to_response("collect_mail/sender_credit_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def ajax_update_sender_credit(request):
    mail_from = request.GET.get('mail_from', '').lower()
    refreash_credit = int(request.GET.get('credit', 0))
    obj, bool = SenderCredit.objects.get_or_create(sender=mail_from)
    if bool:
        credit = 1000 + refreash_credit
    else:
        credit = obj.credit + refreash_credit
    obj.credit = credit
    obj.save()
    return HttpResponse(json.dumps({'msg': credit}), content_type="application/json")

@login_required
def sender_credit_log(request):
    data = request.GET
    form = SenderCreditBaseSearchForm(data)
    sender = data.get('sender', False)
    lists = SenderCreditLog.objects.filter(sender__icontains=sender)
    #lists = _get_sender_credit_data(data, flag=False)
    try:
        count = lists.count()
    except:
        count = len(lists)

    return render_to_response('collect_mail/sender_credit_log.html',{
        'form': form,
        'count': count,
    }, context_instance=RequestContext(request))

@login_required
def ajax_get_sender_credit_log(request):
    data = request.GET
    lists = _get_sender_credit_data(data, flag=False)
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    if search:
        lists = lists.filter( Q(sender__icontains=search) )

    colums = ['id', 'sender', 'mail_id', 'expect_value', 'value', 'reason', 'create_time', 'id']

    if isinstance(lists, query.QuerySet) and order_column and int(order_column) < len(colums):
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

    try:
        count = lists.count()
    except:
        count = len(lists)

    paginator = Paginator(lists, length)

    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    for m in lists.object_list:
        t = TemplateResponse(request, 'collect_mail/ajax_get_sender_credit_log.html', {'d': m})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")
