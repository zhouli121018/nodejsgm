# coding=utf-8
import datetime
import hashlib
import os
import re
import json
# import check
import urllib2
#from phpserialize import serialize
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.context import RequestContext
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template.response import TemplateResponse
from django.db.models import Q, Count, Avg
from django.contrib.auth.forms import SetPasswordForm
from django.db.models.loading import get_model
from django.shortcuts import get_object_or_404
from django.contrib.admin.utils import unquote
from django.contrib.auth.decorators import permission_required
from django.apps import apps as dapps

from apps.core.models import Customer, CustomerIp, CustomerDomain, CustomerMailbox, Cluster, ClusterIp, IpPool, \
    RouteRule, CustomerSetting, ColCustomerDomain, PostfixStatus, Notification, CustomerLocalizedSetting, \
    CustomerSummary

from forms import ClusterForm, CustomerDomainForm, CustomerForm, CustomerIpForm, CustomerMailboxForm, IpSegmentForm, \
    IpPoolForm, CustomerSearchForm, RouteRuleForm, CustomerSettingForm, ColCustomerDomainForm, ColCustomerSearchForm, \
    RelayCustomerSearchForm, CustomerCreateForm, PostfixSearchForm, CustomerMinForm, CustomerLocalizedSettingForm, \
    CustomerSummarySearchForm, AuditLogSearchForm
from common import get_ip_list_from_net, allocate_ippool_for_customer
from lib.common import my_grep1
from lib.tools import get_random_string
from auditlog.models import LogEntry


@login_required
def customer_list(request, template_name='core/customer_list.html'):
    pools = IpPool.objects.all()
    if request.method == "POST":
        action = request.POST.get('action', '')
        if action == 'delete':
            customer_id = request.POST.get('customer_id', '')
            if customer_id:
                CustomerIp.objects.filter(customer_id=customer_id).delete()
                CustomerDomain.objects.filter(customer_id=customer_id).delete()
                CustomerMailbox.objects.filter(customer_id=customer_id).delete()
                Customer.objects.get(id=customer_id).delete()

            messages.add_message(request, messages.SUCCESS, u'删除成功')
        elif action == 'allocate':
            ids = (request.POST.get('ids', '')).split(',')
            pool_id = request.POST.get('pool_id', '')
            Customer.objects.filter(id__in=ids).update(ip_pool_id=pool_id)
            messages.add_message(request, messages.SUCCESS, u'成功分配{}个用户'.format(len(ids)))
        return HttpResponseRedirect(reverse('customer_list'))

    type = request.GET.get('type', '')
    form = CustomerSearchForm
    if type == 'relay':
        template_name = 'core/relay_customer_list.html'
        form = RelayCustomerSearchForm
    elif type == 'collect':
        template_name = 'core/collect_customer_list.html'
        form = ColCustomerSearchForm
    form = form(request.GET)
    return render_to_response(template_name, {
        'pools': pools,
        'form': form,
    }, context_instance=RequestContext(request))


def get_customer_data(data):
    username = data.get('username', '')
    customer_id = data.get('customer_id', '')
    ip = data.get('ip', '')
    domain = data.get('domain', '')
    col_domain = data.get('col_domain', '')
    mailbox = data.get('mailbox', '')
    status = data.get('status', '')
    gateway_status = data.get('gateway_status', '')
    type = data.get('type', '')
    search_pool_id = data.get('search_pool_id', '')
    customers = Customer.objects.all()
    if username:
        customers = customers.filter(Q(username__icontains=username) | Q(company__icontains=username))
    if customer_id:
        customers = customers.filter(id=customer_id)
    if ip:
        customers = customers.filter(ip__ip__icontains=ip)
    if domain:
        customers = customers.filter(domain__domain__icontains=domain)
    if mailbox:
        customers = customers.filter(mailbox__mailbox__icontains=mailbox)
    if col_domain:
        customers = customers.filter(col_domain__domain__icontains=col_domain)
    if status:
        customers = customers.filter(status=status)
    if gateway_status:
        customers = customers.filter(gateway_status=gateway_status)
    if search_pool_id:
        customers = customers.filter(ip_pool_id=search_pool_id)

    if type:
        customers = customers.annotate(ip_count=Count('ip'), domain_count=Count('domain'),
                                       mailbox_count=Count('mailbox'),
                                       col_domain_count=Count('col_domain'))

    if type == 'relay':
        customers = customers.filter(Q(ip_count__gt=0) | Q(domain_count__gt=0) | Q(mailbox__gt=0))
    elif type == 'collect':
        customers = customers.filter(col_domain_count__gt=0)
    elif type == 'all':
        customers = customers.filter(Q(ip_count__gt=0) | Q(domain_count__gt=0) | Q(mailbox__gt=0)).filter(
            col_domain_count__gt=0)

    return customers


