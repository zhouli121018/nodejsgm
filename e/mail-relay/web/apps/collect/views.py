#coding=utf-8
import datetime
import re
import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.context import RequestContext
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template.response import TemplateResponse
from django.db.models import Q, Count

from models import ColCustomer, ColCustomerDomain, ColCustomerSetting

from forms import ColCustomerDomainForm, ColCustomerSearchForm, ColCustomerForm, ColCustomerSettingForm

@login_required
def customer_list(request):
    customers = get_customer_data(request.GET)
    customer_status = customers.values("status").annotate(Count("id")).order_by()

    form = ColCustomerSearchForm(request.GET)
    if request.method == "POST":
        action = request.POST.get('action', '')
        if action == 'delete':
            customer_id = request.POST.get('customer_id', '')
            if customer_id:
                ColCustomerDomain.objects.filter(customer_id=customer_id).delete()
                ColCustomer.objects.get(id=customer_id).delete()
            messages.add_message(request, messages.SUCCESS, u'删除成功')
        return HttpResponseRedirect(reverse('col_customer_list'))
    return render_to_response("collect/customer_list.html", {
        'customers': customers,
        'customer_status': customer_status,
        'form': form
    }, context_instance=RequestContext(request))


def get_customer_data(data):
    username = data.get('username', '')
    customer_id = data.get('customer_id', '')
    forward_address = data.get('forward_address', '')
    domain = data.get('domain', '')
    status = data.get('status', '')
    customers = ColCustomer.objects.all()
    if username:
        customers = customers.filter(Q(username__icontains=username) | Q(company__icontains=username))
    if customer_id:
        customers = customers.filter(id=customer_id)
    if forward_address:
        customers = customers.filter(domain__forward_address__icontains=forward_address)
    if domain:
        customers = customers.filter(domain__domain__icontains=domain)
    if status:
        customers = customers.filter(status=status)
    return customers

@login_required
def customer_add(request):
    form = ColCustomerForm()
    if request.method == "POST":
        form = ColCustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('col_customer_list'))
    return render_to_response("collect/customer_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def customer_modify(request, customer_id):
    customer_obj = ColCustomer.objects.get(id=customer_id)
    form = ColCustomerForm(instance=customer_obj)
    if request.method == "POST":
        form = ColCustomerForm(request.POST, instance=customer_obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('col_customer_list'))
    return render_to_response("collect/customer_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def customer_domain(request, customer_id):
    customer_obj = ColCustomer.objects.get(id=customer_id)
    form = ColCustomerDomainForm()
    if request.method == "POST":
        form = ColCustomerDomainForm(request.POST)
        if form.is_valid():
            ColCustomerDomain(customer=customer_obj, domain=form.data['domain'], forward_address=form.data['forward_address']).save()
            messages.add_message(request, messages.SUCCESS, u'添加成功')
            return HttpResponseRedirect(reverse('col_customer_domain', args=(customer_obj.id,)))
    return render_to_response("collect/customer_domain.html", {
        'form': form,
        'c': customer_obj,
    }, context_instance=RequestContext(request))

@login_required
def customer_domain_batchadd(request, customer_id):
    customer_obj = ColCustomer.objects.get(id=customer_id)

    if request.method == "POST":
        i = 0
        customer = request.POST.get('customer', '')
        for a in customer.split('\n'):
            a = a.replace('\n', '').replace('\r', '').strip().lower()
            if not a:
                continue
            domain, forward_address = a.split(';')[:2]
            _, bool = ColCustomerDomain.objects.get_or_create(customer=customer_obj, domain=domain.strip(), forward_address=forward_address.strip())
            if bool:
                i += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加%s个客户域名' % i)
        return HttpResponseRedirect(reverse('col_customer_domain', args=(customer_id,)))
    return render_to_response("collect/customer_domain_batchadd.html", {
        'c': customer_obj
    }, context_instance=RequestContext(request))


@login_required
def customer_domain_change_status(request, customer_id):
    customer_obj = ColCustomer.objects.get(id=customer_id)
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
        return HttpResponseRedirect(reverse('col_customer_domain', args=(customer_obj.id,)))
    return HttpResponse('no message')



@login_required
def ajax_get_customers(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')

    customers = get_customer_data(data)
    if search:
        customers = customers.filter(Q(username__icontains=search) | Q(company__icontains=search) | Q(id__icontains=search))

    colums = ['id', 'username', 'customer_ip', 'customer_domain', 'customer_mailbox', 'service_start', 'created', 'ip_pool', 'service_end', 'disabled']

    if customers and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            customers = customers.order_by('-%s' % colums[int(order_column)])
        else:
            customers = customers.order_by('%s' % colums[int(order_column)])
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
        t = TemplateResponse(request, 'collect/ajax_get_customers.html', {'c': c})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def customer_setting(request, customer_id):
    customer = ColCustomer.objects.get(id=customer_id)
    setting = ColCustomerSetting.objects.get(customer=customer)
    form = ColCustomerSettingForm(instance=setting)
    if request.method == "POST":
        form = ColCustomerSettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('col_customer_list'))
    return render_to_response("collect/customer_setting.html", {
        'form': form,
        'customer': customer
    }, context_instance=RequestContext(request))
