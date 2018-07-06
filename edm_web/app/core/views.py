# -*- coding:utf-8 -*-
import re
import json
import random
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib import messages
from django_redis import get_redis_connection
from app.core.models import CustomerDomain, DefaultMailbox, CustomerMailbox, CustomerTrackDomain, MailAccurateService, CustomerDomainMailboxRel
from app.core.forms import CustomerDomainForm
from lib.tools import GenDkimKeys, valid_domain, get_random_string
from lib.common import get_object
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.template.response import TemplateResponse
from tagging.models import TagCategory, Tag, TaggedItem
from app.template.models import SendTemplate
from app.address.models import MailList
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from app.core.utils import caches, validators

# 发送域名列表
@login_required
def send_domain(request):
    if request.method == "POST":
        domain = request.POST.get('domain', '')
        action = request.POST.get('action', '')
        id = request.POST.get('id', '')
        if request.user.service().is_umail:
            messages.add_message(request, messages.ERROR, _(u'测试帐号不允许此类操作!'))
            return HttpResponseRedirect(reverse('send_domain'))
        if id:
            obj = get_object(CustomerDomain, request.user, id)
        if action == 'track_delete':
            track_id = request.POST.get('track_id', '')
            trackobj = get_object(CustomerTrackDomain, request.user, track_id)
            trackobj.delete()
            messages.add_message(request, messages.SUCCESS, _(u'跟踪域名:%(domain)s　删除成功!') % {'domain': trackobj.domain})
        elif action == 'track_default':
            track_id = request.POST.get('track_id', '')
            trackobj = get_object(CustomerTrackDomain, request.user, track_id)
            trackobj.isdefault = True
            trackobj.save()
            messages.add_message(request, messages.SUCCESS, _(u'跟踪域名:%(domain)s　设置默认成功!') % {'domain': trackobj.domain})
        elif action == 'track_default_false':
            track_id = request.POST.get('track_id', '')
            trackobj = get_object(CustomerTrackDomain, request.user, track_id)
            trackobj.isdefault = False
            trackobj.save()
            messages.add_message(request, messages.SUCCESS, _(u'跟踪域名:%(domain)s　关闭默认成功!') % {'domain': trackobj.domain})
        elif action == 'add':
            domain = domain.strip()
            if not validators.check_domains(domain):
                messages.add_message(request, messages.ERROR, _(u'添加失败，域名%(domain)s格式错误！')% {'domain': domain} )
                return HttpResponseRedirect(reverse('send_domain'))
            if CustomerDomain.objects.filter(domain=domain, customer=request.user):
                messages.add_message(request, messages.ERROR, _(u'添加失败，发送域名重复添加！'))
            else:
                private_key, public_key = GenDkimKeys()
                public_key = 'k=rsa;p={}'.format(public_key)
                CustomerDomain.objects.create(
                    customer=request.user,
                    domain=domain,
                    dkim_private=private_key,
                    dkim_public=public_key
                )
                messages.add_message(request, messages.SUCCESS, _(u'发送域名添加成功'))
        elif action == 'valid_domain':
            if not validators.check_domains(obj.domain):
                messages.add_message(request, messages.ERROR, _(u'该域名%(domain)s格式错误，无法验证！')% {'domain': domain} )
                return HttpResponseRedirect(reverse('send_domain'))
            # 判断是否有相同已验证通过的域名
            if CustomerDomain.objects.exclude(id=id).filter(domain=obj.domain, status__in=['Y', 'T']):
                obj.status = 'f'
                obj.save()
                messages.add_message(request, messages.ERROR, _(u'该域名:%(domain)s 已被其他客户占用，无法验证!') % {'domain': obj.domain})
            else:
                obj.is_spf = 'Y' if valid_domain(obj.domain, 'spf', 'include:spf.bestedm.org') else 'f'
                obj.is_mx = 'Y' if valid_domain(obj.domain, 'mx', 'mail.bestedm.org') else 'f'
                obj.is_dkim = 'Y' if valid_domain(obj.domain, 'dkim', obj.dkim_public, dkim_selector=obj.dkim_selector) else 'f'
                res = True if obj.is_spf == 'Y' and obj.is_mx == 'Y' else False
                obj.status = 'Y' if res else 'f'
                obj.save()
                if res:
                    loglevel = messages.SUCCESS
                    obj.api_sync('add-domain')
                    add_count = gen_mailbox(obj)
                    message = _(u'域名:%(domain)s, 验证通过!并随机生成%(count)d个账号!') % {'domain': obj.domain, 'count': add_count}
                else:
                    message = _(u'域名:%(domain)s, 验证未通过!') % {'domain': obj.domain}
                    loglevel = messages.WARNING
                messages.add_message(request, loglevel, message)
        elif action == 'delete':
            messages.add_message(request, messages.SUCCESS, _(u'域名:%(domain)s　删除成功!') % {'domain': obj.domain})
            CustomerMailbox.objects.filter(customer=request.user, domain=obj.domain).delete()
            obj.api_sync('del-domain')
            obj.delete()
        elif action == 'gen_mailbox':
            total = 0
            for a in DefaultMailbox.objects.all():
                mailbox = '{}@{}'.format(a.account, obj.domain)
                if not CustomerMailbox.objects.filter(mailbox=mailbox, disabled='0'):
                    m_obj = CustomerMailbox(
                        customer=request.user,
                        domain=obj.domain,
                        name=a.account,
                        mailbox=mailbox,
                        password=get_random_string(10)
                    )
                    m_obj.save()
                    m_obj.api_sync('add-mailbox')
                    total += 1
            messages.add_message(request, messages.SUCCESS, _(u'域名:%(domain)s　成功随机生成%(count)d个账号!') % {'domain': obj.domain, 'count': total})

        return HttpResponseRedirect(reverse('send_domain'))

    lists = CustomerDomain.objects.filter(customer=request.user)
    count = lists.count()
    # 共享域名以及获取发件人
    ctype = CustomerDomainMailboxRel.objects.get_content_type('domain')
    share_domain_ids = CustomerDomainMailboxRel.objects.filter(customer=request.user, content_type=ctype).values_list('object_id', flat=True)
    share_lists = CustomerDomain.objects.filter(customer=request.user.parent, id__in=share_domain_ids, status__in=['Y', 'T'])
    for obj in share_lists:
        count += 1
        obj.no_index = count

    form = CustomerDomainForm()
    # 获取系统域名
    domain_list = CustomerMailbox.objects.filter(customer=request.user).values_list('domain', flat=True).distinct()
    sys_domain_list = CustomerDomain.objects.filter(domain__in=list(domain_list), customer_id=0)

    track_domain_list = CustomerTrackDomain.objects.filter(customer=request.user)
    return render(request, template_name='core/senddomain_list.html', context={
        'lists': lists,
        'share_lists': share_lists,
        'form': form,
        'sys_domain_list': sys_domain_list,
        'track_domain_list': track_domain_list,
    })


