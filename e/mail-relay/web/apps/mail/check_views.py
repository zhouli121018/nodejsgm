# coding=utf-8
import json

import re
import datetime

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.db.models import query, Count, Q
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template.response import TemplateResponse
# from redis_cache import get_redis_connection
from lib.django_redis import get_redis as get_redis_connection

from apps.mail.models import DomainBlacklist, KeywordBlacklist, CheckSettings, \
    SubjectKeywordBlacklist, SubjectKeywordWhitelist, SenderBlacklist, InvalidMail, RecipientBlacklist, \
    CustomKeywordBlacklist, ValidMailSuffix, AttachmentBlacklist, SenderWhitelist, InvalidSenderWhitelist, SpfChecklist, \
    TempSenderBlacklist, RecipientWhitelist, AttachmentTypeBlacklist, CustomerSenderBlacklist, SenderBlockedRecord, \
    RelaySenderWhitelist, CollectRecipientWhitelist, SpamRptBlacklist, CollectRecipientChecklist, SpfIpWhitelist
from apps.mail.forms import DomainBlacklistForm, KeywordBlacklistForm, SubjectKeywordBlacklistForm, \
    SubjectKeywordWhitelistForm, SenderBlacklistForm, InvalidMailForm, RecipientBlacklistForm, \
    CustomKeywordBlacklistForm, ValidMailSuffixForm, AttachmentBlacklistForm, SenderWhitelistForm, \
    InvalidSenderWhitelistForm, SpfChecklistForm, RecipientWhitelistForm, SenderWhitelistBatchForm, \
    SubjectKeywordBlacklistBatchForm, KeywordBlacklistBatchForm, SenderBlacklistBatchForm, AttachmentTypeBlacklistForm, \
    SenderWhitelistSearchFrom, AttachmentBlacklistBatchForm, CustomerSenderBlacklistForm, \
    CustomerSenderBlacklistSearchForm, \
    CustomerSenderBlacklistBatchForm, RecipientWhitelistBatchForm, SenderBlockedRecordSearchForm, \
    RelaySenderWhitelistSearchForm, \
    RelaySenderWhitelistBatchForm, RelaySenderWhitelistForm, CollectRecipientWhitelistBatchForm, \
    CollectRecipientWhitelistForm, SpamRptBlacklistForm, SpamRptBlacklistBatchForm, CollectRecipientChecklistForm, SpfIpWhitelistForm
from apps.collect_mail.models import get_mail_model


@login_required
def domain_blacklist_list(request):
    domain_blacklists = DomainBlacklist.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = DomainBlacklist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            DomainBlacklist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("mail/domain_blacklist_list.html", {
        'domain_blacklists': domain_blacklists,
    }, context_instance=RequestContext(request))


