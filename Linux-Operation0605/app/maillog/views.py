# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import json
import time
import uuid
import random
from django.shortcuts import render
from django.contrib import messages
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.db.transaction import atomic
from django.db.models import Q
from django.db.models import Sum,Count
from django_redis import get_redis_connection
from app.core.models import Mailbox, MailboxUser, MailboxSize, DomainAttr, \
                                Domain, CoreMonitor, CoreAlias, \
                                Department, DepartmentMember, VisitLog, AuthLog
from app.maillog.models import  MailLog, LogReport, LogActive

from app.maillog.forms import  MailLogSearchForm, MailboxStatForm, ActiveUserStatForm

from app.core.constants import MAILBOX_SEND_PERMIT, MAILBOX_RECV_PERMIT

from lib import validators
from lib.tools import recursion_make_dir
from lib.licence import licence_required

@licence_required
def getDomainObj(request):
    domain_list = Domain.objects.all()
    domain = request.GET.get("d","")
    obj = None
    if domain:
        obj = domain_list.filter(domain=domain).first()
    else:
        obj = domain_list.first()
    return obj, domain_list

def add_condition( cond, q ):
    if not cond:
        return q
    return cond & q

def get_day(delta=0):
    if delta<0:
        return time.strftime('%Y-%m-%d %H:%M:%S')
    now = int(time.time())
    midnight = now - (now % 86400) + time.timezone
    premidnight = midnight- 86400*delta
    return time.strftime('%Y-%m-%d 00:00:00',time.localtime(premidnight))

def count_time(last_time):
    now = time.time()
    print "cost: %s s"%(round(now-last_time,3))
    return now