def gen_mailbox(obj):
    total = 0
    for a in DefaultMailbox.objects.all():
        mailbox = '{}@{}'.format(a.account, obj.domain)
        if not CustomerMailbox.objects.filter(mailbox=mailbox, disabled='0'):
            m_obj = CustomerMailbox.objects.create(
                customer=obj.customer,
                domain=obj.domain,
                name=a.account,
                mailbox=mailbox,
                password=get_random_string(10)
            )
            m_obj.api_sync('add-mailbox')
            total += 1
    return total

@login_required
def core_mailbox_add(request):
    domain = request.GET.get('domain', '')
    is_share = request.GET.get('is_share', '')
    if is_share=='1':
        is_not_share = False
        domains = CustomerDomain.objects.filter(domain=domain, customer=request.user.parent)
        if not domains:
            raise Http404
    else:
        is_not_share = True
        domains = CustomerDomain.objects.filter(domain=domain, customer_id__in=[0, request.user.id])
        if not domains:
            raise Http404
    # 判读是不是系统域名
    is_sys = True if domains[0].customer_id == 0 else False
    lists = CustomerMailbox.objects.filter(customer=request.user, domain=domain).order_by('-id')
    is_customer_add = True if lists.count() < 20 else False

    if request.method == "POST":
        action = request.POST.get('action', '')
        id = request.POST.get('id', '')
        if request.user.service().is_umail:
            messages.add_message(request, messages.ERROR, _(u'测试帐号不允许此类操作!'))
            return HttpResponseRedirect('/core/mailbox/add/?domain={}'.format(domain))

        if action == 'sub_del' and id: # 删除共享发件人
            obj = get_object(CustomerMailbox, request.user.parent, id)
            ctype = CustomerDomainMailboxRel.objects.get_content_type('mailbox')
            CustomerDomainMailboxRel.objects.filter(customer=request.user, content_type=ctype, object_id=id).delete()

            box_ids = CustomerDomainMailboxRel.objects.filter(customer=request.user, content_type=ctype).values_list('object_id', flat=True)
            box_count = CustomerMailbox.objects.filter(customer=request.user.parent, domain=domain, id__in=box_ids).count()
            messages.add_message(request, messages.SUCCESS, _(u'删除账号( %(mailbox)s )成功') % {'mailbox': obj.mailbox })
            if box_count:
                return HttpResponseRedirect('/core/mailbox/add/?domain={}&is_share={}'.format(domain, is_share))
            else:
                domain_obj = CustomerDomain.objects.filter(customer=request.user.parent, domain=domain).first()
                if domain_obj:
                    domain_ctype = CustomerDomainMailboxRel.objects.get_content_type('domain')
                    CustomerDomainMailboxRel.objects.filter(customer=request.user, content_type=domain_ctype, object_id=domain_obj.id).delete()
                return HttpResponseRedirect(reverse('send_domain'))

        password = request.POST.get('input_password', '')
        domain = request.POST.get('domain', '')
        mailbox = request.POST.get('input_mailbox', '').strip()
        ids = request.POST.get('ids', '')

        if action == 'sub_alter' and id:
            obj = get_object(CustomerMailbox, request.user.parent, id)
            obj.password = password
            obj.save()
            obj.api_sync('set-mailbox-pass')
            messages.add_message(request, messages.SUCCESS, _(u'修改账号密码成功'))
            return HttpResponseRedirect('/core/mailbox/add/?domain={}&is_share={}'.format(domain, is_share))

        if id:
            obj = get_object(CustomerMailbox, request.user, id)
        if action == 'del':
            messages.add_message(request, messages.SUCCESS, _(u'删除账号( %(mailbox)s )成功') % {'mailbox': obj.mailbox })
            obj.api_sync('del-mailbox')
            obj.delete()
        elif action == 'alter':
            obj.password = password
            obj.save()
            obj.api_sync('set-mailbox-pass')
            messages.add_message(request, messages.SUCCESS, _(u'修改账号密码成功'))
        elif action == 'add':
            #系统域名禁止添加账号
            if is_sys:
                raise Http404
            num = random.randint(10, 32)
            password=get_random_string(num)
            obj = CustomerMailbox(
                customer=request.user,
                domain=domain,
                name=mailbox,
                mailbox='{}@{}'.format(mailbox, domain),
                password=password,
                disabled='0'
            )
            obj.api_sync('add-mailbox')
            obj.save()
            messages.add_message(request, messages.SUCCESS, _(u'新增账号成功'))
        elif action == 'muldel':
            ids = ids.split(',')
            for d in CustomerMailbox.objects.filter(id__in=ids):
                d.api_sync('del-mailbox')
                d.delete()
            messages.add_message(request, messages.SUCCESS, _(u'批量删除成功'))
        return HttpResponseRedirect('/core/mailbox/add/?domain={}'.format(domain))

    return render(request, template_name='core/core_mailbox_add.html', context={
        'domain': domain,
        'is_sys': is_sys,
        'is_customer_add': is_customer_add,
        'is_not_share': is_not_share,
    })

