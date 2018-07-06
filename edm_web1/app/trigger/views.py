# coding=utf-8
import re
import json

from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import reverse
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.template.response import TemplateResponse

# from app.trigger.utils import const
from app.address.models import MailList
from app.template.models import SendTemplate
from app.trigger.models import Trigger, TriggerAction, TriggerTask, TriggerListShip
from app.trigger.forms import TriggerForm, TriggerActionForm
from lib.common import get_object



@login_required
def trigger(request):
    if request.method == "POST":
        action = request.POST.get('action', '')
        id = request.POST.get('id', '')
        if action == 'delete':
            Trigger.objects.filter(customer=request.user, id=id).delete()
        elif action == 'delete_action':
            TriggerAction.objects.filter(trigger__customer=request.user, id=id).delete()
        messages.add_message(request, messages.SUCCESS, _(u'删除成功'))
        return HttpResponseRedirect(reverse('trigger'))
    lists = Trigger.objects.filter(customer=request.user).order_by('-created')
    return render(request, 'trigger/trigger.html', context={
        'lists': lists
    })


@login_required
def trigger_add(request):
    form = TriggerForm(request.user)
    action_form = TriggerActionForm(request.user)

    if request.method == "POST":
        data = json.loads(request.POST.get('data', ''))
        """
        {u'action': [{u'action_schedule': u'0',
                             u'action_time': u'',
                             u'con_holiday': u'',
                             u'con_url': u'',
                             u'condition': u'open',
                             u'replyto': u'',
                             u'send_acct_address': u'all',
                             u'send_acct_domain': u'all',
                             u'sendname': u'',
                             u'template': u'163329',
                             u'time-type': u'min'}],
                u'end_time': u'',
                u'expire_type': u'forever',
                u'maillist_type': u'part',
                u'name': u'11',
                u'start_time': u'',
                u'status': u'enable',
                u'trigger_maillists': [u'241386'],
                u'type': u'open'}
        """
        mailists = data.get('trigger_maillists', [])
        actions = data.get('action', [])
        t_obj = Trigger()
        t_obj.customer = request.user
        for k, v in data.iteritems():
            if not v:
                continue
            if k in ['end_time', 'expire_type', 'maillist_type', 'name', 'start_time', 'status', 'type']:
                setattr(t_obj, k, v)
        t_obj.save()
        if mailists:
            for m in mailists:
                TriggerListShip.objects.create(trigger=t_obj, maillist=MailList.objects.get(id=m, customer=request.user))
        if actions:
            for a in actions:
                act_obj = TriggerAction()
                act_obj.trigger = t_obj
                for k, v in a.iteritems():
                    if not v:
                        continue
                    try:
                        setattr(act_obj, k, v)
                    except BaseException, e:
                        pass
                act_obj.save()
        messages.add_message(request, messages.SUCCESS, _(u'添加成功'))
        return HttpResponse(json.dumps({'msg': u'添加成功'}, ensure_ascii=False), content_type="application/json")
    return render(request, 'trigger/trigger_add.html', context={
        "form": form,
        "action_form": action_form,
        "action_forms": [action_form],
        "trig_title": _(u'添加触发器'),
    })


@login_required
def trigger_show(request, trig_id):
    obj = get_object(Trigger, request.user, trig_id)
    form = TriggerForm(request.user, instance=obj)
    for field in form.visible_fields():
        field.field.widget.attrs['disabled'] = 'disabled'
    action_forms = []
    for action in obj.trigger_action.all():
        action_form = TriggerActionForm(request.user, instance=action)
        for field in action_form.visible_fields():
            field.field.widget.attrs['disabled'] = 'disabled'
        action_forms.append(action_form)
    return render(request, 'trigger/trigger_show.html', context={
        "form": form,
        "action_forms": action_forms,
        "trig_title": _(u'显示触发器'),
    })


