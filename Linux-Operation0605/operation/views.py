# -*- coding: utf-8 -*-
#
import os
import re
import subprocess
import urllib2
import json
import time
import datetime
import psutil

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.template.response import TemplateResponse
from django.contrib import messages
from django.conf import settings

from django_sysinfo.api import get_sysinfo, get_processes
from django_sysinfo.utils import get_network_speed
from django_sysinfo.conf import PROCESSES

from django_redis import get_redis_connection
from django.db.models import Q
from app.core.models import Domain, User, UpgradeList

from forms import QueueSearchForm
from lib.tools import get_process_pid, reboot
from lib.files import make_dir
from lib.parse_email import ParseEmail
from app.utils.domain_session import get_domainid_bysession

def licence_notify(request):
    return render(request, "licence_notify.html", context={})

@login_required
def ajax_get_html(request):
    path = request.GET.get("path","")
    if not path:
        return HttpResponseRedirect(reverse('home'))
    return render(request, "tpl/%s"%path, context={})

@login_required
def s(request, template_name='index.html'):
    return render(request, template_name, {
    })

@login_required
def home(request, template_name='home.html'):
    pid = get_process_pid("'/usr/local/u-mail/update.sh'")
    if request.method == "POST":
        status = request.POST.get("status", "")
        if status == "update":
            if not pid:
                log_dir = os.path.join(settings.BASE_DIR, 'log')
                make_dir(log_dir)
                log_file = os.path.join(log_dir, 'update_umail_beta.log')
                # 升级的命令
                cmd = "/usr/local/u-mail/update.sh beta >{} 2>&1".format(log_file)
                subprocess.Popen(cmd, shell=True)
            return HttpResponseRedirect(reverse('home'))
        if status in ['reboot', 'shutdown']:
            password = request.POST.get('password', '')
            if not reboot('root', password, action=status):
                messages.add_message(request, messages.ERROR, u'密码输入错误!')
            else:
                msg = u'重启' if status == 'reboot' else u'关闭'
                messages.add_message(request, messages.SUCCESS, u'您的服务器即将{}!'.format(msg))
            return HttpResponseRedirect(reverse('home'))

    umail_repo = "/etc/yum.repos.d/umail.repo"
    umail_repo_http = "http://www.comingchina.com:8080/repo/umail_beta.repo"
    cmd = 'yum --disablerepo=* --enablerepo=umail_beta repolist'
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res = p.stdout.read()

    if res.lower().find('error') != -1:
        try:
            with open(umail_repo, 'a') as fw:
                fw.write(urllib2.urlopen(umail_repo_http).read())
        except Exception,err:
            print "download %s error: %s"%(umail_repo_http, str(err))

    versions = []
    cmd = "yum --disablerepo=* --enablerepo=umail_beta info umail_webmail"
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.wait()
    lines = p.stdout.readlines()
    for line in lines:
        line = line.decode('utf-8', 'ignore')
        if line.find('Version') != -1 or line.find(u'版本') != -1:
            versions.append(line.replace(u'：', ':').split(':')[-1].strip())
    install_version = versions[0] if (versions and versions[0]) else u'未识别'
    available_version = versions[1] if len(versions) >= 2 else None

    sys_info = get_sysinfo(request)

    return render(request, template_name, {
        'info': sys_info,
        "pid": pid,
        "install_version": install_version,
        "available_version": available_version,
    })

def demo_login(request):
    from django.contrib import auth

    obj_d = Domain.objects.filter(domain="comingchina.com").first()
    obj_d2 = Domain.objects.filter(domain="test.com").first()
    if not obj_d and not obj_d2:
        return HttpResponseRedirect(reverse('my_login'))

    demo_user, _created = User.objects.get_or_create(username="demo_admin")
    if _created:
        demo_user.password = "748bf02d4fe9c98bdf7dc3c7563791e3"
        demo_user.save()

    auth.login(request, demo_user)
    return HttpResponseRedirect(reverse('home'))