@login_required
def domain_blacklist_add(request):
    form = DomainBlacklistForm()
    if request.method == "POST":
        form = DomainBlacklistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('domain_blacklist_list'))
    return render_to_response("mail/domain_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def domain_blacklist_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = DomainBlacklistForm({'domain': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('domain_blacklist_list'))
    return render_to_response("mail/domain_blacklist_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def domain_blacklist_modify(request, domain_blacklist_id):
    domain_blacklist_obj = DomainBlacklist.objects.get(id=domain_blacklist_id)
    form = DomainBlacklistForm(instance=domain_blacklist_obj)
    if request.method == "POST":
        form = DomainBlacklistForm(request.POST, instance=domain_blacklist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('domain_blacklist_list'))
    return render_to_response("mail/domain_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


def get_keyword_blacklist(data):
    direct_reject = data.get('direct_reject', '')
    c_direct_reject = data.get('c_direct_reject', '')
    parent = data.get('parent', '')
    if parent:
        lists = KeywordBlacklist.objects.filter(parent_id=parent)
    else:
        lists = KeywordBlacklist.objects.filter(parent__isnull=True)
    if direct_reject:
        direct_reject = True if direct_reject.lower() == 'true' else False
        lists = lists.filter(direct_reject=direct_reject)
    if c_direct_reject:
        c_direct_reject = True if c_direct_reject.lower() == 'true' else False
        lists = lists.filter(c_direct_reject=c_direct_reject)
    return lists


@login_required
def ajax_get_keyword_blacklist(request):
    data = request.GET
    lists = get_keyword_blacklist(data)
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')

    if search:
        lists = lists.filter(Q(children__keyword__icontains=search) | Q(keyword__icontains=search))

    colums = ['id', 'order', 'keyword', 'is_regex', 'relay_all', 'relay_pass', 'relay_all', 'collect_all',
              'collect_pass',
              'collect_all', 'relay', 'direct_reject', 'collect', 'c_direct_reject', 'creater', 'created', 'operater',
              'operate_time', 'order', 'order']

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
        t = TemplateResponse(request, 'mail/ajax_get_keyword_blacklist.html', {
            'd': m,
            'app': KeywordBlacklist._meta.app_label,
            'model': KeywordBlacklist._meta.model_name,
        })
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def keyword_blacklist_list(request):
    if request.method == "POST":
        action = request.POST.get('action', '')
        ids = (request.POST.get('ids', '')).split(',')
        if action == 'change_status':
            status = int(request.POST.get('status', ''))
            if int(status) == -1:
                objs = KeywordBlacklist.objects.filter(id__in=ids)
                objs.delete()
                msg = u'成功删除%s个' % len(ids)
            else:
                abled = not status
                KeywordBlacklist.objects.filter(id__in=ids).update(relay=abled, collect=abled)
                tip = u'禁用' if status else u'启用'
                msg = u'成功%s%s个' % (tip, len(ids))

        if action == 'merge_list':
            list_name = request.POST.get('list_name', '').strip()
            p, bool = KeywordBlacklist.objects.get_or_create(keyword=list_name)
            if bool:
                p.to(KeywordBlacklist.objects.filter(id__in=ids).order_by('order')[0].order)
            # lists = lists.exclude(id=parent.id).filter(id__in=ids).update(parent=parent)
            for id in ids:
                children = KeywordBlacklist.objects.filter(parent_id=id)
                if children:
                    children.update(parent=p)
                else:
                    KeywordBlacklist.objects.filter(id=id).update(parent=p)
            p.order_by_self()
            msg = u'成功合并'
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(request.get_full_path())

    data = request.GET
    lists = get_keyword_blacklist(data)
    reject_status = lists.values("direct_reject").annotate(Count("id")).order_by()
    c_reject_status = lists.values("c_direct_reject").annotate(Count("id")).order_by()
    parent = data.get('parent', '')
    if parent:
        parent = KeywordBlacklist.objects.get(id=parent)

    return render_to_response("mail/keyword_blacklist_list.html", {
        'keyword_blacklists': lists,
        'app': KeywordBlacklist._meta.app_label,
        'model': KeywordBlacklist._meta.model_name,
        'reject_status': reject_status,
        'c_reject_status': c_reject_status,
        'parent': parent,
    }, context_instance=RequestContext(request))


@login_required
def keyword_blacklist_add(request):
    form = KeywordBlacklistBatchForm()
    if request.method == "POST":
        form = KeywordBlacklistBatchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            parent = request.GET.get('parent', '')
            if parent:
                parent = KeywordBlacklist.objects.get(id=parent)
            keyword = data.pop('keyword')
            success, fail = 0, 0
            import copy

            for k in keyword.split('\n'):
                d = copy.deepcopy(data)
                d['keyword'] = k.replace('\r', '')
                f = KeywordBlacklistForm(d)
                if f.is_valid():
                    success += 1
                    obj = f.save()
                    obj.creater = request.user
                    if parent:
                        obj.parent = parent
                    obj.save()
                else:
                    fail += 1
            if parent:
                parent.order_by_self()
            messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
            if parent:
                return HttpResponseRedirect('/check_list/keyword_blacklist?parent={}'.format(parent.id))
            return HttpResponseRedirect(reverse('keyword_blacklist_list'))
    parent = request.GET.get('parent', '')
    if parent:
        parent = KeywordBlacklist.objects.get(id=parent)
    parent_id = parent.id if parent else None
    return render_to_response("mail/keyword_blacklist_modify.html", {
        'form': form,
        'parent_id': parent_id,
    }, context_instance=RequestContext(request))


@login_required
def _keyword_blacklist_add(request):
    form = KeywordBlacklistForm()
    if request.method == "POST":
        form = KeywordBlacklistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('keyword_blacklist_list'))
    return render_to_response("mail/keyword_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def keyword_blacklist_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = KeywordBlacklistForm({'keyword': w.replace('\r', ''), 'collect': True, 'relay': True})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('keyword_blacklist_list'))
    return render_to_response("mail/keyword_blacklist_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def keyword_blacklist_modify(request, keyword_blacklist_id):
    keyword_blacklist_obj = KeywordBlacklist.objects.get(id=keyword_blacklist_id)
    form = KeywordBlacklistForm(instance=keyword_blacklist_obj)
    parent_id = keyword_blacklist_obj.parent_id
    if request.method == "POST":
        form = KeywordBlacklistForm(request.POST, instance=keyword_blacklist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            if parent_id:
                return HttpResponseRedirect('/check_list/keyword_blacklist?parent={}'.format(parent_id))
            return HttpResponseRedirect(reverse('keyword_blacklist_list'))
    context = {'form': form, 'parent_id': parent_id}
    return render_to_response("mail/keyword_blacklist_modify.html", context, context_instance=RequestContext(request))


@login_required
def subject_keyword_blacklist_list(request):
    if request.method == "POST":
        action = request.POST.get('action', '')
        ids = (request.POST.get('ids', '')).split(',')
        if action == 'change_status':
            status = int(request.POST.get('status', ''))
            if int(status) == -1:
                objs = SubjectKeywordBlacklist.objects.filter(id__in=ids)
                objs.delete()
                msg = u'成功删除%s个' % len(ids)
            else:
                abled = not status
                SubjectKeywordBlacklist.objects.filter(id__in=ids).update(relay=abled, collect=abled)
                tip = u'禁用' if status else u'启用'
                msg = u'成功%s%s个' % (tip, len(ids))

        if action == 'merge_list':
            list_name = request.POST.get('list_name', '').strip()
            p, bool = SubjectKeywordBlacklist.objects.get_or_create(keyword=list_name)
            if bool:
                p.to(SubjectKeywordBlacklist.objects.filter(id__in=ids).order_by('order')[0].order)
            # lists = lists.exclude(id=parent.id).filter(id__in=ids).update(parent=parent)
            for id in ids:
                children = SubjectKeywordBlacklist.objects.filter(parent_id=id)
                if children:
                    children.update(parent=p)
                else:
                    SubjectKeywordBlacklist.objects.filter(id=id).update(parent=p)
            p.order_by_self()
            msg = u'成功合并'
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(request.get_full_path())

    data = request.GET
    lists = get_subject_blacklist(data)
    reject_status = lists.values("direct_reject").annotate(Count("id")).order_by()
    c_reject_status = lists.values("c_direct_reject").annotate(Count("id")).order_by()
    parent = data.get('parent', '')
    if parent:
        parent = SubjectKeywordBlacklist.objects.get(id=parent)

    return render_to_response("mail/subject_keyword_blacklist_list.html", {
        'subject_keyword_blacklists': lists,
        'reject_status': reject_status,
        'c_reject_status': c_reject_status,
        'app': SubjectKeywordBlacklist._meta.app_label,
        'model': SubjectKeywordBlacklist._meta.model_name,
        'parent': parent
    }, context_instance=RequestContext(request))


def get_subject_blacklist(data):
    direct_reject = data.get('direct_reject', '')
    c_direct_reject = data.get('c_direct_reject', '')
    parent = data.get('parent', '')
    if parent:
        lists = SubjectKeywordBlacklist.objects.filter(parent_id=parent)
    else:
        lists = SubjectKeywordBlacklist.objects.filter(parent__isnull=True)
    if direct_reject:
        direct_reject = True if direct_reject.lower() == 'true' else False
        lists = lists.filter(direct_reject=direct_reject)
    if c_direct_reject:
        c_direct_reject = True if c_direct_reject.lower() == 'true' else False
        lists = lists.filter(c_direct_reject=c_direct_reject)
    return lists


@login_required
def ajax_get_subject_blacklist(request):
    data = request.GET
    lists = get_subject_blacklist(data)
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')

    if search:
        lists = lists.filter(Q(children__keyword__icontains=search) | Q(keyword__icontains=search))

    colums = ['id', 'order', 'keyword', 'is_regex', 'relay_all', 'relay_pass', 'relay_all', 'collect_all',
              'collect_pass',
              'collect_all', 'relay', 'direct_reject', 'collect', 'c_direct_reject', 'creater', 'created', 'operater',
              'operate_time', 'order', 'order']

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
        t = TemplateResponse(request, 'mail/ajax_get_subject_blacklist.html', {
            'd': m,
            'app': SubjectKeywordBlacklist._meta.app_label,
            'model': SubjectKeywordBlacklist._meta.model_name,
        })
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def subject_keyword_blacklist_add(request):
    form = SubjectKeywordBlacklistBatchForm()
    if request.method == "POST":
        form = SubjectKeywordBlacklistBatchForm(request.POST)
        parent = request.GET.get('parent', '')
        if parent:
            parent = SubjectKeywordBlacklist.objects.get(id=parent)
        if form.is_valid():
            data = form.cleaned_data
            keyword = data.pop('keyword')
            success, fail = 0, 0
            import copy

            for k in keyword.split('\n'):
                d = copy.deepcopy(data)
                d['keyword'] = k.replace('\r', '')
                f = SubjectKeywordBlacklistForm(d)
                if f.is_valid():
                    success += 1
                    obj = f.save()
                    obj.creater = request.user
                    if parent:
                        obj.parent = parent
                    obj.save()
                else:
                    fail += 1
            if parent:
                parent.order_by_self()
            messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
            if parent:
                return HttpResponseRedirect('/check_list/subject_keyword_blacklist?parent={}'.format(parent.id))
            return HttpResponseRedirect(reverse('subject_keyword_blacklist_list'))
    parent = request.GET.get('parent', '')
    if parent:
        parent = SubjectKeywordBlacklist.objects.get(id=parent)
    parent_id = parent.id if parent else None
    return render_to_response("mail/subject_keyword_blacklist_modify.html", {
        'form': form,
        'parent_id': parent_id,
    }, context_instance=RequestContext(request))


@login_required
def _subject_keyword_blacklist_add(request):
    form = SubjectKeywordBlacklistForm()
    if request.method == "POST":
        form = SubjectKeywordBlacklistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('subject_keyword_blacklist_list'))
    return render_to_response("mail/subject_keyword_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def subject_keyword_blacklist_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = SubjectKeywordBlacklistForm({'keyword': w.replace('\r', ''), 'relay': True, 'collect': True})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('subject_keyword_blacklist_list'))
    return render_to_response("mail/subject_keyword_blacklist_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def subject_keyword_blacklist_modify(request, subject_keyword_blacklist_id):
    subject_keyword_blacklist_obj = SubjectKeywordBlacklist.objects.get(id=subject_keyword_blacklist_id)
    form = SubjectKeywordBlacklistForm(instance=subject_keyword_blacklist_obj)
    parent_id = subject_keyword_blacklist_obj.parent_id
    if request.method == "POST":
        form = SubjectKeywordBlacklistForm(request.POST, instance=subject_keyword_blacklist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            if parent_id:
                return HttpResponseRedirect('/check_list/subject_keyword_blacklist?parent={}'.format(parent_id))
            return HttpResponseRedirect(reverse('subject_keyword_blacklist_list'))
    return render_to_response("mail/subject_keyword_blacklist_modify.html", {
        'form': form,
        'parent_id': parent_id,
    }, context_instance=RequestContext(request))


@login_required
def subject_keyword_whitelist_list(request):
    subject_keyword_whitelists = SubjectKeywordWhitelist.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = SubjectKeywordWhitelist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            SubjectKeywordWhitelist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("mail/subject_keyword_whitelist_list.html", {
        'subject_keyword_whitelists': subject_keyword_whitelists,
    }, context_instance=RequestContext(request))


@login_required
def subject_keyword_whitelist_add(request):
    form = SubjectKeywordWhitelistForm()
    if request.method == "POST":
        form = SubjectKeywordWhitelistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('subject_keyword_whitelist_list'))
    return render_to_response("mail/subject_keyword_whitelist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def subject_keyword_whitelist_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = SubjectKeywordWhitelistForm({'keyword': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('subject_keyword_whitelist_list'))
    return render_to_response("mail/subject_keyword_whitelist_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def subject_keyword_whitelist_modify(request, subject_keyword_whitelist_id):
    subject_keyword_whitelist_obj = SubjectKeywordWhitelist.objects.get(id=subject_keyword_whitelist_id)
    form = SubjectKeywordWhitelistForm(instance=subject_keyword_whitelist_obj)
    if request.method == "POST":
        form = SubjectKeywordWhitelistForm(request.POST, instance=subject_keyword_whitelist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('subject_keyword_whitelist_list'))
    return render_to_response("mail/subject_keyword_whitelist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


def get_sender_blacklist(data):
    direct_reject = data.get('direct_reject', '')
    c_direct_reject = data.get('c_direct_reject', '')
    parent = data.get('parent', '')
    if parent:
        lists = SenderBlacklist.objects.filter(parent_id=parent)
    else:
        lists = SenderBlacklist.objects.filter(parent__isnull=True)
    if direct_reject:
        direct_reject = True if direct_reject.lower() == 'true' else False
        lists = lists.filter(direct_reject=direct_reject)
    if c_direct_reject:
        c_direct_reject = True if c_direct_reject.lower() == 'true' else False
        lists = lists.filter(c_direct_reject=c_direct_reject)
    return lists


@login_required
def ajax_get_sender_blacklist(request):
    data = request.GET
    lists = get_sender_blacklist(data)
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')

    if search:
        lists = lists.filter(Q(children__keyword__icontains=search) | Q(keyword__icontains=search))

    colums = ['id', 'order', 'keyword', 'is_regex', 'relay', 'direct_reject', 'collect', 'c_direct_reject', 'creater',
              'created', 'operater',
              'operate_time', 'order', 'order']

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
        t = TemplateResponse(request, 'mail/ajax_get_sender_blacklist.html', {
            'd': m,
            'app': SenderBlacklist._meta.app_label,
            'model': SenderBlacklist._meta.model_name,
        })
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def sender_blacklist_list(request):
    if request.method == "POST":
        action = request.POST.get('action', '')
        ids = (request.POST.get('ids', '')).split(',')
        if action == 'change_status':
            status = int(request.POST.get('status', ''))
            if int(status) == -1:
                objs = SenderBlacklist.objects.filter(id__in=ids)
                objs.delete()
                msg = u'成功删除%s个' % len(ids)
            else:
                abled = not status
                SenderBlacklist.objects.filter(id__in=ids).update(relay=abled, collect=abled)
                tip = u'禁用' if status else u'启用'
                msg = u'成功%s%s个' % (tip, len(ids))

        if action == 'merge_list':
            list_name = request.POST.get('list_name', '').strip()
            p, bool = SenderBlacklist.objects.get_or_create(keyword=list_name)
            if bool:
                p.to(SenderBlacklist.objects.filter(id__in=ids).order_by('order')[0].order)
            # lists = lists.exclude(id=parent.id).filter(id__in=ids).update(parent=parent)
            for id in ids:
                children = SenderBlacklist.objects.filter(parent_id=id)
                if children:
                    children.update(parent=p)
                else:
                    SenderBlacklist.objects.filter(id=id).update(parent=p)
            p.order_by_self()
            msg = u'成功合并'
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(request.get_full_path())

    data = request.GET
    lists = get_sender_blacklist(data)
    reject_status = lists.values("direct_reject").annotate(Count("id")).order_by()
    c_reject_status = lists.values("c_direct_reject").annotate(Count("id")).order_by()
    parent = data.get('parent', '')
    if parent:
        parent = SenderBlacklist.objects.get(id=parent)

    return render_to_response("mail/sender_blacklist_list.html", {
        'sender_blacklists': lists,
        'app': SenderBlacklist._meta.app_label,
        'model': SenderBlacklist._meta.model_name,
        'reject_status': reject_status,
        'c_reject_status': c_reject_status,
        'parent': parent,
    }, context_instance=RequestContext(request))


@login_required
def sender_blacklist_add(request):
    form = SenderBlacklistBatchForm()
    if request.method == "POST":
        form = SenderBlacklistBatchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            parent = request.GET.get('parent', '')
            if parent:
                parent = SenderBlacklist.objects.get(id=parent)
            keyword = data.pop('keyword')
            success, fail = 0, 0
            import copy

            for k in keyword.split('\n'):
                d = copy.deepcopy(data)
                d['keyword'] = k.replace('\r', '')
                f = SenderBlacklistForm(d)
                if f.is_valid():
                    success += 1
                    obj = f.save()
                    obj.creater = request.user
                    if parent:
                        obj.parent = parent
                    obj.save()
                else:
                    fail += 1
            if parent:
                parent.order_by_self()
            messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
            if parent:
                return HttpResponseRedirect('/check_list/sender_blacklist?parent={}'.format(parent.id))
            return HttpResponseRedirect(reverse('sender_blacklist_list'))
    parent = request.GET.get('parent', '')
    if parent:
        parent = SenderBlacklist.objects.get(id=parent)
    parent_id = parent.id if parent else None
    return render_to_response("mail/sender_blacklist_modify.html", {
        'form': form,
        'parent_id': parent_id,
    }, context_instance=RequestContext(request))


@login_required
def _sender_blacklist_add(request):
    form = SenderBlacklistForm()
    if request.method == "POST":
        form = SenderBlacklistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('sender_blacklist_list'))
    return render_to_response("mail/sender_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def sender_blacklist_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = SenderBlacklistForm({'keyword': w.replace('\r', ''), 'collect': True, 'relay': True})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('sender_blacklist_list'))
    return render_to_response("mail/sender_blacklist_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def sender_blacklist_modify(request, sender_blacklist_id):
    sender_blacklist_obj = SenderBlacklist.objects.get(id=sender_blacklist_id)
    form = SenderBlacklistForm(instance=sender_blacklist_obj)
    parent_id = sender_blacklist_obj.parent_id
    if request.method == "POST":
        form = SenderBlacklistForm(request.POST, instance=sender_blacklist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            if parent_id:
                return HttpResponseRedirect('/check_list/sender_blacklist?parent={}'.format(parent_id))
            return HttpResponseRedirect(reverse('sender_blacklist_list'))
    return render_to_response("mail/sender_blacklist_modify.html", {
        'form': form,
        'parent_id': parent_id,
    }, context_instance=RequestContext(request))


@login_required
def invalid_mail_list(request):
    invalid_mails = InvalidMail.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = InvalidMail.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            InvalidMail.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("mail/invalid_mail_list.html", {
        'invalid_mails': invalid_mails,
    }, context_instance=RequestContext(request))


@login_required
def invalid_mail_add(request):
    form = InvalidMailForm()
    if request.method == "POST":
        form = InvalidMailForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('invalid_mail_list'))
    return render_to_response("mail/invalid_mail_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def invalid_mail_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = InvalidMailForm({'mail': w.strip().replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('invalid_mail_list'))
    return render_to_response("mail/invalid_mail_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def invalid_mail_modify(request, invalid_mail_id):
    invalid_mail_obj = InvalidMail.objects.get(id=invalid_mail_id)
    form = InvalidMailForm(instance=invalid_mail_obj)
    if request.method == "POST":
        form = InvalidMailForm(request.POST, instance=invalid_mail_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('invalid_mail_list'))
    return render_to_response("mail/invalid_mail_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def ajax_get_invalid_mail(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')

    mails = InvalidMail.objects.all()
    if search:
        mails = mails.filter(mail__icontains=search)

    colums = ['id', 'mail', 'creater', 'created', 'operater', 'operate_time', 'id']

    if isinstance(mails, query.QuerySet) and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            mails = mails.order_by('-%s' % colums[int(order_column)])
        else:
            mails = mails.order_by('%s' % colums[int(order_column)])
    try:
        length = int(data.get('length', 1))
    except ValueError:
        length = 1

    try:
        page = int(data.get('start', '0')) / length + 1
    except ValueError:
        page = 1

    try:
        count = mails.count()
    except:
        count = len(mails)

    paginator = Paginator(mails, length)

    try:
        mails = paginator.page(page)
    except (EmptyPage, InvalidPage):
        mails = paginator.page(paginator.num_pages)

    rs = {"sEcho": 0, "iTotalRecords": count, "iTotalDisplayRecords": count, "aaData": []}
    re_str = '<td.*?>(.*?)</td>'
    for m in mails.object_list:
        t = TemplateResponse(request, 'mail/ajax_get_invalid_mail.html', {'d': m})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def recipient_blacklist_list(request):
    recipient_blacklists = RecipientBlacklist.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = RecipientBlacklist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            RecipientBlacklist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("mail/recipient_blacklist_list.html", {
        'recipient_blacklists': recipient_blacklists,
    }, context_instance=RequestContext(request))


@login_required
def recipient_blacklist_add(request):
    form = RecipientBlacklistForm()
    if request.method == "POST":
        form = RecipientBlacklistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('recipient_blacklist_list'))
    return render_to_response("mail/recipient_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def recipient_blacklist_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = RecipientBlacklistForm({'keyword': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('recipient_blacklist_list'))
    return render_to_response("mail/recipient_blacklist_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def recipient_blacklist_modify(request, recipient_blacklist_id):
    recipient_blacklist_obj = RecipientBlacklist.objects.get(id=recipient_blacklist_id)
    form = RecipientBlacklistForm(instance=recipient_blacklist_obj)
    if request.method == "POST":
        form = RecipientBlacklistForm(request.POST, instance=recipient_blacklist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('recipient_blacklist_list'))
    return render_to_response("mail/recipient_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def ajax_get_collect_recipient_whitelist(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    lists = CollectRecipientWhitelist.objects.all()

    if search:
        lists = lists.filter(keyword__icontains=search)

    colums = ['id', 'keyword', 'disabled', 'creater', 'created', 'operater', 'operate_time']

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
        t = TemplateResponse(request, 'mail/ajax_get_collect_recipient_whitelist.html', {'d': m})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def collect_recipient_whitelist_list(request):
    collect_recipient_whitelists = CollectRecipientWhitelist.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = CollectRecipientWhitelist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            CollectRecipientWhitelist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("mail/collect_recipient_whitelist_list.html", {
        'collect_recipient_whitelists': collect_recipient_whitelists,
    }, context_instance=RequestContext(request))


@login_required
def collect_recipient_whitelist_add(request):
    form = CollectRecipientWhitelistForm()
    if request.method == "POST":
        form = CollectRecipientWhitelistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('collect_recipient_whitelist_list'))
    return render_to_response("mail/collect_recipient_whitelist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def collect_recipient_whitelist_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = CollectRecipientWhitelistForm({'keyword': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('collect_recipient_whitelist_list'))
    return render_to_response("mail/collect_recipient_whitelist_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def collect_recipient_whitelist_modify(request, collect_recipient_whitelist_id):
    collect_recipient_whitelist_obj = CollectRecipientWhitelist.objects.get(id=collect_recipient_whitelist_id)
    form = CollectRecipientWhitelistForm(instance=collect_recipient_whitelist_obj)
    if request.method == "POST":
        form = CollectRecipientWhitelistForm(request.POST, instance=collect_recipient_whitelist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('collect_recipient_whitelist_list'))
    return render_to_response("mail/collect_recipient_whitelist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def custom_keyword_blacklist_list(request):
    custom_keyword_blacklists = CustomKeywordBlacklist.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = CustomKeywordBlacklist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            CustomKeywordBlacklist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("mail/custom_keyword_blacklist_list.html", {
        'custom_keyword_blacklists': custom_keyword_blacklists,
    }, context_instance=RequestContext(request))


@login_required
def custom_keyword_blacklist_add(request):
    form = CustomKeywordBlacklistForm()
    if request.method == "POST":
        form = CustomKeywordBlacklistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('custom_keyword_blacklist_list'))
    return render_to_response("mail/custom_keyword_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def custom_keyword_blacklist_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        type = request.POST.get('type', 'subject')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = CustomKeywordBlacklistForm({'keyword': w.replace('\r', ''), 'type': type})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('custom_keyword_blacklist_list'))
    return render_to_response("mail/custom_keyword_blacklist_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def custom_keyword_blacklist_modify(request, custom_keyword_blacklist_id):
    custom_keyword_blacklist_obj = CustomKeywordBlacklist.objects.get(id=custom_keyword_blacklist_id)
    form = CustomKeywordBlacklistForm(instance=custom_keyword_blacklist_obj)
    if request.method == "POST":
        form = CustomKeywordBlacklistForm(request.POST, instance=custom_keyword_blacklist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('custom_keyword_blacklist_list'))
    return render_to_response("mail/custom_keyword_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


def spam_sender_list(request):
    redis = get_redis_connection()
    sender_dict = redis.hgetall('relay_spam_sender_history')
    try:
        experied_time = CheckSettings.objects.all()[0].active_spam_check_time
    except:
        experied_time = 12
    sender_list = []
    for k, v in sender_dict.iteritems():
        if k == 'is_need_update':
            continue
        time_list = v.split(',')
        last_time = float(time_list[0])
        sender_list.append({
            'mail_from': k,
            'total': len(time_list),
            'is_spam_sender': redis.hexists('relay_spam_sender', k),
            'last_time': datetime.datetime.fromtimestamp(last_time),
            'expired': datetime.datetime.fromtimestamp(last_time + experied_time * 3600),
        }
        )
    sender_list = sorted(sender_list, key=lambda d: d['is_spam_sender'], reverse=True)
    if request.method == 'POST':
        key = request.POST.get('mail_from', '')
        redis.hdel('relay_spam_sender', key)
        redis.hdel('relay_spam_sender_history', key)
        messages.add_message(request, messages.SUCCESS, u'成功删除发件人: {}'.format(key))
        return HttpResponseRedirect(reverse('spam_sender_list'))
    return render_to_response("mail/spam_sender_list.html", {
        'senders': sender_list,
    }, context_instance=RequestContext(request))


@login_required
def mail_suffix_list(request):
    mail_suffixs = ValidMailSuffix.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = ValidMailSuffix.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            ValidMailSuffix.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("mail/mail_suffix_list.html", {
        'mail_suffixs': mail_suffixs,
    }, context_instance=RequestContext(request))


@login_required
def mail_suffix_add(request):
    form = ValidMailSuffixForm()
    if request.method == "POST":
        form = ValidMailSuffixForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('mail_suffix_list'))
    return render_to_response("mail/mail_suffix_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def mail_suffix_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = ValidMailSuffixForm({'keyword': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('mail_suffix_list'))
    return render_to_response("mail/mail_suffix_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def mail_suffix_modify(request, mail_suffix_id):
    mail_suffix_obj = ValidMailSuffix.objects.get(id=mail_suffix_id)
    form = ValidMailSuffixForm(instance=mail_suffix_obj)
    if request.method == "POST":
        form = ValidMailSuffixForm(request.POST, instance=mail_suffix_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('mail_suffix_list'))
    return render_to_response("mail/mail_suffix_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


def get_attach_blacklist(data):
    direct_reject = data.get('direct_reject', '')
    c_direct_reject = data.get('c_direct_reject', '')
    parent = data.get('parent', '')
    if parent:
        lists = AttachmentBlacklist.objects.filter(parent_id=parent)
    else:
        lists = AttachmentBlacklist.objects.filter(parent__isnull=True)
    if direct_reject:
        direct_reject = True if direct_reject.lower() == 'true' else False
        lists = lists.filter(direct_reject=direct_reject)
    if c_direct_reject:
        c_direct_reject = True if c_direct_reject.lower() == 'true' else False
        lists = lists.filter(c_direct_reject=c_direct_reject)
    return lists


@login_required
def ajax_get_attach_blacklist(request):
    data = request.GET
    lists = get_attach_blacklist(data)
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')

    if search:
        lists = lists.filter(Q(children__keyword__icontains=search) | Q(keyword__icontains=search))

    colums = ['id', 'order', 'keyword', 'is_regex', 'relay', 'direct_reject', 'collect', 'c_direct_reject', 'creater',
              'created', 'operater',
              'operate_time', 'order', 'order']

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
        t = TemplateResponse(request, 'mail/ajax_get_attach_blacklist.html', {
            'd': m,
            'app': AttachmentBlacklist._meta.app_label,
            'model': AttachmentBlacklist._meta.model_name,
        })
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def attachment_blacklist_list(request):
    if request.method == "POST":
        action = request.POST.get('action', '')
        ids = (request.POST.get('ids', '')).split(',')
        if action == 'change_status':
            status = int(request.POST.get('status', ''))
            if int(status) == -1:
                objs = AttachmentBlacklist.objects.filter(id__in=ids)
                objs.delete()
                msg = u'成功删除%s个' % len(ids)
            else:
                abled = not status
                AttachmentBlacklist.objects.filter(id__in=ids).update(relay=abled, collect=abled)
                tip = u'禁用' if status else u'启用'
                msg = u'成功%s%s个' % (tip, len(ids))

        if action == 'merge_list':
            list_name = request.POST.get('list_name', '').strip()
            p, bool = AttachmentBlacklist.objects.get_or_create(keyword=list_name)
            if bool:
                p.to(AttachmentBlacklist.objects.filter(id__in=ids).order_by('order')[0].order)
            # lists = lists.exclude(id=parent.id).filter(id__in=ids).update(parent=parent)
            for id in ids:
                children = AttachmentBlacklist.objects.filter(parent_id=id)
                if children:
                    children.update(parent=p)
                else:
                    AttachmentBlacklist.objects.filter(id=id).update(parent=p)
            p.order_by_self()
            msg = u'成功合并'
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(request.get_full_path())

    data = request.GET
    lists = get_attach_blacklist(data)
    reject_status = lists.values("direct_reject").annotate(Count("id")).order_by()
    c_reject_status = lists.values("c_direct_reject").annotate(Count("id")).order_by()
    parent = data.get('parent', '')
    if parent:
        parent = AttachmentBlacklist.objects.get(id=parent)

    return render_to_response("mail/attachment_blacklist_list.html", {
        'attach_blacklists': lists,
        'app': AttachmentBlacklist._meta.app_label,
        'model': AttachmentBlacklist._meta.model_name,
        'reject_status': reject_status,
        'c_reject_status': c_reject_status,
        'parent': parent,
    }, context_instance=RequestContext(request))


@login_required
def attachment_blacklist_add(request):
    form = AttachmentBlacklistBatchForm()
    if request.method == "POST":
        form = AttachmentBlacklistBatchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            keyword = data.pop('keyword')
            success, fail = 0, 0
            import copy

            for k in keyword.split('\n'):
                d = copy.deepcopy(data)
                parent = request.GET.get('parent', '')
                if parent:
                    parent = AttachmentBlacklist.objects.get(id=parent)
                d['keyword'] = k.replace('\r', '')
                f = AttachmentBlacklistForm(d)
                if f.is_valid():
                    success += 1
                    obj = f.save()
                    obj.creater = request.user
                    if parent:
                        obj.parent = parent
                    obj.save()
                else:
                    fail += 1
            if parent:
                parent.order_by_self()
            messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
            if parent:
                return HttpResponseRedirect('/check_list/attachment_blacklist?parent={}'.format(parent.id))
            return HttpResponseRedirect(reverse('attachment_blacklist_list'))
    parent = request.GET.get('parent', '')
    if parent:
        parent = AttachmentBlacklist.objects.get(id=parent)
    parent_id = parent.id if parent else None
    return render_to_response("mail/attachment_blacklist_modify.html", {
        'form': form,
        'parent_id': parent_id,
    }, context_instance=RequestContext(request))


@login_required
def attachment_blacklist_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = AttachmentBlacklistForm({'keyword': w.replace('\r', ''), 'relay': True, 'collect': True})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('attachment_blacklist_list'))
    return render_to_response("mail/attachment_blacklist_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def attachment_blacklist_modify(request, attachment_blacklist_id):
    attachment_blacklist_obj = AttachmentBlacklist.objects.get(id=attachment_blacklist_id)
    form = AttachmentBlacklistForm(instance=attachment_blacklist_obj)
    parent_id = attachment_blacklist_obj.parent_id
    if request.method == "POST":
        form = AttachmentBlacklistForm(request.POST, instance=attachment_blacklist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            if parent_id:
                return HttpResponseRedirect('/check_list/attachment_blacklist?parent={}'.format(parent_id))
            return HttpResponseRedirect(reverse('attachment_blacklist_list'))
    return render_to_response("mail/attachment_blacklist_modify.html", {
        'form': form,
        'parent_id': parent_id,
    }, context_instance=RequestContext(request))


@login_required
def ajax_change_check_list(request):
    id = request.GET.get('id', '')
    name, attr, id = id.split('-')
    if name == 'subject':
        model = SubjectKeywordBlacklist.objects.get(id=id)
    elif name == 'content':
        model = KeywordBlacklist.objects.get(id=id)
    elif name == 'sender':
        model = SenderBlacklist.objects.get(id=id)
    elif name == 'attach':
        model = AttachmentBlacklist.objects.get(id=id)
    t = not model.__getattribute__(attr)
    model.__setattr__(attr, t)
    model.operater = request.user
    model.save()
    class_name = 'glyphicon-ok' if t else 'glyphicon-remove'
    msg = u'<span class="glyphicon {}"><span class="hidden">{}</span></span>'.format(class_name, t)

    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")


@login_required
def sender_whitelist_list(request):
    form = SenderWhitelistSearchFrom(request.GET)
    lists = _get_sender_whitelist(request.GET)
    status_info = lists.values("is_global").annotate(Count("id")).order_by()
    domain_info = lists.values("is_domain").annotate(Count("id")).order_by()

    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = SenderWhitelist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            SenderWhitelist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(reverse('sender_whitelist_list'))
    return render_to_response("mail/sender_whitelist_list.html", {
        'status_info': status_info,
        'domain_info': domain_info,
        'lists': lists,
        'form': form
    }, context_instance=RequestContext(request))


def _get_sender_whitelist(data):
    lists = SenderWhitelist.objects.all()
    sender = data.get('sender', '')
    customer = data.get('customer', '')
    is_global = data.get('is_global', '')
    is_domain = data.get('is_domain', '')
    disabled = data.get('disabled', '')
    if sender:
        lists = lists.filter(sender__icontains=sender)
    if customer:
        lists = lists.filter(Q(customer__company__icontains=customer) | Q(customer__username__icontains=customer))

    if is_global:
        if is_global.lower() == 'true':
            is_global = True
        else:
            is_global = False
        lists = lists.filter(is_global=is_global)
    if is_domain:
        if is_domain.lower() == 'true':
            is_domain = True
        else:
            is_domain = False
        lists = lists.filter(is_domain=is_domain)
    if disabled:
        if disabled.lower() == 'true':
            disabled = True
        else:
            disabled = False
        lists = lists.filter(disabled=disabled)
    return lists


@login_required
def ajax_get_sender_whitelist(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    lists = _get_sender_whitelist(data)

    if search:
        lists = lists.filter(sender__icontains=search)

    colums = ['id', 'sender', 'is_global', 'is_domain', 'customer', 'disabled', 'creater', 'created', 'operater',
              'operate_time', 'id']

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
        t = TemplateResponse(request, 'mail/ajax_get_sender_whitelist.html', {'d': m})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def sender_whitelist_add(request):
    form = SenderWhitelistForm()
    if request.method == "POST":
        form = SenderWhitelistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('sender_whitelist_list'))
    return render_to_response("mail/sender_whitelist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def sender_whitelist_batch_add(request):
    form = SenderWhitelistBatchForm()
    if request.method == "POST":
        form = SenderWhitelistBatchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            senders = data.pop('senders')
            if data['customer']:
                data['customer'] = data['customer'].id
            success, fail = 0, 0
            import copy

            for s in senders.split('\n'):
                d = copy.deepcopy(data)
                d['sender'] = s.replace('\r', '')
                f = SenderWhitelistForm(d)
                if f.is_valid():
                    success += 1
                    obj = f.save()
                    obj.creater = request.user
                    obj.save()
                else:
                    fail += 1
            messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
            return HttpResponseRedirect(reverse('sender_whitelist_list'))
    return render_to_response("mail/sender_whitelist_batch_add.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def sender_whitelist_modify(request, sender_whitelist_id):
    sender_whitelist_obj = SenderWhitelist.objects.get(id=sender_whitelist_id)
    form = SenderWhitelistForm(instance=sender_whitelist_obj)
    if request.method == "POST":
        form = SenderWhitelistForm(request.POST, instance=sender_whitelist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('sender_whitelist_list'))
    return render_to_response("mail/sender_whitelist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def ajax_add_sender_whitelist(request):
    id = request.GET.get('id', '')
    is_global = request.GET.get('is_global', '')
    is_domain = request.GET.get('is_domain', '')
    msg = u'已添加'
    add_sender_whitelist(id, is_global, is_domain, user=request.user)
    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")


@login_required
def ajax_add_sender_blacklist(request):
    id = request.GET.get('id', '')
    is_global = request.GET.get('is_global', '')
    is_domain = request.GET.get('is_domain', '')
    msg = u'已添加'
    add_sender_blacklist(id, is_global, is_domain, user=request.user)
    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")


def add_sender_whitelist(mail_id, is_global=False, is_domain=False, user=None):
    date, id = mail_id.split('_')
    mail_obj = get_mail_model(date).objects.get(id=id)
    mail_from = mail_obj.mail_from
    if mail_from:
        mail_from = mail_from.lower()
        if '=' in mail_from:
            mail_from = mail_from.split('=')[-1]

        if is_domain:
            mail_from = mail_from.split('@')[-1]

        customer = None if is_global else mail_obj.customer
        obj, bool = SenderWhitelist.objects.get_or_create(sender=mail_from, is_global=is_global, is_domain=is_domain,
                                                          customer=customer)
        # spf_obj, spf_bool = SpfChecklist.objects.get_or_create(domain=mail_from.split('@')[-1])
        if user:
            if bool:
                obj.creater = user
            else:
                obj.operater = user
            obj.save()
            # if spf_bool:
            #     spf_obj.creater = user
            # else:
            #     spf_obj.operater = user
            # spf_obj.save()

def add_sender_blacklist(mail_id, is_global=False, is_domain=False, user=None):
    date, id = mail_id.split('_')
    mail_obj = get_mail_model(date).objects.get(id=id)
    mail_from = mail_obj.mail_from
    if mail_from:
        mail_from = mail_from.lower()
        if '=' in mail_from:
            mail_from = mail_from.split('=')[-1]

        if is_domain:
            mail_from = mail_from.split('@')[-1]

        customer = None if is_global else mail_obj.customer
        obj, bool = CustomerSenderBlacklist.objects.get_or_create(sender=mail_from, is_global=is_global,
                                                                  is_domain=is_domain, customer=customer)
        if user:
            if bool:
                obj.creater = user
            else:
                obj.operater = user
            obj.save()


@login_required
def customer_sender_blacklist_list(request):
    form = CustomerSenderBlacklistSearchForm()
    lists = _get_customer_sender_blacklist(request.GET)
    status_info = lists.values("is_global").annotate(Count("id")).order_by()
    domain_info = lists.values("is_domain").annotate(Count("id")).order_by()

    if request.method == 'POST':
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = CustomerSenderBlacklist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            CustomerSenderBlacklist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(reverse('customer_sender_blacklist_list'))
    return render_to_response("mail/customer_sender_blacklist_list.html", {
        'status_info': status_info,
        'domain_info': domain_info,
        'lists': lists,
        'form': form
    }, context_instance=RequestContext(request))


def _get_customer_sender_blacklist(data):
    lists = CustomerSenderBlacklist.objects.all()
    sender = data.get('sender', False)
    customer = data.get('customer', False)
    is_global = data.get('is_global', False)
    is_domain = data.get('is_domain', False)
    disabled = data.get('disabled', False)
    if sender:
        lists = lists.filter(sender__icontains=sender)
    if customer:
        lists = lists.filter(Q(customer__username__icontains=customer) | Q(customer__company__icontains=customer))

    if is_global:
        is_global = True if is_global.lower() == 'true' else False
        lists.filter(is_global=is_global)
    if is_domain:
        is_domain = True if is_domain.lower() == 'true' else False
        lists.filter(is_domain=is_domain)
    if disabled:
        disabled = True if disabled.lower() == 'true' else False
        lists.filter(disabled=disabled)
    return lists


@login_required
def ajax_get_customer_sender_blacklist(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    lists = _get_customer_sender_blacklist(data)

    if search:
        lists = lists.filter(sender__icontains=search)

    colums = ['id', 'sender', 'is_global', 'is_domain', 'customer', 'disabled', 'creater', 'created', 'operater',
              'operate_time', 'id']

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
        t = TemplateResponse(request, 'mail/ajax_get_customer_sender_blacklist.html', {'d': m})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def customer_sender_blacklist_add(request):
    form = CustomerSenderBlacklistForm()
    if request.method == "POST":
        form = CustomerSenderBlacklistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('customer_sender_blacklist_list'))
    return render_to_response("mail/customer_sender_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def customer_sender_blacklist_batch_add(request):
    form = CustomerSenderBlacklistBatchForm()
    if request.method == "POST":
        form = CustomerSenderBlacklistBatchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            senders = data.pop('senders')
            if data['customer']:
                data['customer'] = data['customer'].id
            success, fail = 0, 0
            import copy

            for s in senders.split('\n'):
                d = copy.deepcopy(data)
                d['sender'] = s.replace('\r', '')
                f = CustomerSenderBlacklistForm(d)
                if f.is_valid():
                    success += 1
                    obj = f.save()
                    obj.creater = request.user
                    obj.save()
                else:
                    fail += 1
            messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
            return HttpResponseRedirect(reverse('customer_sender_blacklist_list'))
    return render_to_response("mail/customer_sender_blacklist_batch_add.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def customer_sender_blacklist_modify(request, customer_sender_blacklist_id):
    customer_sender_blacklist_obj = CustomerSenderBlacklist.objects.get(id=customer_sender_blacklist_id)
    form = CustomerSenderBlacklistForm(instance=customer_sender_blacklist_obj)
    if request.method == "POST":
        form = CustomerSenderBlacklistForm(request.POST, instance=customer_sender_blacklist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('customer_sender_blacklist_list'))
    return render_to_response("mail/customer_sender_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def invalidsender_whitelist_list(request):
    invalidsender_whitelists = InvalidSenderWhitelist.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = InvalidSenderWhitelist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            InvalidSenderWhitelist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(reverse('invalidsender_whitelist_list'))
    return render_to_response("mail/invalidsender_whitelist_list.html", {
        'invalidsender_whitelists': invalidsender_whitelists,
    }, context_instance=RequestContext(request))


@login_required
def invalidsender_whitelist_add(request):
    form = InvalidSenderWhitelistForm()
    if request.method == "POST":
        form = InvalidSenderWhitelistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('invalidsender_whitelist_list'))
    return render_to_response("mail/invalidsender_whitelist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def invalidsender_whitelist_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = InvalidSenderWhitelistForm({'sender': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('invalidsender_whitelist_list'))
    return render_to_response("mail/invalidsender_whitelist_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def invalidsender_whitelist_modify(request, invalidsender_whitelist_id):
    invalidsender_whitelist_obj = InvalidSenderWhitelist.objects.get(id=invalidsender_whitelist_id)
    form = InvalidSenderWhitelistForm(instance=invalidsender_whitelist_obj)
    if request.method == "POST":
        form = InvalidSenderWhitelistForm(request.POST, instance=invalidsender_whitelist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('invalidsender_whitelist_list'))
    return render_to_response("mail/invalidsender_whitelist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def ajax_get_checklist(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    lists = SpfChecklist.objects.all()

    if search:
        lists = lists.filter(domain__icontains=search)

    colums = ['id', 'domain', 'direct_reject', 'disabled',  'creater', 'created', 'operater', 'operate_time', 'id']

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
        t = TemplateResponse(request, 'mail/ajax_get_checklist.html', {'d': m})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def spf_checklist_list(request):
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = SpfChecklist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            SpfChecklist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("mail/spf_checklist_list.html", {
    }, context_instance=RequestContext(request))


@login_required
def spf_checklist_add(request):
    form = SpfChecklistForm()
    if request.method == "POST":
        form = SpfChecklistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('spf_checklist_list'))
    return render_to_response("mail/spf_checklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def spf_checklist_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = SpfChecklistForm({'domain': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('spf_checklist_list'))
    return render_to_response("mail/spf_checklist_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def spf_checklist_modify(request, spf_checklist_id):
    spf_checklist_obj = SpfChecklist.objects.get(id=spf_checklist_id)
    form = SpfChecklistForm(instance=spf_checklist_obj)
    if request.method == "POST":
        form = SpfChecklistForm(request.POST, instance=spf_checklist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('spf_checklist_list'))
    return render_to_response("mail/spf_checklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def temp_sender_blacklist_list(request):
    sender_blacklists = TempSenderBlacklist.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = TempSenderBlacklist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        # else:
        # SenderBlacklist.objects.filter(id__in=ids).update(disabled=status)
        # tip = u'禁用' if status else u'启用'
        # msg = u'成功%s%s个' % (tip, len(ids))
        return HttpResponseRedirect(reverse('temp_sender_blacklist_list'))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("mail/temp_sender_blacklist_list.html", {
        'sender_blacklists': sender_blacklists,
    }, context_instance=RequestContext(request))


@login_required
def ajax_add_tempsenderblacklist(request):
    sender = request.GET.get('sender', '')
    days = int(request.GET.get('days', ''))
    customer_id = request.GET.get('customer_id', '')
    if TempSenderBlacklist.objects.filter(sender=sender, expire_time__gt=datetime.datetime.now()):
        msg = u'已存在'
    else:
        expire_time = datetime.datetime.now() + datetime.timedelta(days=days)
        TempSenderBlacklist.objects.create(sender=sender, customer_id=customer_id, operater=request.user,
                                           expire_time=expire_time)
        msg = u'已封{}天'.format(days)
    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")


@login_required
def recipient_whitelist_list(request):
    recipient_whitelists = RecipientWhitelist.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = RecipientWhitelist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            RecipientWhitelist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("mail/recipient_whitelist_list.html", {
        'recipient_whitelists': recipient_whitelists,
    }, context_instance=RequestContext(request))


@login_required
def ajax_get_recipient_whitelist(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    lists = RecipientWhitelist.objects.all()

    if search:
        lists = lists.filter(keyword__icontains=search)

    colums = ['id', 'keyword', 'is_domain', 'disabled', 'creater', 'created', 'operater', 'operate_time']

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
        t = TemplateResponse(request, 'mail/ajax_get_recipient_whitelist.html', {'d': m})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def recipient_whitelist_add(request):
    form = RecipientWhitelistForm()
    if request.method == "POST":
        form = RecipientWhitelistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('recipient_whitelist_list'))
    return render_to_response("mail/recipient_whitelist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def recipient_whitelist_batch_add(request):
    form = RecipientWhitelistBatchForm()
    if request.method == "POST":
        form = RecipientWhitelistBatchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            keywords = data.pop('keywords')
            success, fail = 0, 0
            import copy

            for s in keywords.split('\n'):
                d = copy.deepcopy(data)
                d['keyword'] = s.replace('\r', '')
                f = RecipientWhitelistForm(d)
                if f.is_valid():
                    success += 1
                    obj = f.save()
                    obj.creater = request.user
                    obj.save()
                else:
                    fail += 1
            messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
            return HttpResponseRedirect(reverse('recipient_whitelist_list'))
    return render_to_response("mail/recipient_whitelist_batch_add.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def recipient_whitelist_modify(request, recipient_whitelist_id):
    recipient_whitelist_obj = RecipientWhitelist.objects.get(id=recipient_whitelist_id)
    form = RecipientWhitelistForm(instance=recipient_whitelist_obj)
    if request.method == "POST":
        form = RecipientWhitelistForm(request.POST, instance=recipient_whitelist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('recipient_whitelist_list'))
    return render_to_response("mail/recipient_whitelist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def attachment_type_blacklist_list(request):
    attachment_type_blacklists = AttachmentTypeBlacklist.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = AttachmentTypeBlacklist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            AttachmentTypeBlacklist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("mail/attachment_type_blacklist_list.html", {
        'attachment_type_blacklists': attachment_type_blacklists,
    }, context_instance=RequestContext(request))


@login_required
def attachment_type_blacklist_add(request):
    form = AttachmentTypeBlacklistForm()
    if request.method == "POST":
        form = AttachmentTypeBlacklistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('attachment_type_blacklist_list'))
    return render_to_response("mail/attachment_type_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def attachment_type_blacklist_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = AttachmentTypeBlacklistForm({'keyword': w.replace('\r', ''), 'relay': True, 'collect': True})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('attachment_type_blacklist_list'))
    return render_to_response("mail/attachment_type_blacklist_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def attachment_type_blacklist_modify(request, attachment_type_blacklist_id):
    attachment_type_blacklist_obj = AttachmentTypeBlacklist.objects.get(id=attachment_type_blacklist_id)
    form = AttachmentTypeBlacklistForm(instance=attachment_type_blacklist_obj)
    if request.method == "POST":
        form = AttachmentTypeBlacklistForm(request.POST, instance=attachment_type_blacklist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('attachment_type_blacklist_list'))
    return render_to_response("mail/attachment_type_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def sender_blocked_record_log(request):
    data = request.GET
    form = SenderBlockedRecordSearchForm(data)
    sender = data.get('sender', False)
    customer = data.get('customer', False)

    lists = SenderBlockedRecord.objects.all()
    if sender:
        lists = lists.filter(sender__icontains=sender)
    if customer:
        lists = lists.filter(
            Q(customer__company__icontains=customer) |
            Q(customer__username__icontains=customer)
        )
    try:
        count = lists.count()
    except:
        count = len(lists)

    return render_to_response('mail/sender_blocked_record_log.html', {
        'form': form,
        'count': count,
    }, context_instance=RequestContext(request))


@login_required
def ajax_get_sender_blocked_record_log(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')

    sender = data.get('sender', False)
    customer = data.get('customer', False)
    lists = SenderBlockedRecord.objects.all()
    if sender:
        lists = lists.filter(sender__icontains=sender)
    if customer:
        lists = lists.filter(
            Q(customer__company__icontains=customer) |
            Q(customer__username__icontains=customer)
        )

    if search:
        lists = lists.filter(
            Q(sender__icontains=search) |
            Q(customer__username__icontains=search) |
            Q(customer__company__icontains=search)
        )

    colums = ['id', 'sender', 'customer', 'blocked_days', 'opter', 'opt_time', 'id']

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
        t = TemplateResponse(request, 'mail/ajax_get_sender_blocked_record_log.html', {'d': m})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


def _get_relay_sender_whitelist_data(data):
    sender = data.get('sender', False)
    lists = RelaySenderWhitelist.objects.all()
    if sender:
        lists = lists.filter(sender__icontains=sender)
    return lists


@login_required
def relay_sender_whitelist_list(request):
    data = request.GET
    form = RelaySenderWhitelistSearchForm(data)

    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = RelaySenderWhitelist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            RelaySenderWhitelist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(reverse('relay_sender_whitelist_list'))

    return render_to_response('mail/relay_sender_whitelist_list.html', {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def ajax_get_relay_sender_whitelist_list(request):
    data = request.GET
    lists = _get_relay_sender_whitelist_data(data)
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    if search:
        lists = lists.filter(Q(sender__icontains=search))

    colums = ['id', 'sender', 'disabled', 'created', 'creater', 'operater', 'operate_time', 'id']

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
        t = TemplateResponse(request, 'mail/ajax_get_relay_sender_whitelist_list.html', {'d': m})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def relay_sender_whitelist_modify(request, sender_whitelist_id):
    obj = RelaySenderWhitelist.objects.get(id=sender_whitelist_id)
    form = RelaySenderWhitelistForm(instance=obj)
    if request.method == "POST":
        form = RelaySenderWhitelistForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('relay_sender_whitelist_list'))
    return render_to_response("mail/relay_sender_whitelist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def relay_sender_whitelist_add(request):
    form = RelaySenderWhitelistForm()
    if request.method == "POST":
        form = RelaySenderWhitelistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('relay_sender_whitelist_list'))
    return render_to_response("mail/relay_sender_whitelist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def relay_sender_whitelist_batch_add(request):
    form = RelaySenderWhitelistBatchForm()
    if request.method == "POST":
        form = RelaySenderWhitelistBatchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            senders = data.pop('senders')
            if data['customer']:
                data['customer'] = data['customer'].id
            success, fail = 0, 0
            import copy

            for s in senders.split('\n'):
                d = copy.deepcopy(data)
                d['sender'] = s.replace('\r', '')
                f = RelaySenderWhitelistForm(d)
                if f.is_valid():
                    success += 1
                    obj = f.save()
                    obj.creater = request.user
                    obj.save()
                else:
                    fail += 1
            messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
            return HttpResponseRedirect(reverse('relay_sender_whitelist_list'))
    return render_to_response("mail/relay_sender_whitelist_batch_add.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def spam_rpt_blacklist_list(request):
    spam_rpt_blacklists = SpamRptBlacklist.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = SpamRptBlacklist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            SpamRptBlacklist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("mail/spam_rpt_blacklist_list.html", {
        'spam_rpt_blacklists': spam_rpt_blacklists,
    }, context_instance=RequestContext(request))


@login_required
def spam_rpt_blacklist_add(request):
    form = SpamRptBlacklistForm()
    if request.method == "POST":
        form = SpamRptBlacklistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('spam_rpt_blacklist_list'))
    return render_to_response("mail/spam_rpt_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def spam_rpt_blacklist_batch_add(request):
    form = SpamRptBlacklistBatchForm()
    if request.method == "POST":
        form = SpamRptBlacklistBatchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            recipients = data.pop('recipients')
            success, fail = 0, 0
            import copy

            for r in recipients.split('\n'):
                d = copy.deepcopy(data)
                d['recipient'] = r.replace('\r', '')
                d['customer'] = d['customer'].id
                f = SpamRptBlacklistForm(d)
                if f.is_valid():
                    success += 1
                    obj = f.save()
                    obj.creater = request.user
                    obj.save()
                else:
                    fail += 1
            messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
            return HttpResponseRedirect(reverse('spam_rpt_blacklist_list'))
    return render_to_response("mail/spam_rpt_blacklist_batch_add.html", {
        'form': form
    }, context_instance=RequestContext(request))


@login_required
def spam_rpt_blacklist_modify(request, spam_rpt_blacklist_id):
    spam_rpt_blacklist_obj = SpamRptBlacklist.objects.get(id=spam_rpt_blacklist_id)
    form = SpamRptBlacklistForm(instance=spam_rpt_blacklist_obj)
    if request.method == "POST":
        form = SpamRptBlacklistForm(request.POST, instance=spam_rpt_blacklist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('spam_rpt_blacklist_list'))
    return render_to_response("mail/spam_rpt_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))

def _get_spam_rpt_blacklist(data):
    lists = SpamRptBlacklist.objects.all()
    recipient = data.get('recipient', False)
    customer = data.get('customer', False)
    disabled = data.get('disabled', False)
    if recipient:
        lists = lists.filter(recipient__icontains=recipient)
    if customer:
        lists = lists.filter(Q(customer__username__icontains=customer) | Q(customer__company__icontains=customer))

    if disabled:
        disabled = True if disabled.lower() == 'true' else False
        lists.filter(disabled=disabled)
    return lists

@login_required
def ajax_get_spam_rpt_blacklist(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    lists = _get_spam_rpt_blacklist(data)

    if search:
        lists = lists.filter(recipient__icontains=search)

    colums = ['id', 'recipient', 'customer', 'disabled', 'created', 'operate_time', 'id']

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
        t = TemplateResponse(request, 'mail/ajax_get_spam_rpt_blacklist.html', {'d': m})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def ajax_get_collect_recipient_checklist(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    lists = CollectRecipientChecklist.objects.all()

    if search:
        lists = lists.filter(keyword__icontains=search)

    colums = ['id', 'keyword', 'is_regex', 'disabled', 'creater', 'created', 'operater', 'operate_time']

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
        t = TemplateResponse(request, 'mail/ajax_get_collect_recipient_checklist.html', {'d': m})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def collect_recipient_checklist_list(request):
    lists = CollectRecipientChecklist.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = CollectRecipientChecklist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            CollectRecipientChecklist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("mail/collect_recipient_checklist_list.html", {
        'lists': lists,
    }, context_instance=RequestContext(request))


@login_required
def collect_recipient_checklist_add(request):
    form = CollectRecipientChecklistForm()
    if request.method == "POST":
        form = CollectRecipientChecklistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('collect_recipient_checklist_list'))
    return render_to_response("mail/collect_recipient_checklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def collect_recipient_checklist_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = CollectRecipientChecklistForm({'keyword': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('collect_recipient_checklist_list'))
    return render_to_response("mail/collect_recipient_checklist_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def collect_recipient_checklist_modify(request, id):
    collect_recipient_checklist_obj = CollectRecipientChecklist.objects.get(id=id)
    form = CollectRecipientChecklistForm(instance=collect_recipient_checklist_obj)
    if request.method == "POST":
        form = CollectRecipientChecklistForm(request.POST, instance=collect_recipient_checklist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('collect_recipient_checklist_list'))
    return render_to_response("mail/collect_recipient_checklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def ajax_get_spf_ip_whitelist(request):
    data = request.GET
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    lists = SpfIpWhitelist.objects.all()

    if search:
        lists = lists.filter(keyword__icontains=search)

    colums = ['id', 'keyword', 'disabled', 'creater', 'created', 'operater', 'operate_time']

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
        t = TemplateResponse(request, 'mail/ajax_get_spf_ip_whitelist.html', {'d': m})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def spf_ip_whitelist_list(request):
    spf_ip_whitelists = SpfIpWhitelist.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = SpfIpWhitelist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            SpfIpWhitelist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("mail/spf_ip_whitelist_list.html", {
        'spf_ip_whitelists': spf_ip_whitelists,
    }, context_instance=RequestContext(request))


@login_required
def spf_ip_whitelist_add(request):
    form = SpfIpWhitelistForm()
    if request.method == "POST":
        form = SpfIpWhitelistForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.creater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('spf_ip_whitelist_list'))
    return render_to_response("mail/spf_ip_whitelist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def spf_ip_whitelist_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = SpfIpWhitelistForm({'keyword': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                obj = form.save()
                obj.creater = request.user
                obj.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('spf_ip_whitelist_list'))
    return render_to_response("mail/spf_ip_whitelist_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def spf_ip_whitelist_modify(request, spf_ip_whitelist_id):
    spf_ip_whitelist_obj = SpfIpWhitelist.objects.get(id=spf_ip_whitelist_id)
    form = SpfIpWhitelistForm(instance=spf_ip_whitelist_obj)
    if request.method == "POST":
        form = SpfIpWhitelistForm(request.POST, instance=spf_ip_whitelist_obj)
        if form.is_valid():
            obj = form.save()
            obj.operater = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('spf_ip_whitelist_list'))
    return render_to_response("mail/spf_ip_whitelist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))