@login_required
def trigger_modify(request, trig_id):
    t_obj = get_object(Trigger, request.user, trig_id)
    form = TriggerForm(request.user, instance=t_obj)
    action_form = TriggerActionForm(request.user)
    form.fields['type'].widget.attrs['disabled'] = 'disabled'
    action_forms = []
    for action in t_obj.enable_trigger_action():
        f = TriggerActionForm(request.user, instance=action)
        action_forms.append(f)

    if request.method == "POST":
        data = json.loads(request.POST.get('data', ''))
        mailists = data.get('trigger_maillists', [])
        actions = data.get('action', [])
        for k, v in data.iteritems():
            if not v:
                continue
            if k in ['end_time', 'expire_type', 'maillist_type', 'name', 'start_time', 'status', 'type']:
                setattr(t_obj, k, v)
        t_obj.save()
        TriggerListShip.objects.filter(trigger=t_obj).delete()
        if mailists:
            for m in mailists:
                TriggerListShip.objects.create(trigger=t_obj, maillist=MailList.objects.get(id=m, customer=request.user))
        if actions:
            t_obj.trigger_action.update(status='delete')
            for a in actions:
                act_obj = TriggerAction()
                act_obj.trigger = t_obj
                for k, v in a.iteritems():
                    if not v:
                        continue
                    try:
                        setattr(act_obj, k, v)
                    except BaseException, e:
                        pass
                act_obj.save()
        messages.add_message(request, messages.SUCCESS, _(u'修改成功'))
        return HttpResponse(json.dumps({'msg': u'修改成功'}, ensure_ascii=False), content_type="application/json")
    return render(request, 'trigger/trigger_add.html', context={
        "form": form,
        "action_form": action_form,
        "action_forms": action_forms,
        "trig_title": _(u'修改触发器'),
    })


@login_required
def trigger_action_add(request, trig_id):
    trigobj = get_object(Trigger, request.user, trig_id)
    form = TriggerForm(request.user, instance=trigobj)
    action_form = TriggerActionForm(request.user)
    for field in form.visible_fields():
        field.field.widget.attrs['disabled'] = 'disabled'
    if request.method == "POST":
        action_form = TriggerActionForm(request.user, request.POST)
        if action_form.is_valid():
            action_obj = action_form.save()
            action_obj.trigger = trigobj
            action_obj.save()
            messages.add_message(request, messages.SUCCESS, _(u'添加触发器成功'))
            next = request.POST.get('next', '')
            if next == 'add':
                return HttpResponseRedirect(reverse('trigger_action_add', args=(trigobj.id,)))
            return HttpResponseRedirect(reverse("trigger"))
    return render(request, 'trigger/trigger_add.html', context={
        "form": form,
        "action_form": action_form,
        "trig_title": _(u'添加触发动作'),
    })


@login_required
def trigger_action_modify(request, trig_id, action_id):
    trigobj = get_object(Trigger, request.user, trig_id)
    obj = TriggerAction.objects.get(id=action_id)
    form = TriggerForm(request.user, instance=trigobj)
    action_form = TriggerActionForm(request.user, instance=obj)
    for field in form.visible_fields():
        field.field.widget.attrs['disabled'] = 'disabled'
    if request.method == "POST":
        data = json.loads(request.POST.get('data', ''))

    return render(request, 'trigger/trigger_add.html', context={
        "form": form,
        "action_form": action_form,
        "trig_title": _(u'修改触发器动作'),
    })


@login_required
def ajax_trigger_task(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'id', 'name', 'name', 'trigger', 'create_time', 'create_time', 'create_time']
    lists = TriggerTask.objects.filter(customer=request.user)
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
    number = length * (page - 1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'trigger/ajax_trigger_task.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def trigger_task(request):
    return render(request, 'trigger/trigger_task.html', context={
    })


@login_required
def ajax_trigger_task_one(request, task_id):
    obj = get_object(TriggerTask, request.user, task_id)
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'id', 'email', 'trigger_action', 'trigger_action', 'status', 'create_time', 'action_time']
    lists = obj.triggertaskone_set.all()
    if search:
        lists = lists.filter(email__icontains=search)

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
        t = TemplateResponse(request, 'trigger/ajax_trigger_task_one.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def trigger_task_one(request, task_id):
    obj = get_object(TriggerTask, request.user, task_id)
    return render(request, 'trigger/trigger_task_one.html', context={
        'obj': obj
    })

# 预览或下载eml
@login_required
def template_preview(request, template_id):
    obj = get_object(SendTemplate, request.user, template_id)
    if obj.content_type == 1:
        charset = obj.character if obj.character else 'utf-8'
        return render(request, 'trigger/template_preview.html', context={
            'content': obj.content,
            'charset': charset
        })
    elif obj.content_type == 2:
        response = HttpResponse(obj.content.replace("\r\n", "\n"), content_type='text/html')
        response['Content-Disposition'] = 'attachment; filename="eml.eml"'
        return response

