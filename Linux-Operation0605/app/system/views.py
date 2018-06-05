# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import shutil
import time
import os
import re
import subprocess
import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.db import connection
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.utils import timezone
from lib.licence import Licence
from lib.licence import licence_required
from app.core.models import DomainAttr, Domain, Mailbox, VisitLog, AuthLog
from app.core.templatetags.tags import smooth_timedelta

@login_required
def licence(request):
    """
    授权信息
    :param request:
    :return:
    """
    licence_file = '/usr/local/u-mail/data/www/webmail/licence.dat'

    if request.method == "POST":
        f = request.FILES.get('licence_file', '')
        if not f:
            messages.add_message(request, messages.ERROR, u'请选择授权文件导入')
        else:
            try:
                licence_data = f.read()
                lic_new = Licence(licence_data=licence_data)
                info_new = lic_new.get_licence_info()
            except Exception,err:
                info_new = {}
                messages.add_message(request, messages.ERROR, u'授权文件格式错误，请重新导入')
                return HttpResponseRedirect(reverse('system_licence'))
            try:
                lic = Licence(licence_file=licence_file)
                info = lic.get_licence_info()
            except:
                info = {}

            if info and info_new.get("domain_name","")!=info["domain_name"]:
                messages.add_message(request, messages.ERROR, u'授权文件域名错误，请重新导入')
                return HttpResponseRedirect(reverse('system_licence'))

            now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            if info_new.get("expires_time","") and info_new["expires_time"].strftime('%Y%m%d%H%M%S')<=now:
                messages.add_message(request, messages.ERROR, u'授权截至日期错误，请重新导入')
                return HttpResponseRedirect(reverse('system_licence'))

            shutil.copy(licence_file, '{}.{}'.format(licence_file, now))
            open(licence_file, 'w').write(licence_data)
            messages.add_message(request, messages.SUCCESS, u'授权文件更新成功')
        return HttpResponseRedirect(reverse('system_licence'))

    try:
        lic = Licence(licence_file=licence_file)
        info = lic.get_licence_info()
    except:
        info = {}
        messages.add_message(request, messages.ERROR, u'授权文件格式错误，请重新导入')
    # 测试用户信息处理
    if info.get('evaluation', ''):
        # 生成试用期信息
        system_created = DomainAttr.getAttrObjValue(1, 'system', 'created')
        trial_begin = datetime.datetime.strptime(system_created, '%Y-%m-%d %H:%M:%S')
        trial_end = trial_begin + datetime.timedelta(days=30)
        extra_module = ['all']
    else:
        # 正式用户信息处理
        trial_begin = ''
        trial_end = ''

        # 扩展模块信息
        try:
            extra_module = lic.get_available_module()
        except:
            extra_module = ''

    if isinstance(extra_module, list):
        licence_mod = {
            'all': '所有模块',
            'sms': '短信模块',
            'ctasd_inbound': '高级入站垃圾邮件检测',
            'ctasd_outbound': '高级出站垃圾邮件检测',
        }
        extra_module = ','.join(map(lambda l: licence_mod.get(l, ''), extra_module))

    return render(request, template_name='system/licence.html', context={
        'info': info,
        'trial_begin': trial_begin,
        'trial_end': trial_end,
        'extra_module': extra_module,
    })

def _get_version_info(version_file):
    """
    获取版本信息
    :param version_file:
    :return:
    """
    if not os.path.exists(version_file):
        return "Unknown", "Unknown"
    mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.stat(version_file).st_mtime))
    content = open(version_file, 'r').read()
    return content, mtime


@login_required
def sysinfo(request):
    """
    系统信息
    :param request:
    :return:
    """
    domain_count = Domain.objects.count()
    mailbox_count = Mailbox.objects.count()
    version_info_dict = {
        'webmail': {'version_file': '/usr/local/u-mail/data/www/webmail/version'},
        'app': {'version_file': '/usr/local/u-mail/app/version'},
        'spam': {'version_file': '/usr/local/u-mail/spam-filter/version'},
    }
    for k, v in version_info_dict.iteritems():
        v['content'], v['mtime'] = _get_version_info(v['version_file'])

    # php_version
    cmd = '/usr/local/u-mail/service/php/bin/php -v'
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    php_version = p.stdout.read().split('\n')[0]

    # mysql version
    with connection.cursor() as cursor:
        cursor.execute("select version() as version")
        mysql_version = cursor.fetchone()[0]

    return render(request, template_name='system/sysinfo.html', context={
        'domain_count': domain_count,
        'mailbox_count': mailbox_count,
        'version_info': version_info_dict,
        'php_version': php_version,
        'mysql_version': mysql_version
    })

@login_required
def changlog(request):
    log = request.GET.get('log', '')
    if log == 'webmail':
        log_file = '/usr/local/u-mail/data/www/webmail/changelog.php'
    elif log == 'app':
        log_file = '/usr/local/u-mail/app/CHANGELOG'
        changelog = open(log_file, 'r').read()
        return render(request, template_name='system/changelog.html', context={
            'changelog': changelog,
        })
    raise Http404


@login_required
def ajax_get_visitlog(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['lasttime', 'mailbox', 'mailbox', 'logintime', 'lasttime', 'logintime', 'clienttype', 'clientip', 'lasttime']
    lists = VisitLog.objects.all()
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
        continuetime = smooth_timedelta(l.lasttime - l.logintime)
        out_time = timezone.now() - l.lasttime
        is_login = True if out_time.total_seconds() <= 600 else False
        t = TemplateResponse(request, 'system/ajax_get_visitlog.html', {'l': l, 'number': number, 'continuetime': continuetime, 'is_login': is_login})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")

@licence_required
def visitlog(request):
    """
    用户访问记录
    :param request:
    :return:
    """

    return render(request, template_name='system/visitlog.html', context={
    })



@login_required
def ajax_get_authlog(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    colums = ['id', 'user', 'type', 'time', 'client_ip', 'is_login']
    lists = AuthLog.objects.all()
    if search:
        lists = lists.filter(user__icontains=search)

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
        t = TemplateResponse(request, 'system/ajax_get_authlog.html', {'l': l, 'number': number})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs), content_type="application/json")

@licence_required
def authlog(request):
    """
    用户访问记录
    :param request:
    :return:
    """

    return render(request, template_name='system/authlog.html', context={
    })
