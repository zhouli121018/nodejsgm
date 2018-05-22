# coding=utf-8
import re
import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db import connections
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.translation import ugettext_lazy as _

from lib.common import get_object
from lib.tools import valid_domain
from lib.parse_email import ParseEmail
from app.core.models import MailBox, CustomerMailbox, CustomerTrackDomain, SysPicDomain,CustomerDomainMailboxRel
from app.address.models import MailList
from app.task.models import SendTask, SendContent
from app.trigger.models import Trigger
from app.task.utils import caches as task_caches, tools as task_tools, contexts as task_contexts, posts as task_posts
from app.template.utils import templates
from app.task.forms import TaskExportForm
from django_redis import get_redis_connection

# #########  邮件任务管理 ##########
# 任务列表视图
@login_required
def task_list(request):
    isvalid = request.GET.get('isvalid', '')
    if request.method == "POST":
        id = request.POST.get('id', False)
        ids = (request.POST.get('ids', False)).split(',')
        status = int(request.POST.get('status', False))
        if id:
            obj = SendTask.objects.get(id=id, user=request.user)
            if obj.send_status in [3, -3, 4] and status in [2, -2]:
                msg = _(u'状态改变失败')
                messages.add_message(request, messages.ERROR, msg)
                return HttpResponseRedirect('/task/?isvalid={}'.format(isvalid))
            elif status == -4:  # 恢复任务
                obj.isvalid = True
                obj.save()
                msg = _(u'恢复任务（%(send_name)s）成功') % {'send_name': obj.send_name}
            elif status == -3:  # 单个删除
                if obj.send_status == 2:
                    msg = _(u'删除失败，正在发送中的任务不能删除，请先暂停！')
                    messages.add_message(request, messages.ERROR, msg)
                    return HttpResponseRedirect('/task/?isvalid={}'.format(isvalid))
                else:
                    SendTask.objects.exclude(send_status=2).filter(id=id).update(isvalid=False)
                    msg = _(u'成功删除')
            elif status == -2:
                if obj.send_status != -2: # 已经暂停，则不重复暂停
                    obj.send_status = status
                    obj.save()
                    obj.stop()
                msg = _(u'成功暂停')
            elif status == 2:
                if obj.send_status != 2: # 正在发送则不在重复启动
                    obj.send_status = status
                    obj.save()
                    obj.start()
                msg = _(u'成功启动')
        if ids:
            if status == -10:  # 批量删除
                SendTask.objects.exclude(send_status=2).filter(id__in=ids).update(isvalid=False)
                msg = _(u'成功删除')
            if status == -99:  # 点击打开地址池导出
                open_or_click = request.POST.get("export_open_or_click_task", "open")
                is_new_maillist = int(request.POST.get("export_is_new_maillist_task", "0"))
                maillist_name = request.POST.get("export_maillist_name_task", "").strip()
                maillist_id = request.POST.get("export_maillist_id_task", "")
                task_idents = list(SendTask.objects.filter(id__in=ids, user=request.user).values_list("send_name", flat=True))
                open_or_click = 'open' if open_or_click=='open' else 'click'
                if not task_idents:
                    messages.add_message(request, messages.ERROR, msg = _(u'选择的任务不存在，请重新选择'))
                    return HttpResponseRedirect('/task/?isvalid={}'.format(isvalid))
                if is_new_maillist==0 and not maillist_id:
                    messages.add_message(request, messages.ERROR, msg = _(u'没有选择相应的地址池'))
                    return HttpResponseRedirect('/task/?isvalid={}'.format(isvalid))
                if is_new_maillist==0 and maillist_id and not MailList.objects.filter(customer=request.user, id=maillist_id).exists():
                    messages.add_message(request, messages.ERROR, msg = _(u'没有选择相应的地址池'))
                    return HttpResponseRedirect('/task/?isvalid={}'.format(isvalid))
                if is_new_maillist==1 and not maillist_name:
                    maillist_name = u"打开/点击地址"

                redis = get_redis_connection()
                redis.lpush(":edmweb:export:task:addrs:click_or_open:", json.dumps([
                    open_or_click, is_new_maillist, maillist_name, maillist_id, task_idents, request.user.id
                ]))
                msg = _(u'成功导出地址，请前往地址池查看（可能须等待5-30秒不等）')

        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect('/task/?isvalid={}'.format(isvalid))
    form = TaskExportForm(request.user)
    return render(request, 'task/task_list.html', context={
        'isvalid': isvalid, "form": form})