def download_excel(ws, filename):
    import xlwt,StringIO,os
    filedir="/usr/local/u-mail/app/data/data_netdisk_backup"
    recursion_make_dir(filedir)
    filepath="%s/%s"%(filedir,filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    ws.save(filepath)

    #返回文件给客户
    sio = StringIO.StringIO()
    ws.save(sio)
    sio.seek(0)
    response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s'%filename
    response.write(sio.getvalue())
    return response

@licence_required
def mailLogView(request):
    domain, domain_list = getDomainObj(request)
    form = MailboxStatForm(request.GET)
    return render(request, "maillog/maillog_home.html", context={
        "form": form,
        "domain_list": domain_list,
        "domain": domain,
    })

@licence_required
def mailLogList(request):
    domain, domain_list = getDomainObj(request)
    form = MailLogSearchForm(request.GET)
    return render(request, "maillog/maillog.html", context={
        "form": form,
        "domain_list": domain_list,
        "domain": domain,
    })

@licence_required
def ajax_maillog_list(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')

    log_type = data.get('type', '')
    start_time = data.get('start_time', '')
    end_time = data.get('end_time', '')
    username = data.get('username', '')
    send_mail = data.get('send_mail', '')
    recv_mail = data.get('recv_mail', '')
    max_attach = data.get('max_attach', '')
    min_attach = data.get('min_attach', '')
    senderip = data.get('senderip', '')
    rcv_server = data.get('rcv_server', '')
    text = data.get('text', '')

    start_time = "" if start_time=='None' else start_time
    end_time = "" if end_time=='None' else end_time

    colums = [
         'id', 'recv_time', 'mailbox_id', 'type', 'status', 'senderip',
         'rcv_server', 'send_mail', 'recv_mail', 'subject', 'attachment',
         'attachment_size',
         ]

    condition = None
    domain, domain_list = getDomainObj(request)
    if domain:
        condition = add_condition(condition, Q(domain_id=domain.id))

    if search:
        condition = add_condition(condition, Q(send_mail__icontains=search) | Q(recv_mail__icontains=search))
    if log_type:
        condition = add_condition(condition, Q(type=log_type))
    if username:
        condition = add_condition(condition, (Q(send_mail__icontains=username) | Q(recv_mail__icontains=username)))
    if send_mail:
        condition = add_condition(condition, Q(send_mail__icontains=send_mail))
    if recv_mail:
        condition = add_condition(condition, Q(recv_mail__icontains=recv_mail))
    if senderip:
        condition = add_condition(condition, Q(senderip__icontains=senderip))
    if rcv_server:
        condition = add_condition(condition, Q(rcv_server__icontains=rcv_server))
    if text:
        condition = add_condition(condition, Q(subject__icontains=text) | Q(attachment__icontains=text))

    #print ">>>>>>>>>>>>>>>condition is ",condition

    if start_time or end_time:
        q = None
        if start_time:
            q = add_condition(q,Q(recv_time__gte=start_time))
        if end_time:
            q = add_condition(q,Q(recv_time__lte=end_time))
        condition = add_condition(condition, q)
    if max_attach or min_attach:
        q = None
        if min_attach:
            min_attach = int(float(min_attach)*1024*1024)
            q = add_condition(q,Q(attachment_size__gte=min_attach))
        if max_attach:
            max_attach = int(float(max_attach)*1024*1024)
            q = add_condition(q,Q(attachment_size__lte=max_attach))
        condition = add_condition(condition, q)

    #每次查询只显示前10000结果
    max_show = 10000
    if condition:
        lists = MailLog.objects.filter( condition ).order_by("-recv_time")[:max_show]
    else:
        lists = MailLog.objects.all().order_by("-recv_time")[:max_show]

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

    count = len(lists)
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
        t = TemplateResponse(request, 'maillog/ajax_maillog_list.html', {'d': d, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1

    return HttpResponse(json.dumps(rs), content_type="application/json")

@licence_required
def mailLogMailboxStat(request):
    domain, domain_list = getDomainObj(request)
    form = MailboxStatForm(request.GET)
    return render(request, "maillog/mailbox_stat.html", context={
        "form": form,
        "domain_list": domain_list,
        "domain": domain,
    })

def maillogMailboxStatSearch(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')

    username = data.get('username', '')
    name = data.get('name', '')
    department = data.get('department', '')
    position = data.get('position', '')
    worknumber = data.get('worknumber', '')

    quota = data.get('quota', '')
    netdisk_quota = data.get('netdisk_quota', '')

    send_permit = data.get('send_permit', '')
    recv_permit = data.get('recv_permit', '')

    domain, domain_list = getDomainObj(request)
    q_domain = Q(domain_id=domain.id)
    condition_mailbox = q_domain
    condition_user = None
    condition_quota = None
    condition_netdiskquota = None

    id_list = []
    if name:
        condition_user = add_condition(condition_user, Q(realname__icontains=name))
    if worknumber:
        condition_user = add_condition(condition_user, Q(eenumber__icontains=worknumber))
    if condition_user:
        condition_user = add_condition(condition_user, q_domain)
        for obj in MailboxUser.objects.filter( condition_user ):
            id_list.append( obj.id )
        if not id_list:
            return [], 0, 1, 1

    if position or department:
        condition_dept = None
        condition_position = None
        dept_list = []

        if department:
            condition_dept = add_condition(condition_dept, Q(title__icontains=department))
            condition_dept = add_condition(condition_dept, q_domain)
            for obj in Department.objects.filter( condition_dept ):
                dept_list.append( obj.id )

        if position:
            condition_position = add_condition(condition_position, Q(position__icontains=position))
            condition_position = add_condition(condition_position, q_domain)
        else:
            condition_position = add_condition(condition_position, q_domain)

        q_dept = None
        for dept_id in dept_list:
            if q_dept:
                q_dept = q_dept | Q(dept_id=dept_id)
            else:
                q_dept = Q(dept_id=dept_id)

        condition_position = add_condition(q_dept, condition_position)
        q_box = None
        for mailbox_id in id_list:
            if q_box:
                q_box = q_box | Q(mailbox_id=mailbox_id)
            else:
                q_box = Q(mailbox_id=mailbox_id)
        condition_position = add_condition(q_box, condition_position)
        id_list = []
        for obj in DepartmentMember.objects.filter( condition_position ):
            id_list.append( obj.mailbox_id )

        if not id_list:
            return [], 0, 1, 1

    condition_mailbox = add_condition(condition_mailbox, q_domain)
    if username:
        condition_mailbox = add_condition(condition_mailbox, Q(name__icontains=username))
    if send_permit:
        condition_mailbox = add_condition(condition_mailbox, Q(limit_send=send_permit))
    if recv_permit:
        condition_mailbox = add_condition(condition_mailbox, Q(limit_recv=recv_permit))
    if quota:
        condition_mailbox = add_condition(condition_mailbox, Q(quota_mailbox=quota))
    if netdisk_quota:
        condition_mailbox = add_condition(condition_mailbox, Q(quota_netdisk=netdisk_quota))
    q_box = None
    for mailbox_id in id_list:
        if q_box:
            q_box = q_box | Q(id=mailbox_id)
        else:
            q_box = Q(id=mailbox_id)
    condition_mailbox = add_condition(q_box, condition_mailbox)
    mailbox_lists = Mailbox.objects.filter( condition_mailbox )

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
    return mailbox_lists, start_num, page, length

def cal_mailboxstat(number, d):
    send_permit_map = dict(MAILBOX_SEND_PERMIT)
    recv_permit_map = dict(MAILBOX_RECV_PERMIT)
    def get_send_permit(v):
        v = str(v)
        return send_permit_map.get(v,'-1')
    def get_recv_permit(v):
        v = str(v)
        return recv_permit_map.get(v,'-1')

    username = d.name
    name = d.name
    department = ""
    position = ""
    worknumber = ""

    sendpermit = get_send_permit(d.limit_send)
    recvpermit = get_recv_permit(d.limit_recv)
    quotamailbox = d.quota_mailbox
    quotanetdisk = d.quota_netdisk

    quotamailbox_used = 0

    obj_user = MailboxUser.objects.filter(id=d.id).first()
    if obj_user:
        name = obj_user.realname
        worknumber = obj_user.eenumber

    obj_member = DepartmentMember.objects.filter(mailbox_id=d.id).first()
    if obj_member:
        position = obj_member.position
        dept_id = obj_member.dept_id
        obj_dept = Department.objects.filter(id=dept_id).first()
        if obj_dept:
            department = obj_dept.title

    size_obj = MailboxSize.objects.filter(id=d.id).first()
    quotamailbox_used = 0 if not size_obj else size_obj.size

    obj = VisitLog.objects.filter(mailbox_id=d.id).order_by('-logintime').first()
    last_weblogin = obj.logintime.strftime('%Y-%m-%d %H:%M:%S') if obj else u"--"
    obj = AuthLog.objects.filter(user=d.mailbox,is_login=True).order_by('-time').first()
    last_clientlogin = obj.time.strftime('%Y-%m-%d %H:%M:%S') if obj else u"--"

    data = {
        'number': number,
        'username': username,
        'name': name,
        'department': department,
        'position': position,
        'worknumber': worknumber,
        'sendpermit': sendpermit,
        'recvpermit': recvpermit,
        'quotamailbox': quotamailbox,
        'quotamailbox_used': quotamailbox_used,
        'quotanetdisk': quotanetdisk,
        "last_weblogin": last_weblogin,
        "last_clientlogin": last_clientlogin,
    }
    return data

@licence_required
def ajax_mailLogMailboxStat(request):
    mailbox_lists, start_num, page, length = maillogMailboxStatSearch(request)
    count = len(mailbox_lists)
    if start_num >= count:
        page = 1
    paginator = Paginator(mailbox_lists, length)
    try:
        mailbox_lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        mailbox_lists = paginator.page(paginator.num_pages)
    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page-1) + 1
    MB = 1024*1024.0
    for d in mailbox_lists.object_list:
        data = cal_mailboxstat(number, d)
        t = TemplateResponse(request, 'maillog/ajax_mailbox_stat.html', data )
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1

    return HttpResponse(json.dumps(rs), content_type="application/json")

def dumpMailboxReportData(request):
    import xlwt,StringIO,os

    #创建workbook对象并设置编码
    ws = xlwt.Workbook(encoding='utf-8')
    w = ws.add_sheet(u'邮件收发统计',cell_overwrite_ok=True)
    w.write(0, 0, u"序号")
    w.write(0, 1, u"用户名称")
    w.write(0, 2, u"用户姓名")
    w.write(0, 3, u"部门")
    w.write(0, 4, u"职位")
    w.write(0, 5, u"工号")
    w.write(0, 6, u"发送权限")
    w.write(0, 7, u"接收权限")
    w.write(0, 8, u"邮箱容量（MB）")
    w.write(0, 9, u"网络硬盘容量（MB）")
    w.write(0, 10, u"已用邮箱容量（MB）")

    list_mailog = MailLog.objects.all()
    mailbox_lists, start_num, page, length  = maillogMailboxStatSearch(request)
    current_row = 1
    MB = 1024*1024.0
    for d in mailbox_lists:
        data = cal_mailboxstat(current_row, d)

        username = data["username"]
        name = data["name"]
        department = data["department"]
        position = data["position"]
        worknumber = data["worknumber"]
        sendpermit = data["sendpermit"]
        recvpermit = data["recvpermit"]
        quotamailbox = data["quotamailbox"]
        quotanetdisk = data["quotanetdisk"]
        quotamailbox_used = data["quotamailbox_used"]

        w.write(current_row, 0, current_row)
        w.write(current_row, 1, username)
        w.write(current_row, 2, name)
        w.write(current_row, 3, department)
        w.write(current_row, 4, position)
        w.write(current_row, 5, worknumber)
        w.write(current_row, 6, sendpermit)
        w.write(current_row, 7, recvpermit)
        w.write(current_row, 8, quotamailbox)
        w.write(current_row, 9, quotanetdisk)
        w.write(current_row, 10, quotamailbox_used)
        current_row += 1
    return download_excel(ws,"mailbox.xls")

@licence_required
def mailLogExportMailboxReport(request):
    return dumpMailboxReportData(request)

@licence_required
def mailLogActiveUserStat(request):
    def get_date_offset(domain_id):
        def get_daystart(delta=0):
            import time
            now = int(time.time())
            midnight = now - (now % 86400) + time.timezone
            premidnight = midnight- 86400*delta
            return time.strftime('%Y-%m-%d 00:00:00',time.localtime(premidnight))
        #end def

        save_days = 15
        obj = DomainAttr.objects.filter(domain_id=domain_id, type='webmail', item='sw_mail_log_save_day').first()
        if obj:
            save_days = int(obj.value)
        l = []
        for v in xrange(-1,save_days):
            if v == -1:
                l.append( (-1,"至今") )
                continue
            date_start = get_daystart(int(v))
            l.append( (v, '%s'%date_start ) )
        return tuple(l)
    #end get_date_offset

    domain, domain_list = getDomainObj(request)
    date_select = get_date_offset(domain.id)
    date_select2 = get_date_offset(domain.id)
    date_value = request.GET.get("date_select","0")
    date_value2 = request.GET.get("date_select2","-1")
    if date_value and date_value.isdigit():
        date_value = int(date_value)
    if date_value2 and date_value2.isdigit():
        date_value2 = int(date_value2)
    form = ActiveUserStatForm(request.GET)
    return render(request, "maillog/active_user.html", context={
        "form": form,
        "domain_list": domain_list,
        "domain": domain,
        "date_select": date_select,
        "date_select2": date_select2,
        "date_value" : date_value,
        "date_value2": date_value2,
    })

def mailLogActiveSearch(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    username = data.get('username', '')

    department = data.get('department', '0')
    department = 0 if not department else int(department)
    showmax = data.get('showmax', '')
    showmax = 0 if not showmax.strip() else int(showmax)

    date_select = data.get('date_select', '')
    if not date_select or date_select=="None":
        date_select = "-1"
    date_select = int(date_select)

    date_select2 = data.get('date_select2', '')
    if not date_select2 or date_select2=="None":
        date_select2 = "-1"
    date_select2 = int(date_select2)

    domain, domain_list = getDomainObj(request)
    domain_id = domain.id
    q_domain = Q(domain_id=domain.id)

    id_list = []
    if department and int(department)>0:
        dept_list = []
        condition_dept = add_condition(Q(id=department), q_domain)
        for obj in Department.objects.filter( condition_dept ):
            dept_list.append( obj.id )

        q_dept = None
        for dept_id in dept_list:
            if q_dept:
                q_dept = q_dept | Q(dept_id=dept_id)
            else:
                q_dept = Q(dept_id=dept_id)
        for obj in DepartmentMember.objects.filter( q_dept ):
            id_list.append( obj.mailbox_id )
        if not id_list:
            return "stat", [], None, 0, 1, 1

    condition = None

    condition_mailbox = None
    q_box = None
    for mailbox_id in id_list:
        if q_box:
            q_box = q_box | Q(id=mailbox_id)
        else:
            q_box = Q(id=mailbox_id)
    if q_box:
        condition_mailbox = add_condition(condition_mailbox, q_box)
    #-------------------------- 筛选 邮箱 ----------------------------
    if search:
        condition_mailbox = add_condition(condition_mailbox, Q(name__icontains=username))
    if username:
        condition_mailbox = add_condition(condition_mailbox, Q(name__icontains=username))
    if condition_mailbox:
        condition_mailbox = add_condition(condition_mailbox, Q(domain_id=domain_id))
        list_box = Mailbox.objects.filter(condition_mailbox)
        for box in list_box:
            if condition:
                condition = condition | Q(mailbox_id=box.id)
            else:
                condition = Q(mailbox_id=box.id)
    #-------------------------- 筛选 邮箱 完毕 ------------------------
    if condition:
        condition = Q(domain_id=domain_id) & condition
    else:
        condition = Q(domain_id=domain_id)

    start_day = max(date_select, date_select2)
    end_day = min(date_select, date_select2)
    start_time=get_day(int(start_day))

    #obj_cache = LogActive.objects.filter(add_condition(condition, Q(key=start_time))).first()
    #暂时先不用缓存
    obj_cache = None
    condition_single = Q(domain_id=domain_id)
    if obj_cache:
        condition = add_condition(condition, Q(key__gte=start_time))
        condition_single = add_condition(condition_single, Q(key__gte=start_time))
        if end_day>-1 and end_day != start_day:
            end_time=get_day(int(end_day))
            condition = add_condition(condition, Q(key__lt=end_time))
            condition_single = add_condition(condition_single, Q(key__lt=end_time))
        lists = LogActive.objects.all()
        lists = lists.filter(condition).values('mailbox_id').annotate(size__count=Sum('total_count'),size__sum=Sum('total_flow')).order_by('-size__count')
        flag = "cache"
    else:
        condition = add_condition(condition, Q(recv_time__gte=start_time))
        condition_single = add_condition(condition_single, Q(recv_time__gte=start_time))
        if end_day>-1 and end_day != start_day:
            end_time=get_day(int(end_day))
            condition = add_condition(condition, Q(recv_time__lt=end_time))
            condition_single = add_condition(condition_single, Q(recv_time__lt=end_time))
        lists = MailLog.objects.all()
        lists = lists.filter(condition).values('mailbox_id').annotate(Count('size'),Sum('size')).order_by('-size__count')
        flag = "stat"

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

    return flag, lists, condition_single, start_num, page, length, showmax

def mailLogActiveStatSingle(flag, lists, d, condition):
    MB=1024*1024.0
    count = len(lists)
    mailbox_id = d["mailbox_id"]
    total_count = d["size__count"]
    total_flow = round(int(d["size__sum"])/MB,2)

    in_count = in_flow = out_count = out_flow =0
    success_count = success_flow = 0
    spam_count = spam_flow = 0
    failure_count = failure_flow = 0
    spam_ratio = '--'
    out_ratio = '--'

    obj_box = Mailbox.objects.filter(id=mailbox_id).first()
    if not obj_box:
        name = u"已删除邮箱_%s"%mailbox_id
    else:
        name = obj_box.name

    last_time = time.time()
    q = add_condition(condition, Q(mailbox_id=mailbox_id))

    if flag == "cache":
        #last_time = count_time(last_time)
        #入站流量
        lists = lists.filter(q).values('mailbox_id').annotate(
                        Sum('total_count'),    Sum('total_flow'),
                        Sum('in_count'),    Sum('in_flow'),
                        Sum('spam_count'),    Sum('spam_flow'),
                        Sum('success_count'),    Sum('success_flow'),
                        ).first()
        #last_time = count_time(last_time)
        in_count = int(lists["in_count__sum"])
        in_flow_base = int(lists["in_flow__sum"])
        in_flow = round(in_flow_base/MB,2)
        out_count = max(total_count - in_count, 0)
        out_flow = (int(d["size__sum"]) - in_flow_base)/MB
        out_flow = max(round(out_flow,2), 0)
        success_count = int(lists["success_count__sum"])
        success_flow = int(lists["success_flow__sum"])
        spam_count = int(lists["spam_count__sum"])
        spam_flow = round(lists["spam_flow__sum"]/MB,2)
    else:
        #print ">>>> 1111   "
        #last_time = count_time(last_time)
        #入站流量
        lists_in = lists.filter(q & Q(type='in')).values('mailbox_id').annotate(Count('size'),Sum('size')).first()
        #print ">>>> 2222   "
        #last_time = count_time(last_time)
        #出站成功数量
        lists_out_success = lists.filter(q & Q(result='1') & Q(type='out')).values('mailbox_id').annotate(Count('size'),Sum('size')).first()
        #print ">>>> 3333   "
        #last_time = count_time(last_time)
        #垃圾数量
        lists_spam = lists.filter(q & Q(type='in',status='spam-flag')).values('mailbox_id').annotate(Count('size'),Sum('size')).first()
        #print ">>>> 4444   "
        #last_time = count_time(last_time)

        in_flow_base = 0
        if lists_in:
            in_count = int(lists_in["size__count"])
            in_flow_base = int(lists_in["size__sum"])
            in_flow = round(in_flow_base/MB,2)
        out_count = max(total_count - in_count, 0)
        out_flow = (int(d["size__sum"]) - in_flow_base)/MB
        out_flow = max(round(out_flow,2), 0)

        if lists_out_success:
            success_count = int(lists_out_success["size__count"])
            success_flow = round(lists_out_success["size__sum"]/MB,2)
            #因为浮点数计算可能有误差，所以取两者最大值，避免显示看起来很奇怪
            out_flow = max(out_flow, success_flow)
        failure_count = max(out_count - success_count,0)
        failure_flow = max(round(out_flow - success_flow,2),0)

        if lists_spam:
            spam_count = int(lists_spam["size__count"])
            spam_flow = round(lists_spam["size__sum"]/MB,2)

    if in_count > 0:
        ratio = round( spam_count*1.0/in_count, 3 )
        spam_ratio = "%s%%"%(ratio*100)
    if out_count > 0:
        ratio = round( success_count*1.0/out_count, 3 )
        out_ratio = "%s%%"%(ratio*100)

    data = {
        'name':name,
        'total_used' : 0,
        'total_count': total_count,
        'total_flow': total_flow,
        'd': d,
        'in_count': in_count,  'in_flow': in_flow,
        'out_count': out_count, 'out_flow': out_flow,
        'spam_count': spam_count, 'spam_flow': spam_flow,
        'success_count': success_count, 'success_flow': success_flow,
        'failure_count': failure_count, 'failure_flow': failure_flow,
        'spam_ratio': spam_ratio, 'out_ratio': out_ratio,
    }
    return data

@licence_required
def ajax_mailLogActiveUserStat(request):
    last_time = time.time()
    flag, lists, condition, start_num, page, length, showmax = mailLogActiveSearch(request)
    #print "mailLogActiveSearch:  ",condition
    #last_time = count_time(last_time)

    MB=1024*1024.0
    count = len(lists)
    if showmax >0 and count > showmax:
        count = showmax
    if start_num >= count:
        page = 1
    paginator = Paginator(lists, length)
    #print "mailLogActiveSearch Paginator"
    #last_time = count_time(last_time)
    try:
        page_lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page_lists = paginator.page(paginator.num_pages)
    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page-1) + 1

    for d in page_lists.object_list:
        data = mailLogActiveStatSingle(flag, lists, d, condition)
        #print "mailLogActiveStatSingle:  ",d
        #last_time = count_time(last_time)

        data["number"] = number
        t = TemplateResponse(request, 'maillog/ajax_active_user.html', data )
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")

def dumpActiveData(flag, object_list, showmax, condition):
    import xlwt,StringIO,os
    #创建workbook对象并设置编码
    ws = xlwt.Workbook(encoding='utf-8')
    w = ws.add_sheet(u'邮件收发统计',cell_overwrite_ok=True)
    w.write(0, 0, u"序号")
    w.write(0, 1, u"用户名")
    w.write(0, 2, u"已用容量")
    w.write(0, 3, u"邮件数量")
    w.write(0, 4, u"总流量")
    w.write(0, 5, u"入站数量")
    w.write(0, 6, u"入站流量")
    w.write(0, 7, u"垃圾过滤数量")
    w.write(0, 8, u"垃圾过滤流量")
    w.write(0, 9, u"出站数量")
    w.write(0, 10, u"出站流量")
    w.write(0, 11, u"成功数量")
    w.write(0, 12, u"成功流量")
    w.write(0, 13, u"失败数量")
    w.write(0, 14, u"失败流量")
    w.write(0, 15, u"垃圾率")
    w.write(0, 16, u"出站成功率")
    excel_row = 1

    cnt = 0
    last_time = time.time()
    for d in object_list:
        data = mailLogActiveStatSingle(flag, object_list, d, condition)

        name = data["name"]
        total_used = data["total_used"]
        total_count = data["total_count"]
        total_flow = data["total_flow"]
        in_count = data["in_count"]
        in_flow = data["in_flow"]
        out_count = data["out_count"]
        out_flow = data["out_flow"]
        spam_count = data["spam_count"]
        spam_flow = data["spam_flow"]
        success_count = data["success_count"]
        success_flow = data["success_flow"]
        failure_count = data["failure_count"]
        failure_flow = data["failure_flow"]
        spam_ratio = data["spam_ratio"]
        out_ratio = data["out_ratio"]

        w.write(excel_row, 0, excel_row)
        w.write(excel_row, 1, name)
        w.write(excel_row, 2, total_used)
        w.write(excel_row, 3, total_count)
        w.write(excel_row, 4, total_flow)
        w.write(excel_row, 5, in_count)
        w.write(excel_row, 6, in_flow)
        w.write(excel_row, 7, out_count)
        w.write(excel_row, 8, out_flow)
        w.write(excel_row, 9, spam_count)
        w.write(excel_row, 10, spam_flow)
        w.write(excel_row, 11, success_count)
        w.write(excel_row, 12, success_flow)
        w.write(excel_row, 13, failure_count)
        w.write(excel_row, 14, failure_flow)
        w.write(excel_row, 15, spam_ratio)
        w.write(excel_row, 16, out_ratio)
        excel_row += 1
        cnt += 1
        if showmax and cnt>=showmax:
            break
    return download_excel(ws,"active.xls")

@licence_required
def mailLogExportActive(request):
    data = request.GET
    flag, lists, condition, start_num, page, length, showmax = mailLogActiveSearch(request)
    return dumpActiveData(flag, lists, showmax, condition)

def get_mail_stat_data(domain_id, mailbox_id, t):
    def get_stat(lists,condition,type,key):
        data = LogReport.get_cache(domain_id,mailbox_id,type,key)
        if not data:
            stat = lists.filter( condition )
            total = len(stat)
            data = {"total":total}
            LogReport.save_cache(domain_id,mailbox_id,type,key,data)
        total = int(data["total"])
        return total
    def check_sql_domain(sql):
        if domain_id:
            sql += " AND `domain_id`={}".format(domain_id)
        return sql
    def count_maillog_today(t,today):
        sql_total = 'select count(1) from core_mail_log where `type`="{}"'.format(t)
        sql_total = check_sql_domain(sql_total)
        stat_total = MailLog.objects.extra(select={'count':sql_total}).first()
        size_total = 0 if not stat_total else stat_total.count

        sql_today = "select count(1) from core_mail_log where `type`='{}' and `recv_time`>='{}'".format( t, today )
        sql_today = check_sql_domain(sql_today)
        stat_today = MailLog.objects.extra(select={'count':sql_today}).first()
        size_today = 0 if not stat_today else stat_today.count
        return size_total, size_today
    def count_maillog_today2(t,today):
        sql_total = 'select count(1) from core_mail_log where `status`="{}"'.format(t)
        sql_total = check_sql_domain(sql_total)
        stat_total = MailLog.objects.extra(select={'count':sql_total}).first()
        size_total = 0 if not stat_total else stat_total.count

        sql_today = "select count(1) from core_mail_log where `status`='{}' and `recv_time`>='{}'".format( t, today )
        sql_today = check_sql_domain(sql_today)
        stat_today = MailLog.objects.extra(select={'count':sql_today}).first()
        size_today = 0 if not stat_today else stat_today.count
        return size_total, size_today
    def count_authlog_today(t,today):
        sql_total = 'select count(1) from core_auth_log where `type`="{}"'.format(t)
        sql_total = check_sql_domain(sql_total)
        stat_total = MailLog.objects.extra(select={'count':sql_total}).first()
        size_total = 0 if not stat_total else stat_total.count

        sql_today = "select count(1) from core_auth_log where `type`='{}' and `time`>='{}'".format( t, today )
        sql_today = check_sql_domain(sql_today)
        stat_today = MailLog.objects.extra(select={'count':sql_today}).first()
        size_today = 0 if not stat_today else stat_today.count
        return size_total, size_today

    condition = None
    if domain_id:
        condition = Q(domain_id=domain_id)
    today = get_day()
    day_1 = get_day(1)
    day_2 = get_day(2)
    day_3 = get_day(3)
    day_4 = get_day(4)
    day_5 = get_day(5)
    day_6 = get_day(6)
    lists = MailLog.objects.all()
    if t == "smtp_in":
        size_total, size_today = count_maillog_today('in', today)

        condition = add_condition(condition,Q(type='in'))
        lists = MailLog.objects.all()
        size_6 = get_stat( lists, condition & (Q(recv_time__gte=day_6) & Q(recv_time__lt=day_5)),t,day_6)
        size_5 = get_stat( lists, condition & (Q(recv_time__gte=day_5) & Q(recv_time__lt=day_4)),t,day_5)
        size_4 = get_stat( lists, condition & (Q(recv_time__gte=day_4) & Q(recv_time__lt=day_3)),t,day_4)
        size_3 = get_stat( lists, condition & (Q(recv_time__gte=day_3) & Q(recv_time__lt=day_2)),t,day_3)
        size_2 = get_stat( lists, condition & (Q(recv_time__gte=day_2) & Q(recv_time__lt=day_1)),t,day_2)
        size_1 = get_stat( lists, condition & (Q(recv_time__gte=day_1) & Q(recv_time__lt=today)),t,day_1)
        size_week = size_1 + size_2 + size_3 + size_4 + size_5 + size_6 + size_today
    elif t == "smtp_out":
        size_total, size_today = count_maillog_today('out', today)

        condition = add_condition(condition,Q(type='out'))
        lists = MailLog.objects.all()
        size_6 = get_stat( lists, condition & (Q(recv_time__gte=day_6) & Q(recv_time__lt=day_5)),t,day_6)
        size_5 = get_stat( lists, condition & (Q(recv_time__gte=day_5) & Q(recv_time__lt=day_4)),t,day_5)
        size_4 = get_stat( lists, condition & (Q(recv_time__gte=day_4) & Q(recv_time__lt=day_3)),t,day_4)
        size_3 = get_stat( lists, condition & (Q(recv_time__gte=day_3) & Q(recv_time__lt=day_2)),t,day_3)
        size_2 = get_stat( lists, condition & (Q(recv_time__gte=day_2) & Q(recv_time__lt=day_1)),t,day_2)
        size_1 = get_stat( lists, condition & (Q(recv_time__gte=day_1) & Q(recv_time__lt=today)),t,day_1)
        size_week = size_1 + size_2 + size_3 + size_4 + size_5 + size_6 + size_today
    elif t == "pop3_session":
        size_total, size_today = count_authlog_today('pop3', today)

        condition = add_condition(condition,Q(type='pop3'))
        lists = AuthLog.objects.all()
        size_6 = get_stat( lists, condition & (Q(time__gte=day_6) & Q(time__lt=day_5)),t,day_6)
        size_5 = get_stat( lists, condition & (Q(time__gte=day_5) & Q(time__lt=day_4)),t,day_5)
        size_4 = get_stat( lists, condition & (Q(time__gte=day_4) & Q(time__lt=day_3)),t,day_4)
        size_3 = get_stat( lists, condition & (Q(time__gte=day_3) & Q(time__lt=day_2)),t,day_3)
        size_2 = get_stat( lists, condition & (Q(time__gte=day_2) & Q(time__lt=day_1)),t,day_2)
        size_1 = get_stat( lists, condition & (Q(time__gte=day_1) & Q(time__lt=today)),t,day_1)
        size_week = size_1 + size_2 + size_3 + size_4 + size_5 + size_6 + size_today
    elif t == "imap_session":
        size_total, size_today = count_authlog_today('imap', today)

        condition = add_condition(condition,Q(type='imap'))
        lists = AuthLog.objects.all()
        size_6 = get_stat( lists, condition & (Q(time__gte=day_6) & Q(time__lt=day_5)),t,day_6)
        size_5 = get_stat( lists, condition & (Q(time__gte=day_5) & Q(time__lt=day_4)),t,day_5)
        size_4 = get_stat( lists, condition & (Q(time__gte=day_4) & Q(time__lt=day_3)),t,day_4)
        size_3 = get_stat( lists, condition & (Q(time__gte=day_3) & Q(time__lt=day_2)),t,day_3)
        size_2 = get_stat( lists, condition & (Q(time__gte=day_2) & Q(time__lt=day_1)),t,day_2)
        size_1 = get_stat( lists, condition & (Q(time__gte=day_1) & Q(time__lt=today)),t,day_1)
        size_week = size_1 + size_2 + size_3 + size_4 + size_5 + size_6 + size_today
    elif t == "spam_receive":
        size_total, size_today = count_maillog_today2('spam-flag', today)

        condition = add_condition(condition,Q(status='spam-flag'))
        lists = MailLog.objects.all()
        size_6 = get_stat( lists, condition & (Q(recv_time__gte=day_6) & Q(recv_time__lt=day_5)),t,day_6)
        size_5 = get_stat( lists, condition & (Q(recv_time__gte=day_5) & Q(recv_time__lt=day_4)),t,day_5)
        size_4 = get_stat( lists, condition & (Q(recv_time__gte=day_4) & Q(recv_time__lt=day_3)),t,day_4)
        size_3 = get_stat( lists, condition & (Q(recv_time__gte=day_3) & Q(recv_time__lt=day_2)),t,day_3)
        size_2 = get_stat( lists, condition & (Q(recv_time__gte=day_2) & Q(recv_time__lt=day_1)),t,day_2)
        size_1 = get_stat( lists, condition & (Q(recv_time__gte=day_1) & Q(recv_time__lt=today)),t,day_1)
        size_week = size_1 + size_2 + size_3 + size_4 + size_5 + size_6 + size_today
    elif t == "spam_reject":
        size_total, size_today = count_maillog_today2('spam', today)

        condition = add_condition(condition,Q(status='spam'))
        lists = MailLog.objects.all()
        size_6 = get_stat( lists, condition & (Q(recv_time__gte=day_6) & Q(recv_time__lt=day_5)),t,day_6)
        size_5 = get_stat( lists, condition & (Q(recv_time__gte=day_5) & Q(recv_time__lt=day_4)),t,day_5)
        size_4 = get_stat( lists, condition & (Q(recv_time__gte=day_4) & Q(recv_time__lt=day_3)),t,day_4)
        size_3 = get_stat( lists, condition & (Q(recv_time__gte=day_3) & Q(recv_time__lt=day_2)),t,day_3)
        size_2 = get_stat( lists, condition & (Q(recv_time__gte=day_2) & Q(recv_time__lt=day_1)),t,day_2)
        size_1 = get_stat( lists, condition & (Q(recv_time__gte=day_1) & Q(recv_time__lt=today)),t,day_1)
        size_week = size_1 + size_2 + size_3 + size_4 + size_5 + size_6 + size_today
    elif t == "spam_virus":
        size_total, size_today = count_maillog_today2('virus', today)

        condition = add_condition(condition,Q(status='virus'))
        lists = MailLog.objects.all()
        size_6 = get_stat( lists, condition & (Q(recv_time__gte=day_6) & Q(recv_time__lt=day_5)),t,day_6)
        size_5 = get_stat( lists, condition & (Q(recv_time__gte=day_5) & Q(recv_time__lt=day_4)),t,day_5)
        size_4 = get_stat( lists, condition & (Q(recv_time__gte=day_4) & Q(recv_time__lt=day_3)),t,day_4)
        size_3 = get_stat( lists, condition & (Q(recv_time__gte=day_3) & Q(recv_time__lt=day_2)),t,day_3)
        size_2 = get_stat( lists, condition & (Q(recv_time__gte=day_2) & Q(recv_time__lt=day_1)),t,day_2)
        size_1 = get_stat( lists, condition & (Q(recv_time__gte=day_1) & Q(recv_time__lt=today)),t,day_1)
        size_week = size_1 + size_2 + size_3 + size_4 + size_5 + size_6 + size_today
    #end if
    data = {
            "stat_total"    :   size_total,
            "stat_week"     :   size_week,
            "stat_6"        :   size_6,
            "stat_5"        :   size_5,
            "stat_4"        :   size_4,
            "stat_3"        :   size_3,
            "stat_2"        :   size_2,
            "stat_1"        :   size_1,
            "stat_today"   :   size_today,
        }
    return data

@licence_required
def mailLogMailStat(request):
    domain, domain_list = getDomainObj(request)
    if not domain:
        domain_id = domain_list.filter(domain=domain).first().id
    else:
        domain_id = domain.id

    mailbox_id = 0
    smtp_in = get_mail_stat_data(domain_id,mailbox_id,"smtp_in")
    smtp_out = get_mail_stat_data(domain_id,mailbox_id,"smtp_out")
    imap_session = get_mail_stat_data(domain_id,mailbox_id,"imap_session")
    pop3_session = get_mail_stat_data(domain_id,mailbox_id,"pop3_session")
    spam_receive = get_mail_stat_data(domain_id,mailbox_id,"spam_receive")
    spam_reject = get_mail_stat_data(domain_id,mailbox_id,"spam_reject")
    spam_virus = get_mail_stat_data(domain_id,mailbox_id,"spam_virus")
    return render(request, "maillog/mail_stat.html", context={
            "domain_list": domain_list,
            "domain": domain,

            "smtp_in"   :   smtp_in,
            "smtp_out"  :   smtp_out,
            "imap_session": imap_session,
            "pop3_session": pop3_session,
            "spam_receive": spam_receive,
            "spam_reject": spam_reject,
            "spam_virus": spam_virus,
    })

def dumpMailReportData(domain_id):
    import xlwt,StringIO,os

    mailbox_id = 0
    smtp_in = get_mail_stat_data(domain_id,mailbox_id,"smtp_in")
    smtp_out = get_mail_stat_data(domain_id,mailbox_id,"smtp_out")
    imap_session = get_mail_stat_data(domain_id,mailbox_id,"imap_session")
    pop3_session = get_mail_stat_data(domain_id,mailbox_id,"pop3_session")
    spam_receive = get_mail_stat_data(domain_id,mailbox_id,"spam_receive")
    spam_reject = get_mail_stat_data(domain_id,mailbox_id,"spam_reject")
    spam_virus = get_mail_stat_data(domain_id,mailbox_id,"spam_virus")

    #创建workbook对象并设置编码
    ws = xlwt.Workbook(encoding='utf-8')
    w = ws.add_sheet(u'邮件收发统计',cell_overwrite_ok=True)
    w.write(0, 0, u"SMTP/IMAP/POP")
    w.write(0, 1, u"近期总计")
    w.write(0, 2, u"7天总计")
    w.write(0, 3, u"今日")
    w.write(0, 4, u"昨日")
    w.write(0, 5, u"2日之前")
    w.write(0, 6, u"3日之前")
    w.write(0, 7, u"4日之前")
    w.write(0, 8, u"5日之前")
    w.write(0, 9, u"6日之前")

    excel_row = 1
    rows_mail =(
        (u"SMTP邮件(收信)",smtp_in),
        (u"SMTP邮件(发信)",smtp_out),
        (u"IMAP会话",imap_session),
        (u"POP3会话",pop3_session),
    )
    rows_spam =(
        (u"已接收的垃圾邮件",spam_receive),
        (u"已拒绝的垃圾邮件",spam_reject),
        (u"已拒绝的病毒邮件",spam_virus),
    )

    for name,data in rows_mail:
        excel_row += 1
        w.write(excel_row, 0, name)
        w.write(excel_row, 1, data["stat_total"])
        w.write(excel_row, 2, data["stat_week"])
        w.write(excel_row, 3, data["stat_today"])
        w.write(excel_row, 4, data["stat_1"])
        w.write(excel_row, 5, data["stat_2"])
        w.write(excel_row, 6, data["stat_3"])
        w.write(excel_row, 7, data["stat_4"])
        w.write(excel_row, 8, data["stat_5"])
        w.write(excel_row, 9, data["stat_6"])

    for i in xrange(4):
        excel_row += 1
        w.write(excel_row, 0, u"")

    excel_row += 1
    w.write(excel_row, 0, u"垃圾/病毒邮件")
    w.write(excel_row, 1, u"近期总计")
    w.write(excel_row, 2, u"7天总计")
    w.write(excel_row, 3, u"今日")
    w.write(excel_row, 4, u"昨日")
    w.write(excel_row, 5, u"2日之前")
    w.write(excel_row, 6, u"3日之前")
    w.write(excel_row, 7, u"4日之前")
    w.write(excel_row, 8, u"5日之前")
    w.write(excel_row, 9, u"6日之前")
    for name,data in rows_spam:
        excel_row += 1
        w.write(excel_row, 0, name)
        w.write(excel_row, 1, data["stat_total"])
        w.write(excel_row, 2, data["stat_week"])
        w.write(excel_row, 3, data["stat_today"])
        w.write(excel_row, 4, data["stat_1"])
        w.write(excel_row, 5, data["stat_2"])
        w.write(excel_row, 6, data["stat_3"])
        w.write(excel_row, 7, data["stat_4"])
        w.write(excel_row, 8, data["stat_5"])
        w.write(excel_row, 9, data["stat_6"])

    return download_excel(ws,"mail_report.xls")

@licence_required
def mailLogExportMailReport(request):
    domain, domain_list = getDomainObj(request)
    if not domain:
        domain_id = domain_list.filter(domain=domain).first().id
    else:
        domain_id = domain.id
    return dumpMailReportData(domain_id)
