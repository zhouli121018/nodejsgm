# coding=utf-8
import re
import time
import json
import ast
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django_redis import get_redis_connection
# from django.utils.translation import ugettext_lazy as _

from app.statistics.configs import DATA_TYPES, AREA_CODE, COLOR_20, JC_CODE_COUNTRY, ERRTYPE_VALS
from app.task.models import SendTask
from app.track.models import StatTask, TrackStat, TrackLink, StatError
from app.statistics.utils.tools import get_realcustomer_and_obj
from app.statistics.utils import caches as statistics_caches, contexts as statistics_contexts
from lib.excel_response import ExcelResponse, DHeadExcelResponse, MultiSheetExcelResponse
from lib.common import get_object

# 统计客户地址池数量队列（python 专用）
EDM_WEB_USER_MAIL_IMPORT_COUNT_QUEUE = 'edm_web_user_mail_import_count_queue'

# 邮件发送统计总表
@login_required
def mail_statistics(request):
    context=statistics_contexts.mail_statistics_context(request)
    return render(request, 'statistics/mail_statistics.html', context=context)

@login_required
def ajax_mail_statistics(request):
    return statistics_caches.ajax_mail_statistics(request)

@login_required
def mail_statistics_export(request):
    date_start = request.GET.get('date_start', '')
    date_end = request.GET.get('date_end', '')
    if not date_start and not date_end:
        raise Http404
    user_id = request.GET.get('user_id', '').strip()
    user_id, subobj = get_realcustomer_and_obj(request, user_id)
    return statistics_caches.mail_statistics_export(user_id, date_start, date_end)

# 导出失败地址
@login_required
def export_fail_addr_statistics(request):
    data = request.GET
    errtype = data.get('errtype', '')
    errdate = data.get('errdate', '')
    task_name = data.get('task_name', '')
    user_id  = request.GET.get('user_id', '').strip()
    customer_id, subobj = get_realcustomer_and_obj(request, user_id)
    if errdate:
        lists = [(u'email',)] if request.user.lang_code == 'en-us' else [(u'邮箱地址',)]
        res = StatError.objects.filter(customer_id=customer_id, send_date=errdate).filter(
            error_type__in=errtype.split(',')).values_list('recipient')
        lists.extend(res)
        return ExcelResponse(lists, 'mail', encoding='gbk')
    if task_name:
        stats = StatTask.objects.filter(customer_id=customer_id, task_ident=task_name).values_list('id', flat=True)
        list = StatError.objects.filter(customer_id=customer_id, task_id__in=stats).order_by('id')
        errtype_list = errtype.split(',')
        lists = []
        for err in errtype_list:
            if err not in ERRTYPE_VALS: continue
            res = list.filter(error_type=err).values_list('recipient')
            count = res.count()
            sheetname = u'{}({})'.format(ERRTYPE_VALS[err], count)
            lists.append((sheetname, count, res))
        lists.sort(key=lambda x: x[1], reverse=True)
        max_count = lists[0][1] if lists else 0
        return MultiSheetExcelResponse(lists, max_count, 'mail', encoding='gbk')

# 邮件批次发送统计表
@login_required
def batch_statistics(request):
    action_type = request.GET.get('action_type', 'batch').strip()
    date_start = request.GET.get('date_start', '')
    date_end = request.GET.get('date_end', '')
    user_id  = request.GET.get('user_id', '').strip()
    customer_id, subobj = get_realcustomer_and_obj(request, user_id)
    return render(request, 'statistics/batch_statistics.html', context={
        'action_type': action_type,
        'date_start': date_start,
        'date_end': date_end,
        "subobj": subobj,
    })

@login_required
def ajax_batch_statistics(request):
    return statistics_caches.ajax_batch_statistics(request)

# 发件人发送统计表
@login_required
def sender_statistics(request):
    action_type = request.GET.get('action_type', 'sender').strip()
    date_start = request.GET.get('date_start', '')
    date_end = request.GET.get('date_end', '')
    user_id  = request.GET.get('user_id', '').strip()
    customer_id, subobj = get_realcustomer_and_obj(request, user_id)
    return render(request, 'statistics/sender_statistics.html', context={
        'action_type': action_type,
        'date_start': date_start,
        'date_end': date_end,
        "subobj": subobj,
    })

@login_required
def ajax_sender_statistics(request):
    return statistics_caches.ajax_sender_statistics(request)

@login_required
def ajax_clear_erraddr(request):
    customer_id = request.user.id
    action = request.POST.get('action', '')
    errtype = request.POST.get('errtype', '')
    date = request.POST.get('date', '')
    task_id = request.POST.get('task_id', '')
    if errtype == 'all' and checkDate(date):
        redis = get_redis_connection()
        redis.lpush(":edmweb:clear:erraddr:all:", json.dumps({
            "action": action,
            "task_id": task_id,
            "errtype": errtype,
            "date": date,
            "customer_id": customer_id,
        }))
    return HttpResponse(json.dumps({'msg': 'Y',}), content_type="application/json")

def checkDate(date, type="%Y-%m-%d"):
    try:
        time.strftime(type, time.strptime(date, type))
        return True
    except:
        return False

# 任务统计报告
@login_required
def mail_statistics_report(request, task_id):
    context = statistics_caches.mail_statistics_report_context(request, task_id)
    return render(request, 'statistics/mail_statistics_report.html', context=context)

@login_required
def ajax_mail_statistics_report(request, task_id):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')

    obj = get_object(SendTask, request.user, task_id)
    ident = obj.send_name
    stat_objs = TrackStat.objects.filter(task_ident=obj.send_name, customer_id=request.user.id)
    lists = TrackLink.objects.filter(track__in=stat_objs)

    colums = ['id', 'link', 'click_unique', 'click_total', 'click_first', 'click_last']

    if lists.exists() and order_column and int(order_column) < len(colums):
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
    for obj in lists.object_list:
        t = TemplateResponse(request, 'statistics/ajax_mail_statistics_report.html', {'obj': obj, 'number': number, 'ident': ident})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

@login_required
def world_mill_en(request):
    # country_data = eval(request.GET.get('country_data', '{}'))
    country_data = ast.literal_eval(request.GET.get('country_data', '{}'))
    country_max = int(request.GET.get('country_max', '0'))
    return render(request, 'statistics/world_mill_en.html', context={
        'country_data': country_data,
        'country_max': country_max,
    })

@login_required
def china_mill_zh(request):
    # area_data = eval(request.GET.get('area_data', '{}'))
    area_data = ast.literal_eval(request.GET.get('area_data', '{}'))
    area_max = int(request.GET.get('area_max', '0'))
    return render(request, 'statistics/china_mill_zh.html', context={
        'area_data': area_data,
        'area_max': area_max,
    })