@login_required
def ajax_core_mailbox(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    domain = data.get('domain', '')

    is_share = request.GET.get('is_share', '')
    if is_share == '1':
        is_not_share = False
        ctype = CustomerDomainMailboxRel.objects.get_content_type('mailbox')
        box_ids = CustomerDomainMailboxRel.objects.filter(customer=request.user, content_type=ctype).values_list('object_id', flat=True)
        lists = CustomerMailbox.objects.filter(customer=request.user.parent, domain=domain, id__in=box_ids)
    else:
        is_not_share = True
        lists = CustomerMailbox.objects.filter(customer=request.user, domain=domain)
    if search:
        lists = lists.filter(mailbox__icontains=search)

    colums = ['id', 'id', 'mailbox', 'mailbox', 'disabled']
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
        page = int(data.get('start', '0')) / length + 1
    except ValueError:
        page = 1

    count = lists.count()

    paginator = Paginator(lists, length)

    try:
        lists = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lists = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    number = length * (page - 1) + 1
    for d in lists.object_list:
        t = TemplateResponse(request, 'core/ajax_core_mailbox.html', {'l': d, 'number': number, 'is_not_share': is_not_share,})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
        number += 1
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def ajax_check_mailbox(request):
    domain = request.POST.get('domain', '')
    mailbox = request.POST.get('mailbox', '').strip()
    msg = {'msg': 'Y'}
    if CustomerMailbox.objects.filter(
            customer=request.user, domain=domain).count() >= 20:
        msg = {'msg': 'C'}
    elif CustomerMailbox.objects.filter(
            customer=request.user, domain=domain,
            mailbox='{}@{}'.format(mailbox, domain)).exists():
        msg = {'msg': 'N'}
    return HttpResponse(json.dumps(msg), content_type="application/json")

@login_required
def track_domain_add(request):
    domain = request.POST.get('track_domain', '').strip()
    CustomerTrackDomain.objects.create(
        customer=request.user,
        domain = domain
    )
    messages.add_message(request, messages.SUCCESS, _(u'跟踪统计链接域名添加成功'))
    return HttpResponseRedirect(reverse('send_domain'))

@login_required
def ajax_track_domain_add_check(request):
    domain = request.GET.get('domain', '')
    if domain in ['comingchina.com', 'magvision.com', 'bestedm.org']:
        return HttpResponse(json.dumps({'res': 'M'}), content_type="application/json")
    r = re.compile(r'.*?(\.comingchina.com|\.magvision.com|\.bestedm.org)$')
    if r.search(domain):
        return HttpResponse(json.dumps({'res': 'M'}), content_type="application/json")
    _existed = CustomerTrackDomain.objects.filter(customer=request.user, domain=domain).exists()
    if _existed:
        res = 'N'
    else:
        r = valid_domain(domain, 'cname', record='count1.bestedm.org') or valid_domain(domain, 'cname', record='count.bestedm.org')
        res = 'success' if r else 'fail'
    return HttpResponse(json.dumps({'res': res}), content_type="application/json")

# 打开第三级标签
@login_required
def tagging_open_three(request):
    obj_id = request.GET.get('obj_id', '')
    tag_type = request.GET.get('tag_type', '')
    parent_id = request.GET.get('parent_id', '')
    child_ids = request.GET.get('child_ids', '')
    tag_obj = Tag.objects.get(id=parent_id)
    tag_lists = caches.cache_child_tags(parent_id)
    select_ids = map(int, child_ids.split(',')) if child_ids else []
    tag_vals = { '{}'.format(obj.id): {'name': obj.name, 'p_name': obj.parent.name } for obj in tag_lists}
    return render(request, template_name='core/tagging_open_three.html', context={
        'tag_obj': tag_obj,
        'tag_type': tag_type,
        'tag_lists': tag_lists,
        'parent_id': parent_id,
        'obj_id': obj_id,
        'select_ids': select_ids,
        'tag_vals': json.dumps(tag_vals),
    })

@login_required
def tag_customer(request):
    if not request.session.get('is_admin', ''):
        raise Http404
    if request.method == "POST":
        names = request.POST.getlist('names[]', '')
        action = request.POST.get('action', '')
        tag = request.POST.get('tag', '')
        tag_id = request.POST.get('tag_id', '')
        tag_type = request.POST.get('tag_type', '')
        obj_id = request.POST.get('obj_id', '')
        if tag_type == 'customer':
            tag_obj = request.user
        elif tag_type == 'template':
            tag_obj = SendTemplate.objects.get(id=obj_id)
        elif tag_type == 'address':
            tag_obj = MailList.objects.get(id=obj_id)

        ctype = ContentType.objects.get_for_model(tag_obj)
        if action == 'delete':
            TaggedItem.objects.filter(tag_id=tag_id, content_type=ctype, object_id=tag_obj.id).delete()
        else:
            TaggedItem.objects.filter(content_type=ctype, object_id=tag_obj.id).delete()
            for tag_id in names:
                remark = request.POST.get('remark_{}'.format(tag_id), '').strip()
                remark = remark if remark else None
                TaggedItem.objects.get_or_create(tag_id=tag_id, content_type=ctype, object_id=tag_obj.id, remark=remark)
                names2 = request.POST.getlist(u'name{}[]'.format(tag_id), '')
                for tag_id2 in names2:
                    TaggedItem.objects.get_or_create(tag_id=tag_id2, content_type=ctype, object_id=tag_obj.id, remark=None)

        t = TemplateResponse(request, 'core/ajax_get_tag_info.html', {'tag_obj': tag_obj, 'tag_type': tag_type,})
        t.render()
        return HttpResponse(json.dumps({'html': t.content}), content_type="application/json")

    tag_type = request.GET.get('tag_type', '')
    obj_id = request.GET.get('obj_id', '')
    tag_lists = caches.cache_parent_tags(tag_type=tag_type, is_show=False)
    seach_tags = []
    if tag_type == 'address':
        seach_tags = caches.cache_search_address_tags()
    return render(request, template_name='core/tag_customer.html', context={
        'tag_lists': tag_lists,
        'tag_type': tag_type,
        'obj_id': obj_id,
        'seach_tags': seach_tags,
    })

@login_required
def ajax_tag_search(request):
    s = request.GET.get("s", "")
    slist = [ i.strip() for i in s.split("|") if i.strip() ]
    html = u""
    duplicate = []
    for s in slist:
        lists = Tag.objects.filter(category__category='address').filter(name__contains=s)
        for d in lists:
            tag_id = d.id
            if tag_id in duplicate: continue
            duplicate.append(tag_id)
            has_parent = d.parent and '1' or ''
            parent_id = has_parent and d.parent_id or tag_id
            parent_name = has_parent and d.parent.name or ''
            tag_name = has_parent and u"{} > {}".format(parent_name, d.name) or d.name
            html += u'''<span onclick="changeSearchLists('{category_id}', '{parent_id}', '{parent_name}', '{tag_id}', '{tag_name}', '{has_parent}')" style="" id="id_tag_search_change_{tag_id}" class="ac-tag_tag">{tag_name}</span>'''.format(
                category_id=d.category_id,
                parent_id=parent_id,
                parent_name=parent_name,
                tag_id=tag_id,
                tag_name=tag_name,
                has_parent=has_parent
            )
    if not html:
        html = u'<span style="display: inline;float: left;">no result</span>'
    return HttpResponse(json.dumps({'info': html}), content_type="application/json")



# 地址池批量打标签
@login_required
def ml_maillist_batch_tag(request):
    if not request.session.get('is_admin', ''):
        raise Http404
    if request.method == "POST":
        names = request.POST.getlist('name[]', '')
        action = request.POST.get('action', '')
        isvalid = request.POST.get('isvalid', '1')
        list_ids = request.POST.get('list_ids', '')
        if action == 'address':
            objs = MailList.objects.filter(id__in=list_ids.split(','))
            for tag_obj in objs:
                if not tag_obj.is_allow_export:
                    continue
                ctype = ContentType.objects.get_for_model(tag_obj)
                TaggedItem.objects.filter(content_type=ctype, object_id=tag_obj.id).delete()
                for tag_id in names:
                    remark = request.POST.get('remark_{}'.format(tag_id), '').strip()
                    remark = remark if remark else None
                    TaggedItem.objects.get_or_create(tag_id=tag_id, content_type=ctype, object_id=tag_obj.id, remark=remark)
                    names2 = request.POST.getlist(u'name{}[]'.format(tag_id), '')
                    for tag_id2 in names2:
                        TaggedItem.objects.get_or_create(tag_id=tag_id2, content_type=ctype, object_id=tag_obj.id, remark=None)
            messages.add_message(request, messages.SUCCESS, u'批量修改标签成功')
            return HttpResponseRedirect('/address/?isvalid={}'.format(isvalid))

    list_ids = request.GET.get('list_ids', '')
    isvalid = request.GET.get('isvalid', '')
    tag_lists = caches.cache_parent_tags(is_show=False)
    seach_tags = caches.cache_search_address_tags()
    return render(request, 'core/ml_maillist_batch_tagging.html', context={
        'list_ids': list_ids,
        'tag_lists': tag_lists,
        'isvalid': isvalid,
        'seach_tags': seach_tags,
    })

# 开启精准数据服务
@login_required
def ajax_mail_accurate_open(request):
    status = caches.cache_open_accurate(request)
    _status = 'Y' if status else 'N'
    return HttpResponse(json.dumps({ 'status': _status, }), content_type="application/json")

# 精准邮件数据服务 打开第三级标签
@login_required
def mail_accurate_service_open_three(request):
    tag_type = request.GET.get('tag_type', '')
    parent_id = request.GET.get('parent_id', '')
    tag_lists = caches.cache_child_tags(parent_id)
    child_ids = request.GET.get('child_ids', '')
    select_ids = map(int, child_ids.split(',')) if child_ids else []
    tag_obj = Tag.objects.get(id=parent_id)
    tag_vals = { '{}'.format(obj.id): {'name': obj.name, 'p_name': obj.parent.name } for obj in tag_lists}
    return render(request, template_name='core/mail_accurate_service_open_three.html', context={
        'tag_obj': tag_obj,
        'tag_type': tag_type,
        'tag_lists': tag_lists,
        'parent_id': parent_id,
        'select_ids': select_ids,
        'tag_vals': json.dumps(tag_vals),
    })

# 精准邮件数据服务
@login_required
def mail_accurate_service(request):
    status = caches.cache_open_accurate(request)
    if not status:
        raise Http404
    if request.method == "POST":
        redis = get_redis_connection()
        namelist = request.POST.getlist('name[]', '')
        namelist = [int(i) for i in namelist]
        remark = request.POST.get('remark', '').strip()
        linkman = request.POST.get('linkman', '').strip()
        phone = request.POST.get('phone', '').strip()
        obj = MailAccurateService.objects.create(
            customer_id=request.user.id,
            json_text=json.dumps({
                'namelist': namelist,
            }),
            remark=remark,
            linkman=linkman,
            mobile=phone,
            is_email=False,
        )
        redis.lpush('edm_web_mail_accurate_service_queue', obj.id)
        messages.add_message(request, messages.SUCCESS, _(u'申请数据成功，稍后会有客户经理和您联系，谢谢！'))
        return HttpResponseRedirect(reverse('mail_accurate_service'))

    tag_lists = caches.cache_parent_tags()
    return render(request, 'core/mail_accurate_service.html', context={
        'tag_lists': tag_lists,
    })

@login_required
def ajax_check_domain(request):
    id = request.POST.get('id', '')
    # print id
    ctype = request.POST.get('ctype', '')
    obj = get_object(CustomerDomain, request.user, id)
    res = 'f'
    if ctype == 'dkim':
        res = 'Y' if valid_domain(obj.domain, 'dkim', obj.dkim_public, dkim_selector=obj.dkim_selector) else 'f'
        obj.is_dkim = res
        obj.save()
    msg = {'msg': res}
    return HttpResponse(json.dumps(msg), content_type="application/json")