# ajax 加载任务列表
@login_required
def ajax_task_list(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    isvalid = data.get('isvalid', '')
    task_date = data.get('task_date', '').strip()
    lists = SendTask.objects.filter(user=request.user)
    if not request.session.get('is_admin', False):
        lists = lists.filter(is_shield=False)
    if isvalid == '1':
        lists = lists.filter(isvalid=True)
    elif isvalid == '2':
        lists = lists.filter(isvalid=False)
    if task_date:
        date_start = '{} 00:00:00'.format(task_date)
        date_end = '{} 23:59:59'.format(task_date)
        lists = lists.filter(send_time__gte=date_start).filter(send_time__lte=date_end)
    if search:
        send_list = SendContent.objects.filter(user=request.user, template_name__icontains=search).values_list('send', flat=True)
        lists = lists.filter(Q(send_name__icontains=search) | Q(id__in=send_list))
        # lists = lists.filter(send_name__icontains=search)

    colums = ['id', 'id', 'send_name', 'send_template_id', 'send_maillist_id', 'send_status', 'created']

    if order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            lists = lists.order_by('-%s' % colums[int(order_column)])
        else:
            lists = lists.order_by('%s' % colums[int(order_column)])
    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1
    length = min(length, 25)

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
        t = TemplateResponse(request, 'task/ajax_task_list.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

# 任务暂停 检测
@csrf_exempt
@login_required
def ajax_pause_task(request, task_id):
    msg = {'msg': 'N'}
    try:
        obj = SendTask.objects.get(user=request.user, pk=task_id)
    except:
        return HttpResponse(json.dumps(msg), content_type="application/json")
    if obj.send_status in [2, -5]:
        return HttpResponse(json.dumps({'msg': 'Y'}), content_type="application/json")
    return HttpResponse(json.dumps(msg), content_type="application/json")


# 任务增加
@login_required
def task_add(request):
    # 是否为审核用户
    custQtyValid, is_service_disabled = task_contexts.get_user_service(request)
    if request.method == "POST":
        return task_posts.post_task_add(request, is_service_disabled)
    context = task_contexts.get_task_add_context(request)
    context.update({ 'custQtyValid': custQtyValid, 'is_service_disabled': is_service_disabled,})
    return render(request, "task/task_add.html", context=context)


# 获取下一个模板
@csrf_exempt
@login_required
def ajax_load_template(request):
    return templates.get_next_templates(request)

# 任务修改
@login_required
def task_modify(request, task_id):
    obj = get_object(SendTask, request.user, task_id)
    if obj.send_status in [2, 3, 4]:
        raise Http404
    custQtyValid, is_service_disabled = task_contexts.get_user_service(request)
    if request.method == "POST":
        return task_posts.post_task_modify(request, task_id, is_service_disabled)
    context = task_contexts.get_task_modify_context(request, task_id)
    context.update({
        'task_obj': obj,
        'c_send_maillist_ids': task_tools.get_modify_maillistid(obj),
        'custQtyValid': custQtyValid,
        'is_service_disabled': is_service_disabled,
    })
    return render(request, 'task/task_modify.html', context=context)


# 任务查看
@login_required
def task_view(request, task_id):
    obj = get_object(SendTask, request.user, task_id)
    # template_objs = SendTemplate.objects.filter(user=request.user, name__isnull=False)
    # template_ids = SendTaskTpl.objects.filter(task_id=task_id).values_list('template_id', flat=True)
    template_objs = SendContent.objects.filter(send_id=task_id, isvalid=True)
    return render(request, 'task/task_view.html', {
        'task_obj': obj,
        'template_objs': template_objs,
        # 'template_ids': template_ids,
    })


@csrf_exempt
@login_required
def ajax_get_maillist_count(request):
    data = request.GET
    list_id = int(data.get('list_id', 0))
    cr = connections['mm-pool'].cursor()
    tablename = 'ml_subscriber_' + str(request.user.id)
    sql = "SELECT COUNT(1) FROM %s WHERE list_id=%d;" % (tablename, list_id)
    cr.execute(sql)
    data = cr.fetchone()
    count = data[0] if data else 0
    return HttpResponse(json.dumps({'count': count}), content_type="application/json")

@csrf_exempt
@login_required
def ajax_get_maillist_trigger(request):
    data = request.GET
    list_id = int(data.get('list_id', 0))
    task_id = data.get('task_id', None)
    cr = connections['mm-pool'].cursor()
    tablename = 'ml_subscriber_' + str(request.user.id)
    sql = "SELECT COUNT(1) FROM %s WHERE list_id=%d;" % (tablename, list_id)
    cr.execute(sql)
    data = cr.fetchone()
    count = data[0] if data else 0

    # 获取 关联的触发器
    html = ''
    trigger_ids = []
    if task_id:
        task_obj = SendTask.objects.filter(id=task_id).first()
        trigger_ids = task_obj.trigger_set.filter(status='enable').values_list("id", flat=True)
    lists = Trigger.getTriggerBylist(request.user.id, list_id, type='open')
    if lists:
        t = TemplateResponse(request, 'task/trigger.html', {'lists': lists, 'task_id': task_id, 'trigger_ids': trigger_ids,})
        t.render()
        html = t.content
    return HttpResponse(json.dumps({'count': count, 'html': html}), content_type="application/json")

from collections import defaultdict
@csrf_exempt
@login_required
def ajax_get_maillistcount_and_triggers(request):
    data = request.GET
    list_ids = data.get('list_ids', "0")
    task_id = data.get('task_id', None)
    lists = MailList.objects.filter(
        Q(customer=request.user) |  Q(sub_share_maillist__user=request.user)).filter(
        id__in=map(int, list_ids.split(","))).values_list("id", "customer_id", "count_real")
    count = 0
    index = 0
    html = ''
    user_ids = defaultdict(list)
    for list_id, customer_id, count_real in lists:
        user_ids[customer_id].append(list_id)
        index += 1
        count += count_real
    # cr = connections['mm-pool'].cursor()
    # for customer_id, listids in user_ids.items():
    #     tablename = 'ml_subscriber_' + str(customer_id)
    #     sql = "SELECT COUNT(1) FROM {} WHERE list_id IN ({});".format(tablename, ",".join(map(str, listids)))
    #     cr.execute(sql)
    #     data = cr.fetchone()
    #     c = data[0] if data else 0
    #     MailList
    #     count += c
    #     index += 1
    if index==1 and user_ids.keys()[0] == request.user.id:
        # 获取 关联的触发器
        trigger_ids = []
        if task_id:
            task_obj = SendTask.objects.filter(id=task_id).first()
            trigger_ids = task_obj.trigger_set.filter(status='enable').values_list("id", flat=True)
        lists = Trigger.getTriggerBylistids(request.user.id, list_ids.split(","), type='open')
        if lists:
            t = TemplateResponse(request, 'task/trigger.html', {'lists': lists, 'task_id': task_id, 'trigger_ids': trigger_ids,})
            t.render()
            html = t.content
    return HttpResponse(json.dumps({'count': count, 'html': html}), content_type="application/json")

@csrf_exempt
@login_required
def ajax_get_mailbox(request):
    data = request.GET
    domain = data.get('domain', '')
    data = list(MailBox.objects.filter(
        customer=request.user, domain=domain, disabled='0'
    ).exclude(mailbox__isnull=True).values_list('mailbox', flat=True))
    if not data:
        ctype = CustomerDomainMailboxRel.objects.get_content_type('mailbox')
        box_ids = CustomerDomainMailboxRel.objects.filter(customer=request.user, content_type=ctype).values_list(
            'object_id', flat=True)
        data = list(CustomerMailbox.objects.filter(
            customer=request.user.parent, domain=domain, disabled='0', id__in=box_ids
        ).exclude(mailbox__isnull=True).values_list('mailbox', flat=True))
    return HttpResponse(json.dumps({'json_list': data}), content_type="application/json")


@login_required
def ajax_stat_info(request, task_id):
    obj = get_object(SendTask, request.user, task_id)
    flag = obj.get_track_stat_flag()
    show_stat_rate, show_link_rate = obj.get_rate()
    if obj.track_status == 1:
        if flag:
            info = _(u'''<span class="text-nowrap">打开率：
            <span class="myself-txt-color-red margin-right-5">%(rate)s</span>
            <code><a href="/track/trackstat/?ident=%(send_name)s&mode=1" target="_blank">查看详情</a></code>
            </span>''') % {'rate': show_stat_rate, 'send_name': obj.send_name}
        else:
            info = _(u'暂无数据') % {}
    elif obj.track_status == 2:
        if flag:
            info = _(u'''<span class="text-nowrap">打开率：
            <span class="myself-txt-color-red">%(rate)s</span></span><br>
            <span class="text-nowrap">点击率：
            <span class="myself-txt-color-blue margin-right-5">%(link_rate)s</span>
            <code><a href="/track/trackstat/?ident=%(send_name)s&mode=2" target="_blank">查看详情</a></code>
            </span>''') % {'rate': show_stat_rate, 'link_rate': show_link_rate, 'send_name': obj.send_name}
        else:
            info = _(u'暂无数据') % {}
    else:
        info = _(u'未启用') % {}
    return HttpResponse(json.dumps({'info': info}), content_type="application/json")


@login_required
def ajax_template_info(request, task_id):
    obj = get_object(SendTask, request.user, task_id)
    html = obj.show_template_list()
    return HttpResponse(json.dumps({'info': html}), content_type="application/json")


@login_required
def ajax_stat_success_info(request, task_id):
    obj = get_object(SendTask, request.user, task_id)
    info = obj.show_stat_success_info()
    return HttpResponse(json.dumps({'info': info}), content_type="application/json")


@login_required
def ajax_check_track_domain(request):
    domain = request.GET.get('domain', '')
    if domain in ['comingchina.com', 'magvision.com', 'bestedm.org']:
        return HttpResponse(json.dumps({'res': 'M'}), content_type="application/json")
    r = re.compile(r'.*?(\.comingchina.com|\.magvision.com|\.bestedm.org)$')
    if r.search(domain):
        return HttpResponse(json.dumps({'res': 'M'}), content_type="application/json")
    r = valid_domain(domain, 'cname', record='count1.bestedm.org') or valid_domain(domain, 'cname',
                                                                                   record='count.bestedm.org')
    res = 'success' if r else 'fail'
    return HttpResponse(json.dumps({'res': res}), content_type="application/json")


# 预览模板内容
@login_required
def task_preview(request, content_id):
    obj = get_object(SendContent, request.user, content_id)
    p = ParseEmail(obj.send_content)
    m = p.parseMailTemplate()
    text = m.get('html_text', '')
    charset = m.get('html_charset', '')
    if not text:
        text = m.get('plain_text', '')
        charset = m.get('plain_charset', '')
    return HttpResponse(text, charset=charset)


# 缓存最近10个任务
def ajax_cache_latest_task(request):
    return HttpResponse(json.dumps({"content":task_caches.cache_latest_task(request)}), content_type="application/json")