@login_required
def ajax_process(request):
    """
    ajax 操作进程
    :param request:
    :return:
    """
    name = request.GET.get('name', '')
    action = request.GET.get('action', '')
    if name not in PROCESSES.keys():
        raise Http404
    if action == 'restart':
        p = psutil.Popen(PROCESSES[name][action].split())
        p.wait(30)
    res = get_processes(name=name).get(name, {})

    if 'connections' in res:
        res['connections'] = len(res['connections'])
    if 'cmdline' in res:
        res['cmdline'] = ' '.join(res['cmdline'])
    if 'create_time' in res:
        res['create_time'] = datetime.datetime.fromtimestamp(res['create_time']).strftime("%Y-%m-%d %H:%M:%S")
    if 'pid' in res:
        res['status'] = '<span class="text-success">已启动</span>'
    else:
        res['status'] = '<span class="text-danger">未启动</span>'
    res['cpu_percent'] = '%.2f%s' % (res['cpu_percent'], '%')
    res['memory_percent'] = '%.2f%s' % (res['memory_percent'], '%')

    return HttpResponse(json.dumps(res), content_type="application/json")

@login_required
def ajax_get_network(request):
    """
    ajax 定时获取网络速度
    :param request:
    :return:
    """
    res = get_network_speed()
    return HttpResponse(json.dumps(res), content_type="application/json")

@login_required
def queue(request, name, template_name='queue.html'):
    """
    查看队列信息
    :param request:
    :param name:
    :param template_name:
    :return:
    """
    queue_names = ['router', 'postman', 'smtp', 'incheck', 'maillist', 'forward', 'dkim', 'review']
    if name not in queue_names:
        raise Http404
    if request.method == "POST":
        redis = get_redis_connection()
        keys = request.POST.get('ids', '')
        action = request.POST.get('action', '')
        if action == 'empty_all':
            i = ajax_queue(request, name, action='empty_all')
        else:
            i = 0
            for key in keys.split(','):
                if _delete_queue(redis, name, key):
                    i += 1
        messages.add_message(request, messages.SUCCESS, u'成功删除{}个数据'.format(i))
        return HttpResponseRedirect(reverse('queue', args=(name,)))
    form = QueueSearchForm(request.GET)
    return render(request, template_name, {
        'name': name,
        'form': form
    })

@login_required
def ajax_queue(request, name, action=''):
    """
    ajax 加载队列信息
    :param request:
    :return:
    """
    data = request.GET
    data_key = 'task_data:' + name

    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    key = data.get('key', '')
    sender = data.get('sender', '')
    recipients = data.get('recipients', '')
    senderip = data.get('senderip', '')

    redis = get_redis_connection()
    datas = redis.hgetall(data_key)
    lists = []
    # wait_key = 'task_queue:' + name
    # keys = redis.lrange(wait_key, 0, -1)
    redis.hdel
    del_count = 0
    for k, v in datas.iteritems():
        # if k not in keys:
        #     continue
        if key and k.find(key) == -1:
            continue
        d = json.loads(v)
        d['recipients'] = ','.join(d.get('recipients', ''))

        if sender and d.get('sender', '').find(sender) == -1:
            continue
        if recipients and d.get('recipients', '').find(recipients) == -1:
            continue
        if senderip and d.get('senderip', '').find(senderip) == -1:
            continue

        if search and v.find(search) == -1:
            continue
        if action == 'empty_all':
            if _delete_queue(redis, name, k):
                del_count += 1
        d['key'] = k
        d['create_time'] = k[:10]
        lists.append(d)

    if action == 'empty_all':
        return del_count
    colums = ['key', 'sender', 'recipients', 'senderip', 'create_time']

    if lists and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            lists = sorted(lists, key=lambda l: l[colums[int(order_column)]], reverse=True)
        else:
            lists = sorted(lists, key=lambda l: l[colums[int(order_column)]])
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
    number = length * (page - 1) + 1
    for l in lists.object_list:
        t = TemplateResponse(request, 'ajax_queue.html', {'l': l, 'number': number, 'queue': name})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

def _delete_queue(redis, queue, key):
    try:
        wait_queue = 'task_queue:' + queue
        data_queue = 'task_data:' + queue
        file_path = os.path.join('/usr/local/u-mail/app/data/', 'cache_{}'.format(queue), key)
        redis.lrem(wait_queue, 0, key)
        redis.hdel(data_queue, key)
        if os.path.exists(file_path):
            os.unlink(file_path)
        return True
    except:
        return False