@login_required
@permission_required('core.customer_add')
def customer_add(request):
    form = CustomerCreateForm()
    if request.method == "POST":
        form = CustomerCreateForm(request.POST)
        if form.is_valid():
            customer = form.save()
            customer.creater = request.user
            customer.save()
            # 为新用户分配发送池
            allocate_ippool_for_customer(customer.id)
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('customer_list'))
    return render_to_response("core/customer_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
@permission_required('core.customer_batchadd')
def customer_batchadd(request):
    if request.method == "POST":
        i = 0
        customer = request.POST.get('customer', '')
        for a in customer.split('\n'):
            a = a.replace('\n', '').replace('\r', '')
            if not a:
                continue
            username, company, service_start, service_end, ips, domains, mailboxes = a.split(';')[:7]
            service_start = datetime.datetime.strptime(service_start.strip(), '%Y-%m-%d').date()
            service_end = datetime.datetime.strptime(service_end.strip(), '%Y-%m-%d').date()
            c = Customer.objects.create(username=username, company=company, service_start=service_start,
                                        service_end=service_end, creater=request.user)
            for ip in ips.split(','):
                ip = ip.strip()
                if ip:
                    CustomerIp.objects.create(customer=c, ip=ip)
            for domain in domains.split(','):
                domain = domain.strip()
                if domain:
                    CustomerDomain.objects.create(customer=c, domain=domain)
            for m in mailboxes.split(','):
                m = m.strip()
                if m:
                    mailbox, password = m.split('----')[:2]
                    CustomerMailbox.objects.create(customer=c, mailbox=mailbox.strip(), password=password.strip())
            i += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加%s个客户' % i)
        return HttpResponseRedirect(reverse('customer_list'))
    return render_to_response("core/customer_batchadd.html", {
    }, context_instance=RequestContext(request))


@login_required
@permission_required('core.customer_modify')
def customer_modify(request, customer_id):
    customer_obj = Customer.objects.get(id=customer_id)
    f = CustomerForm if request.user.is_superuser else CustomerMinForm
    form = f(instance=customer_obj)
    if request.method == "POST":
        form = f(request.POST, instance=customer_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('customer_list') + "?customer_id={}".format(customer_id))
    return render_to_response("core/customer_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def customer_ip(request, customer_id):
    customer_obj = Customer.objects.get(id=customer_id)
    form = CustomerIpForm()
    if request.method == "POST":
        form = CustomerIpForm(request.POST)
        if form.is_valid():
            CustomerIp(customer=customer_obj, ip=form.data['ip']).save()
            messages.add_message(request, messages.SUCCESS, u'添加成功')
            return HttpResponseRedirect(reverse('customer_ip', args=(customer_obj.id,)))
    return render_to_response("core/customer_ip.html", {
        'form': form,
        'c': customer_obj,
    }, context_instance=RequestContext(request))


@login_required
def customer_ip_change_status(request, customer_id):
    customer_obj = Customer.objects.get(id=customer_id)
    if request.method == "POST":
        status = request.POST.get('status', '')
        ip_id = request.POST.get('ip_id', '')
        ip = CustomerIp.objects.get(id=ip_id, customer=customer_obj)
        if status == 'delete':
            ip.delete()
            msg = u'删除成功'
        elif status == 'abled':
            ip.disabled = False
            ip.save()
            msg = u'启用IP成功'
        elif status == 'disabled':
            ip.disabled = True
            ip.save()
            msg = u'禁用IP成功'

        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(reverse('customer_ip', args=(customer_obj.id,)))
    return HttpResponse('no message')


@login_required
def customer_domain(request, customer_id):
    customer_obj = Customer.objects.get(id=customer_id)
    form = CustomerDomainForm()
    if request.method == "POST":
        form = CustomerDomainForm(request.POST)
        if form.is_valid():
            CustomerDomain(customer=customer_obj, domain=form.data['domain']).save()
            messages.add_message(request, messages.SUCCESS, u'添加成功')
            return HttpResponseRedirect(reverse('customer_domain', args=(customer_obj.id,)))
    return render_to_response("core/customer_domain.html", {
        'form': form,
        'c': customer_obj,
    }, context_instance=RequestContext(request))


@login_required
def customer_domain_change_status(request, customer_id):
    customer_obj = Customer.objects.get(id=customer_id)
    if request.method == "POST":
        status = request.POST.get('status', '')
        id = request.POST.get('id', '')
        obj = CustomerDomain.objects.get(id=id, customer=customer_obj)
        if status == 'delete':
            obj.delete()
            msg = u'删除成功'
        elif status == 'abled':
            obj.disabled = False
            obj.save()
            msg = u'启用域名成功'
        elif status == 'disabled':
            obj.disabled = True
            obj.save()
            msg = u'禁用域名成功'

        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(reverse('customer_domain', args=(customer_obj.id,)))
    return HttpResponse('no message')


@login_required
def customer_mailbox(request, customer_id):
    customer_obj = Customer.objects.get(id=customer_id)
    form = CustomerMailboxForm()
    if request.method == "POST":
        form = CustomerMailboxForm(request.POST)
        if form.is_valid():
            CustomerMailbox(customer=customer_obj, mailbox=form.data['mailbox'], password=form.data['password']).save()
            messages.add_message(request, messages.SUCCESS, u'添加成功')
            return HttpResponseRedirect(reverse('customer_mailbox', args=(customer_obj.id,)))
    return render_to_response("core/customer_mailbox.html", {
        'form': form,
        'c': customer_obj,
    }, context_instance=RequestContext(request))


@login_required
def customer_mailbox_change_status(request, customer_id):
    customer_obj = Customer.objects.get(id=customer_id)
    if request.method == "POST":
        status = request.POST.get('status', '')
        id = request.POST.get('id', '')
        obj = CustomerMailbox.objects.get(id=id, customer=customer_obj)
        if status == 'delete':
            obj.delete()
            msg = u'删除成功'
        elif status == 'abled':
            obj.disabled = False
            obj.save()
            msg = u'启用帐号成功'
        elif status == 'disabled':
            obj.disabled = True
            obj.save()
            msg = u'禁用帐号成功'

        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(reverse('customer_mailbox', args=(customer_obj.id,)))
    return HttpResponse('no message')


@login_required
def col_customer_domain(request, customer_id=None):
    if not customer_id:
        customer_id = request.GET.get('customer_id', '')
    customer_obj = Customer.objects.get(id=customer_id)
    form = ColCustomerDomainForm(initial={'customer': customer_obj})
    if request.method == "POST":
        form = ColCustomerDomainForm(request.POST)
        if form.is_valid():
            form.save()
            # ColCustomerDomain(customer=customer_obj, domain=form.data['domain'],
            #                   forward_address=form.data['forward_address'].strip()).save()
            messages.add_message(request, messages.SUCCESS, u'添加成功')
            return HttpResponseRedirect('{}?customer_id={}'.format(reverse('colcustomer_domain'), customer_id))
    return render_to_response("core/col_customer_domain.html", {
        'form': form,
        'c': customer_obj,
    }, context_instance=RequestContext(request))

@login_required
def col_customer_domain_modify(request, customer_id, domain_id):
    obj = ColCustomerDomain.objects.get(id=domain_id)
    form = ColCustomerDomainForm(instance=obj)
    if request.method == "POST":
        form = ColCustomerDomainForm(request.POST, instance=obj)
        if form.is_valid():
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect('{}?customer_id={}'.format(reverse('colcustomer_domain'), customer_id))
            # return HttpResponseRedirect(reverse('colcustomer_domain', args=(customer_id, )))
    return render_to_response("core/col_customer_domain_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def col_customer_domain_batchadd(request, customer_id):
    customer_obj = Customer.objects.get(id=customer_id)

    if request.method == "POST":
        i = 0
        customer = request.POST.get('customer', '')
        for a in customer.split('\n'):
            a = a.replace('\n', '').replace('\r', '').strip().lower()
            if not a:
                continue
            domain, forward_address = a.split(';')[:2]
            _, bool = ColCustomerDomain.objects.get_or_create(customer=customer_obj, domain=domain.strip(),
                                                              forward_address=forward_address.strip())
            if bool:
                i += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加%s个客户域名' % i)
        # return HttpResponseRedirect(reverse('colcustomer_domain', args=(customer_id,)))
        return HttpResponseRedirect('{}?customer_id={}'.format(reverse('colcustomer_domain'), customer_id))
    return render_to_response("core/col_customer_domain_batchadd.html", {
        'c': customer_obj
    }, context_instance=RequestContext(request))


@login_required
def col_customer_domain_change_status(request, customer_id):
    customer_obj = Customer.objects.get(id=customer_id)
    if request.method == "POST":
        status = request.POST.get('status', '')
        id = request.POST.get('id', '')
        obj = ColCustomerDomain.objects.get(id=id, customer=customer_obj)
        if status == 'delete':
            obj.delete()
            msg = u'删除成功'
        elif status == 'abled':
            obj.disabled = False
            obj.save()
            msg = u'启用域名成功'
        elif status == 'disabled':
            obj.disabled = True
            obj.save()
            msg = u'禁用域名成功'

        messages.add_message(request, messages.SUCCESS, msg)
        # return HttpResponseRedirect(reverse('colcustomer_domain', args=(customer_obj.id,)))
        return HttpResponseRedirect('{}?customer_id={}'.format(reverse('colcustomer_domain'), customer_obj.id))
    return HttpResponse('no message')


@login_required
def cluster_list(request):
    id = request.GET.get('id', '')
    if id:
        clusters = Cluster.objects.filter(id=id)
    else:
        clusters = Cluster.objects.all()
    if request.method == "POST":
        cluster_id = request.POST.get('cluster_id', '')
        action = request.POST.get('action', '')
        c_obj = Cluster.objects.get(id=cluster_id)

        # 删除smtp服务器
        if action == 'delete':
            if ClusterIp.objects.filter(cluster=c_obj):
                messages.add_message(request, messages.WARNING, u'该服务器有配置IP,暂不能删除')
            else:
                messages.add_message(request, messages.SUCCESS, u'成功删除服务器:%s' % c_obj.name)
                c_obj.delete()

        # 部署服务器
        if action == 'deploy':
            import os
            import sys
            import subprocess
            import shlex

            if c_obj.deploy_status == 'helo_waiting':
                c_obj.deploy_status = 'helo_deploying'
            else:
                c_obj.deploy_status = 'deploying'
            c_obj.save()

            deploy_file = os.path.join(settings.DEPLOY_DIR, 'deploy.py')
            # cmd = u"""{0:s} {1:s} {2:s}""".format(sys.executable, deploy_file, cluster_id)
            cmd = u"""{0:s} {1:s} {2:s}""".format(settings.PYTHON_PATH, deploy_file, cluster_id)
            args = shlex.split(cmd.encode('utf8'))
            subprocess.Popen(args)

            messages.add_message(request, messages.WARNING, u'服务器(%s)正在部署，请耐心等候！' % c_obj.name)

    return render_to_response("core/cluster_list.html", {
        'clusters': clusters,
    }, context_instance=RequestContext(request))


@login_required
def cluster_add(request):
    form = ClusterForm()
    if request.method == "POST":
        form = ClusterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('cluster_list'))
    return render_to_response("core/cluster_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def cluster_modify(request, cluster_id):
    cluster_obj = Cluster.objects.get(id=cluster_id)
    form = ClusterForm(instance=cluster_obj)
    if request.method == "POST":
        form = ClusterForm(request.POST, instance=cluster_obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('cluster_list'))
    return render_to_response("core/cluster_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def ip_list(request, cluster_id):
    """
    IP管理
    """
    cluster_id = int(cluster_id)
    pools = IpPool.objects.all()
    seach_pool_id = request.GET.get('search_pool_id', '')
    if cluster_id:
        c_obj = Cluster.objects.get(id=cluster_id)
        ip_list = ClusterIp.objects.filter(cluster_id=cluster_id)
    else:
        c_obj = None
        ip_list = ClusterIp.objects.all()
    if seach_pool_id:
        ip_list = ip_list.filter(ip_pool_id=seach_pool_id)
    c_objs = Cluster.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        action = request.POST.get('action', '')
        # 禁用/启用/删除IP
        if action == 'change_status':
            status = int(request.POST.get('status', ''))
            if int(status) == -1:
                ips = ClusterIp.objects.filter(id__in=ids)
                ips.delete()
                msg = u'成功删除%s个IP' % len(ids)
            else:
                ClusterIp.objects.filter(id__in=ids).update(disabled=status)
                tip = u'禁用' if status else u'启用'
                msg = u'成功%s%s个IP' % (tip, len(ids))

        elif action == 'allocate':
            pool_id = request.POST.get('pool_id', '')
            ClusterIp.objects.filter(id__in=ids).update(ip_pool_id=pool_id)
            msg = u'成功分配{}个IP'.format(len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(reverse('ip_list', args=(cluster_id,)))

    return render_to_response("core/ip_list.html", {
        'ip_list': ip_list,
        'c_id': int(cluster_id),
        'c_obj': c_obj,
        'c_objs': c_objs,
        'pools': pools,
    }, context_instance=RequestContext(request))


@login_required
def ip_add(request, cluster_id):
    """
    IP添加
    """
    form = IpSegmentForm()
    cluster = Cluster.objects.get(id=cluster_id)
    if request.method == "POST":
        # 单个IP添加
        if request.POST.get('single', ''):
            ips = request.POST.get('ips', '')
            ips_conf_list = [e.split() for e in ips.split('\n') if len(e.split()) == 4]

            ip_obj_list = []
            for e in ips_conf_list:
                ip = ClusterIp(cluster_id=cluster_id, device=e[0], ip=e[1], netmask=e[2], helo=e[3])
                ip_obj_list.append(ip)
            try:
                ClusterIp.objects.bulk_create(ip_obj_list)

                # 标记需要应用部署
                cluster.deploy_status = 'waiting'
                cluster.save()
            except Exception, e:
                print e.message
            messages.add_message(request, messages.SUCCESS, u"成功添加%s个IP地址!" % len(ips_conf_list))
            return HttpResponseRedirect(reverse('ip_list', args=(cluster_id,)))
        # 按照网段添加
        else:
            form = IpSegmentForm(request.POST)
            if form.is_valid():
                data = form.data
                ip_list = get_ip_list_from_net(data['ip'])
                ip_obj_list = []
                for e in ip_list:
                    ip = ClusterIp(cluster_id=cluster_id, ip=str(e), device=data['device'], netmask=data['netmask'],
                                   helo=(data['helo']).format(*str(e).split('.')), ip_pool_id=data['ip_pool'])
                    ip_obj_list.append(ip)
                # 批量添加如果有重复则单个添加
                total_num = 0
                try:
                    ClusterIp.objects.bulk_create(ip_obj_list)
                    total_num = len(ip_obj_list)
                except Exception, e:
                    for obj in ip_obj_list:
                        try:
                            obj.save()
                            total_num += 1
                        except Exception, e:
                            continue

                if total_num > 0:
                    # 标记需要应用部署
                    cluster.deploy_status = 'waiting'
                    cluster.save()
                messages.add_message(request, messages.SUCCESS, u"成功添加%s个IP地址!" % total_num)
                return HttpResponseRedirect(reverse('ip_list', args=(cluster_id,)))

    return render_to_response("core/ip_add.html", {
        'cluster': cluster,
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def ip_pool_list(request):
    id = request.GET.get('id', '')
    if id:
        ip_pools = IpPool.objects.filter(id=id)
    else:
        ip_pools = IpPool.objects.all()
    if request.method == "POST":
        ip_pool_id = request.POST.get('ip_pool_id', '')
        if ip_pool_id:
            IpPool.objects.get(id=ip_pool_id).delete()
        messages.add_message(request, messages.SUCCESS, u'删除成功')
    return render_to_response("core/ip_pool_list.html", {
        'ip_pools': ip_pools,
    }, context_instance=RequestContext(request))


@login_required
def ip_pool_add(request):
    form = IpPoolForm()
    if request.method == "POST":
        form = IpPoolForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('ip_pool_list'))
    return render_to_response("core/ip_pool_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def ip_pool_modify(request, ip_pool_id):
    ip_pool_obj = IpPool.objects.get(id=ip_pool_id)
    form = IpPoolForm(instance=ip_pool_obj)
    if request.method == "POST":
        form = IpPoolForm(request.POST, instance=ip_pool_obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('ip_pool_list'))
    return render_to_response("core/ip_pool_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def ajax_get_customers(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    type = data.get('type', '')

    customers = get_customer_data(data)
    if search:
        customers = customers.filter(
            Q(username__icontains=search) | Q(company__icontains=search) | Q(id__icontains=search))

    if type == 'relay':
        colums = ['id', 'username', 'ip_count', 'domain_count', 'mailbox_count', 'ip_pool', 'relay_limit',
                  'relay_exceed',
                  'service_end', 'status', 'relay_statistics__count',
                  'created', 'operate_time', 'last_login', 'service_end']
    elif type == 'collect':
        colums = ['id', 'username', 'col_domain_count', 'collect_limit', 'collect_exceed', 'gateway_service_end',
                  'gateway_status',
                  'collect_statistics__count', 'created', 'operate_time', 'last_login', 'service_end']
    else:
        colums = ['id', 'username', 'ip_count', 'domain_count', 'mailbox_count', 'ip_pool', 'relay_limit',
                  'relay_exceed', 'service_end', 'status',
                  'relay_statistics__count', 'col_domain_count', 'collect_limit', 'collect_exceed',
                  'gateway_service_end', 'gateway_status',
                  'collect_statistics__count', 'created', 'operate_time', 'last_login', 'service_end']

    if customers and order_column and int(order_column) < len(colums):
        col_name = colums[int(order_column)]
        if col_name == 'relay_statistics__count':
            customers = customers.filter(relay_statistics__date=datetime.date.today())
        elif col_name == 'collect_statistics__count':
            customers = customers.filter(collect_statistics__date=datetime.date.today())
        if order_dir == 'desc':
            customers = customers.order_by('-%s' % col_name)
        else:
            customers = customers.order_by('%s' % col_name)
    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        page = int(data.get('start', '0')) / length + 1
    except ValueError:
        page = 1

    count = len(customers)

    paginator = Paginator(customers, length)

    try:
        customers = paginator.page(page)
    except (EmptyPage, InvalidPage):
        customers = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    for c in customers.object_list:
        t = TemplateResponse(request, 'core/ajax_get_customers.html', {'c': c, 'type': type})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def route_rule_list(request, ip_pool_id):
    """
    路由规则管理
    """
    ip_pool_id = int(ip_pool_id)
    pools = IpPool.objects.all()
    if ip_pool_id:
        p_obj = IpPool.objects.get(id=ip_pool_id)
        rule_list = RouteRule.objects.filter(ip_pool=p_obj)
    else:
        p_obj = None
        rule_list = RouteRule.objects.all()
    p_objs = IpPool.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        action = request.POST.get('action', '')
        # 禁用/启用/删除路由规则
        if action == 'change_status':
            status = int(request.POST.get('status', ''))
            if int(status) == -1:
                ips = RouteRule.objects.filter(id__in=ids)
                ips.delete()
                msg = u'成功删除%s条路由规则' % len(ids)
            else:
                RouteRule.objects.filter(id__in=ids).update(disabled=status)
                tip = u'禁用' if status else u'启用'
                msg = u'成功%s%s条路由规则' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(reverse('route_rule_list', args=(ip_pool_id,)))
    return render_to_response("core/route_rule_list.html", {
        'rule_list': rule_list,
        'p_id': int(ip_pool_id),
        'p_obj': p_obj,
        'p_objs': p_objs,
        'pools': pools,
    }, context_instance=RequestContext(request))


@login_required
def route_rule_add(request):
    ip_pool_id = request.GET.get('ip_pool_id', 0)
    try:
        ip_pool = IpPool.objects.get(id=ip_pool_id)
        form = RouteRuleForm(initial={'ip_pool': ip_pool})
    except BaseException, e:
        form = RouteRuleForm()
    if request.method == "POST":
        form = RouteRuleForm(request.POST)
        if form.is_valid():
            customer = form.save()
            # 为新用户分配发送池
            allocate_ippool_for_customer(customer.id)
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('route_rule_list', args=(ip_pool_id,)))
    return render_to_response("core/route_rule_modify.html", {
        'form': form,
        'ip_pool_id': ip_pool_id
    }, context_instance=RequestContext(request))


@login_required
def route_rule_modify(request, id):
    obj = RouteRule.objects.get(id=id)
    ip_pool_id = obj.ip_pool.id
    form = RouteRuleForm(instance=obj)
    if request.method == "POST":
        form = RouteRuleForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('route_rule_list', args=(ip_pool_id,)))
    return render_to_response("core/route_rule_modify.html", {
        'form': form,
        'ip_pool_id': ip_pool_id
    }, context_instance=RequestContext(request))


@login_required
def customer_setting(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    setting = customer.customer_setting
    # setting, _ = CustomerSetting.objects.get_or_create(customer=customer)
    form = CustomerSettingForm(instance=setting)
    if request.method == "POST":
        form = CustomerSettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('customer_list') + "?customer_id={}".format(customer_id))
    return render_to_response("core/customer_setting.html", {
        'form': form,
        'customer': customer
    }, context_instance=RequestContext(request))


@login_required
def postfix_status(request):
    res = PostfixStatus.objects.filter(date__gte=(datetime.date.today() - datetime.timedelta(days=10)))
    return render_to_response("core/postfix_status.html", {
        'res': res
    }, context_instance=RequestContext(request))


@login_required
def customer_password_modify(request, customer_id):
    user_obj = Customer.objects.get(id=customer_id)
    form = SetPasswordForm(user=user_obj)
    if request.method == "POST":
        form = SetPasswordForm(user_obj, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('customer_list') + "?customer_id={}".format(customer_id))
    return render_to_response("core/password_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def postfix_search(request):
    form = PostfixSearchForm()
    iframe_url = ''
    if request.method == "POST":
        form = PostfixSearchForm(request.POST)
        if form.is_valid():
            server_id = form.cleaned_data['server_id']
            search = form.cleaned_data['search']
            date = form.cleaned_data.get('date', '')
            server_name = settings.__getattr__('WEB_{}'.format(server_id.upper()))
            iframe_url = 'http://{}/core/get_postfix_search?search={}&date={}'.format(server_name, search, date)
    return render_to_response("core/postfix_search.html", {
        'form': form,
        'iframe_url': iframe_url
    }, context_instance=RequestContext(request))


@login_required
def get_postfix_search(request):
    search = request.GET.get('search', '')
    date = request.GET.get('date', '')
    date_list = []
    date_str = ''
    if date:
        try:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
            date_str = u'%s %2d' % (date.strftime('%b'), int(date.strftime('%d')))
            date_list = [date.strftime('%Y%m%d'), (date + datetime.timedelta(days=1)).strftime('%Y%m%d'), 'log']
        except:
            pass
    res = []
    search_list = [search, date_str] if date_str else [search, ]
    if search:
        log_files = filter(lambda f: f.startswith('postfix'), os.listdir('/var/log/'))
        for f in log_files:
            if date_list:
                for l in date_list:
                    if f.endswith(l):
                        break
                else:
                    continue
            f = '/var/log/{}'.format(f)
            num, _ = my_grep1(f, search_list, 1000)
            res.extend(_)
    return render_to_response("core/get_postfix_search.html", {
        'res': res,
    }, context_instance=RequestContext(request))


@login_required
def notice_list(request):
    notices = Notification.objects.filter(manager=request.user)
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
                Notification.objects.filter(manager=request.user, id=id).delete()
                messages.add_message(request, messages.SUCCESS, u'删除成功')
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
    is_mynotice = data.get('is_mynotice', '')
    if is_mynotice:
        notices = Notification.objects.filter(manager=user)
    else:
        notices = Notification.objects.all()
    if id:
        notices = notices.filter(id=id)
    if search:
        notices = notices.filter(
            Q(subject__icontains=search) | Q(content__icontains=search))

    if is_mynotice:
        colums = ['id', 'subject', 'content', 'is_sms', 'is_email', 'created', 'id']
    else:
        colums = ['id', 'subject', 'content', 'is_sms', 'is_email', 'customer', 'manager', 'created', 'id']

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


@login_required
def notice_history(request):
    notices = get_notices(request.GET, request.user)
    if request.method == "POST":
        action = request.POST.get('action', '')
        if action == 'delete':
            id = request.POST.get('id', '')
            if id:
                Notification.objects.filter(id=id).delete()
                messages.add_message(request, messages.SUCCESS, u'删除成功')
                return HttpResponseRedirect(reverse('notice_history'))
    return render_to_response("core/notice_history.html", {
        'notices': notices,
    }, context_instance=RequestContext(request))


@login_required
def ordered_model(request, app, model, id, move):
    next = request.GET.get('next', '/')
    model = get_model(app, model)
    obj = get_object_or_404(model, pk=unquote(id))
    obj.move(move)
    messages.add_message(request, messages.SUCCESS, u'排序成功')
    return HttpResponseRedirect(next)


@login_required
def batch_ordered_model(request, app, model):
    data = request.POST
    next = data.get('next', '/')
    id = data.get('id', '')
    ids = data.get('ids', '')
    model = get_model(app, model)
    obj = get_object_or_404(model, pk=unquote(id))
    move = obj.order
    if ids:
        objs = model.objects.filter(id__in=ids.split(',')).order_by('-order')
        for o in objs:
            o.refresh_from_db(fields=('order', ))
            o.to(move)
            try:
                move_self = o.order_by_self()
                if move_self:
                    move = move_self
            except:
                move = o.order
    messages.add_message(request, messages.SUCCESS, u'排序成功')
    return HttpResponseRedirect(next)


def validate_key(auth_key, auth_string):
    """
    安全认证：查看客户端key和服务器端key是否相同
    """
    auth_string_server = hashlib.md5('%s-%s' % (auth_key, datetime.datetime.now().strftime("%Y%m%d"))).hexdigest()
    return True if auth_string == auth_string_server else False


def spam_check(request):
    auth_string = request.GET.get('auth', '')
    auth_key = settings.AUTH_KEY
    if not validate_key(auth_key, auth_string):
        return HttpResponse(u'认证失败')
    sender = request.POST.get('sender', '') or request.GET.get('sender', '')
    receiver = request.POST.get('receiver') or request.GET.get('receiver', '')
    message = request.POST.get('message') or request.GET.get('message', '')
    mail = {
        'sender': sender,
        'receiver': [receiver],
        'message': message
    }
    res = check.check_edm_mail(mail)
    res['status'] = True
    return serialize(res)


@login_required
def ajax_get_customer_status(request):
    customers = get_customer_data(request.GET)
    customer_status = customers.values("status").annotate(Count("id")).order_by()
    customers = customers.annotate(ip_count=Count('ip'), domain_count=Count('domain'), mailbox_count=Count('mailbox'),
                                   col_domain_count=Count('col_domain'))
    relay_count = customers.filter(Q(ip_count__gt=0) | Q(domain_count__gt=0) | Q(mailbox__gt=0)).count()
    collect_count = customers.filter(col_domain_count__gt=0).count()
    all_count = customers.filter(Q(ip_count__gt=0) | Q(domain_count__gt=0) | Q(mailbox__gt=0)).filter(
        col_domain_count__gt=0).count()

    t = TemplateResponse(request, 'core/ajax_get_customer_status.html', {
        'customers': customers,
        'customer_status': customer_status,
        'relay_count': relay_count,
        'collect_count': collect_count,
        'all_count': all_count,
    })
    t.render()
    return HttpResponse(json.dumps({'html': t.content}), content_type="application/json")


@login_required
def customer_localized_setting(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    setting = customer.customer_localized_setting
    if not setting.token:
        setting.token = get_random_string(20)
        setting.save()
    # setting, _ = CustomerSetting.objects.get_or_create(customer=customer)
    form = CustomerLocalizedSettingForm(instance=setting)
    if request.method == "POST":
        form = CustomerLocalizedSettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('customer_list') + "?customer_id={}".format(customer_id))
    return render_to_response("core/customer_localized_setting.html", {
        'form': form,
        'customer': customer
    }, context_instance=RequestContext(request))


def get_customer_summary(data):
    date_end = data.get('date_end', '')
    date_start = data.get('date_start', '')
    username = data.get('username', '')
    customer_id = data.get('customer_id', '')
    is_relay_limit = data.get('is_relay_limit', '')
    is_collect_limit = data.get('is_collect_limit', '')
    is_limit = data.get('is_limit', '')
    is_all = data.get('is_all', '')
    is_rid_tmp = data.get('is_rid_tmp', '')
    if date_end or date_start:
        is_all = ''
    if not date_end:
        date_end = datetime.datetime.today() - datetime.timedelta(days=1)
    else:
        date_end = datetime.datetime.strptime(date_end.replace('-', ''), '%Y%m%d')
    if not date_start:
        date_start = date_end
    else:
        date_start = datetime.datetime.strptime(date_start.replace('-', ''), '%Y%m%d')
    if is_all:
        lists = CustomerSummary.objects.all()
    else:
        lists = CustomerSummary.objects.filter(date__lte=date_end, date__gte=date_start)
    if is_rid_tmp:
        lists = lists.exclude(customer__company__icontains=u'临时信任')
    if username:
        lists = lists.filter(Q(customer__username__icontains=username) | Q(customer__company__icontains=username))
    if customer_id:
        lists = lists.filter(customer_id=customer_id)
    if is_relay_limit:
        lists = lists.filter(is_relay_limit=True)
    if is_collect_limit:
        lists = lists.filter(is_collect_limit=True)
    if is_limit:
        lists = lists.filter(Q(is_collect_limit=True) | Q(is_relay_limit=True))
    return lists


@login_required
def customer_summary(request):
    data = request.GET
    lists = get_customer_summary(data)
    lists = lists.aggregate(relay_avg=Avg('relay_count'), collect_avg=Avg('collect_count'))
    return render_to_response("core/customer_summary.html", {
        'form': CustomerSummarySearchForm(data),
        'lists': lists
    }, context_instance=RequestContext(request))


@login_required
def ajax_get_customer_summary(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    type = data.get('type', '')

    lists = get_customer_summary(data)
    if search:
        lists = lists.filter(
            Q(customer__username__icontains=search) | Q(customer__company__icontains=search))

    colums = ['id', 'customer__username', 'relay_limit', 'relay_count', 'is_relay_limit', 'collect_limit',
              'collect_count', 'is_collect_limit', 'customer__sale', 'date']

    if lists and order_column and int(order_column) < len(colums):
        col_name = colums[int(order_column)]
        if order_dir == 'desc':
            lists = lists.order_by('-%s' % col_name)
        else:
            lists = lists.order_by('%s' % col_name)
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
    for l in lists.object_list:
        t = TemplateResponse(request, 'core/ajax_get_customer_summary.html', {'l': l, 'type': type})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

@login_required
def ajax_get_smtp_status(request):
    id = request.GET.get('id', '')
    timeout = 10
    if id:
        cluster = Cluster.objects.get(id=id)
        api_url = cluster.api_url
        if not api_url:
            api_url = "http://%s:10001/state/" % cluster.ip
        try:
            res = json.loads(urllib2.urlopen(api_url, timeout=timeout).read())
            msg = u'''总数:<code>{detail}</code> 已接收:<code>{received}</code>  等待发送:<code>{waiting}</code>
            已发送:<code>{delivered}</code> 日志回传:<code>{logging}</code> 重试:<code>{retry_waiting}</code>
            '''.format(**res)
        except:
            msg = u'获取异常'

    return HttpResponse(json.dumps({'msg': msg}, ensure_ascii=False), content_type="application/json")


@login_required
def auditlog(request, template_name='core/auditlog.html'):
    """
    操作日志记录
    :param request:
    :param template_name:
    :return:
    """
    form = AuditLogSearchForm(request.GET)
    return render_to_response(template_name, {
        'form': form
    }, context_instance=RequestContext(request))


def get_auditlog(data, user):
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    content_type = data.get('content_type', '')
    id = data.get('id', '')
    logs = LogEntry.objects
    if content_type:
        app_label, model_name = content_type.split('.')
        model = dapps.get_model(app_label, model_name)
        if id:
            logs = logs.get_for_relate_object(model.objects.get(id=id))
        else:
            logs = logs.get_for_relate_model(model)
    else:
        logs = logs.all()
    if search:
        logs = logs.filter(
            Q(remote_addr__icontains=search) | Q(changes__icontains=search))

    colums = ['id', 'relate_content_type', 'changes', 'action', 'actor', 'remote_addr', 'timestamp']

    if logs and order_column and int(order_column) < len(colums):
        col_name = colums[int(order_column)]
        if order_dir == 'desc':
            logs = logs.order_by('-%s' % col_name)
        else:
            logs = logs.order_by('%s' % col_name)
    return logs


@login_required
def ajax_get_auditlog(request):
    data = request.GET
    logs = get_auditlog(data, request.user)

    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        page = int(data.get('start', '0')) / length + 1
    except ValueError:
        page = 1

    count = len(logs)

    paginator = Paginator(logs, length)

    try:
        logs = paginator.page(page)
    except (EmptyPage, InvalidPage):
        logs = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    for n in logs.object_list:
        t = TemplateResponse(request, 'core/ajax_get_auditlog.html', {'n': n, 'type': type})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")