@login_required
def mail_read(request):
    cid = request.GET.get('cid', '')
    aid = request.GET.get('aid', '')
    download = request.GET.get('download', '')
    view_body = request.GET.get('view_body', '')
    view_source = request.GET.get('view_source', '')
    export = request.GET.get('export', '')
    key = request.GET.get('key', '')
    queue = request.GET.get('queue', '')
    file_path = os.path.join('/usr/local/u-mail/app/data/', 'cache_{}'.format(queue), key)

    redis = get_redis_connection()
    data_key = 'task_data:' + queue
    tm = json.loads(redis.hget(data_key, key))
    if key and os.path.exists(file_path):
        content = open(file_path, 'r').read()
        parse_obj = ParseEmail(content)
        m = parse_obj.parseMailTemplate()
        if cid or aid:
            attachments = m['attachments']
            real_attachments = m['real_attachments']
            if aid:
                attach = real_attachments[int(aid)]
                response = HttpResponse(attach.get('data', ''),
                                        content_type=attach.get('content_type', '').split(';')[0])
            if download:
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(
                    attach.get('decode_name', '').encode('utf-8'))
            if cid:
                for one in attachments:
                    if one.get('content_id') == cid:
                        attach = one
                        response = HttpResponse(attach.get('data', ''),
                                                content_type=attach.get('content_type', '').split(';')[0])
                        break
            return response

        if view_body:
            text = m.get('html_text', '')
            charset = m.get('html_charset', '')
            if not text:
                text = m.get('plain_text', '')
                charset = m.get('plain_charset', '')
            link = '{}?key={}&queue={}&cid=\g<cid>'.format(reverse('mail_read'), key, queue)
            text = re.sub('"cid:(?P<cid>.*?)"', link, text)

            return HttpResponse(text, charset=charset)
        if view_source:
            return render(request, "txt.html", {
                'content': content.decode('gbk', 'ignore'),
            })

        if export:
            response = HttpResponse(content, content_type='text/html')
            response['Content-Disposition'] = 'attachment; filename="eml.eml"'
            return response

        return render(request, "mail_read.html", {
            'm': m,
            'tm': tm,
            'id': id,
            'key': key,
            'queue': queue
        })
    return HttpResponse(u'no email')

def upgrade_record(request):
    domain = request.GET.get("domain","")
    if not domain:
        return HttpResponse(u'no domain')
    obj_d = Domain.objects.filter(Q(domain__icontains="comingchina.com") | Q(domain="test.com")).first()
    if not obj_d:
        return HttpResponse(u'invalid domain')

    obj = UpgradeList.getObj(domain)
    obj.app = u"{}".format(request.GET.get("app",""))
    obj.webmail = u"{}".format(request.GET.get("webmail",""))
    obj.operation = u"{}".format(request.GET.get("operation",""))
    obj.prev_app = u"{}".format(request.GET.get("prev_app",""))
    obj.prev_webmail = u"{}".format(request.GET.get("prev_webmail",""))
    obj.prev_operation = u"{}".format(request.GET.get("prev_operation",""))
    obj.update_time = u"{}".format(time.strftime('%Y-%m-%d %H:%M:%S'))
    obj.save()

    rs = {"status":"OK"}
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

def admin_upgrade_record(request):
    obj_list = UpgradeList.objects.all().order_by('-update_time')
    return render(request, "upgrade_record.html", context={
        "obj_list"      :   obj_list,
        })

def ajax_debug_kkserver(request):
    data = request.POST

    import json
    data = json.loads(request.body.decode())
    print ">>>>>>>>>>>>>>>  request.body  :   ",request.body
    print "post data is  ",data.get("users",[])
    print "get data is  ",request.GET
    rs = {
        "result"        :   0,
        "batchNo"       :   "hello",
    }
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

@login_required
def set_domain_id(request):
    next = request.META.get('HTTP_REFERER', None)
    if not next or next.endswith("lang/set/"):
        next = '/'

    response = HttpResponseRedirect(next)
    domain_id = request.POST.get('domain_id', None)
    if not domain_id:
        domain_id = get_domainid_bysession(request)
    if hasattr(request, 'session'):
        request.session['domain_id'] = domain_id
    return response

