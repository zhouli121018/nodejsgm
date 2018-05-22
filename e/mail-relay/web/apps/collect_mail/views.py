# coding=utf-8
import json
import os

import re
import time
import datetime
import base64

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.db.models import Q, query
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template.response import TemplateResponse
from django.db.models import Count, Sum, Case, When, Value, IntegerField
from django.core.cache import cache
from django.core.servers.basehttp import FileWrapper
from redis_cache import get_redis_connection as get_redis_connection2
from lib.django_redis import get_redis as get_redis_connection

from apps.collect_mail.models import get_mail_model, KeywordBlacklist, CheckSettings, \
    SubjectKeywordBlacklist, Statistics, Settings, DeliverLog, HighRiskFlag, CheckStatistics, MailStateLog, \
    ReviewStatistics
from apps.core.models import Customer
from apps.collect_mail.forms import KeywordBlacklistForm, MailSearchForm, CheckSettingsForm, \
    SubjectKeywordBlacklistForm, MailBaseSearchForm, SettingsForm, HighRiskFlagForm
from apps.mail.models import SubjectKeywordBlacklist as RSubjectKeywordBlacklist, SenderBlacklist as RSenderBlacklist, \
    SenderWhitelist, AttachmentBlacklist
from apps.mail.models import KeywordBlacklist as RKeywordBlacklist
from apps.mail.forms import ActiveSenderForm
from lib.parse_email import ParseEmail
from lib.tools import validate_key
from lib.common import high_light
from apps.mail.check_views import add_sender_whitelist, add_sender_blacklist


@login_required
def mail_summary(request):
    if request.method == "POST":
        action = request.POST.get("action", '')
        if action == "refresh":
            redis = get_redis_connection()
            map(lambda k: redis.delete(k),
                filter(lambda k: k.startswith(':1:_cache:collect_mail_status'), redis.keys()))
            return HttpResponseRedirect(request.get_full_path())
    start = request.GET.get('start', '')
    end = request.GET.get('end', '')
    date_end = datetime.datetime.today()
    date_start = date_end - datetime.timedelta(days=14)
    if start or end:
        if start:
            date_start = datetime.datetime.strptime(start, '%Y-%m-%d')
        if end:
            date_end = datetime.datetime.strptime(end, '%Y-%m-%d')
        if end and not start:
            date_end = date_end - datetime.timedelta(days=30)

    index = 1
    date = date_start
    res = {}
    while True:
        if index > 30 or date > date_end:
            break
        date_str = date.strftime('%Y-%m-%d')
        res[date_str] = get_state_data(date_str)

        date = date + datetime.timedelta(days=1)
        index += 1

    return render_to_response("collect_mail/mail_summary.html", {
        'res': res
    }, context_instance=RequestContext(request))


def get_state_data(date_str):
    key = '_cache:collect_mail_status:{}'.format(date_str)
    if datetime.date.today().strftime('%Y-%m-%d') != date_str:
        rs = cache.get(key)
        if rs:
            return rs
    rs = {}
    model = get_mail_model(date_str.replace('-', ''))
    try:
        rs['count'] = model.objects.count()
        rs['count1'] = model.objects.filter(mail_id=0).count()
    except:
        return rs
    rs['state'] = dict(model.objects.values_list("state").annotate(Count("id")))
    rs['check'] = dict(model.objects.values_list("check_result").annotate(Count("id")))
    rs['review'] = dict(model.objects.values_list("review_result").annotate(Count("id")))
    rs['send'] = {
        'success': model.objects.filter(return_code=250).count(),
        'fail': model.objects.filter(Q(state='finished') | Q(state='bounce')).exclude(return_code=250).count()
    }
    rs['state']['review'] = model.objects.filter(state='review').exclude(check_result='spam').count()
    cache.set(key, rs, 0)
    return rs


def get_all_data(data):
    all_day = data.get('all_day', '')
    date_start = data.get('date_start', '')
    if all_day:
        date_end = datetime.datetime.today()
        date_start = date_end - datetime.timedelta(days=20)
        date = date_start
        mails = []
        while date <= date_end:
            date = date + datetime.timedelta(days=1)
            mails.extend(get_search_data(data, date.strftime('%Y-%m-%d')))
    elif date_start:
        date = data.get('date', '').replace('-', '')
        date_end = datetime.datetime.strptime(date, '%Y%m%d')if date else datetime.datetime.today()
        date_start = datetime.datetime.strptime(date_start.replace('-', ''), '%Y%m%d')
        mails = []
        while date_start <= date_end:
            mails.extend(get_search_data(data, date_start.strftime('%Y-%m-%d')))
            date_start = date_start + datetime.timedelta(days=1)
    else:
        mails = get_search_data(data)
    return mails


def get_search_data(data, date=''):
    if not date:
        date = data.get('date', '')
    customers = data.get('customers', '')
    mail_from = data.get('mail_from', '')
    mail_to = data.get('mail_to', '')
    subject = data.get('subject', '')
    state = data.get('state', '')
    error_type = data.get('error_type', '')
    dspam_study = data.get('dspam_study', '')
    check = data.get('check', '')
    check_message = data.get('check_message', '')
    not_check = data.get('not_check', '')
    review = data.get('review', '')
    send = data.get('send', '')
    mail_id = data.get('mail_id', '')
    customer = data.get('customer', '')
    customer_report = data.get('customer_report', '')
    search = data.get('search[value]', '')
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    show = data.get('show', '')
    reviewer_id = data.get('reviewer_id', '')
    client_ip = data.get('client_ip', '')
    server_id = data.get('server_id', '')
    filter_word = data.get('filter_word', '')
    reviewer = data.get('reviewer', '')
    all_check = data.get('all_check', '')
    check_list = data.getlist('check', [])
    time_start = data.get('time_start', '')
    time_end = data.get('time_end', '')
    check_list = data.getlist('check', '')

    if not date:
        date = time.strftime('%Y-%m-%d')

    return_code = data.get('return_code', '')

    if not date:
        date = time.strftime('%Y%m%d')
    else:
        date = date.replace('-', '')
    mail_model = get_mail_model(date)

    mails = mail_model.objects.all()
    if customers:
        mails = mails.filter(Q(customer__company__icontains=customers) | Q(customer__username__icontains=customers))
    if mail_from:
        mails = mails.filter(mail_from__icontains=mail_from)
    if mail_to:
        mails = mails.filter(mail_to__icontains=mail_to)
    if customer:
        mails = mails.filter(customer_id=customer)
    if error_type:
        mails = mails.filter(error_type=error_type)
    if dspam_study:
        mails = mails.filter(dspam_study=dspam_study)

    if isinstance(check_list, list) and len(check_list) > 1:
        mails = mails.filter(check_result__in=check_list)
    elif check:
        if check == 'subject_and_keyword':
            mails = mails.filter(check_result__in=['keyword_blacklist', 'subject_blacklist', 'sender_blacklist'])
        else:
            mails = mails.filter(check_result=check)
    if not_check:
        mails = mails.exclude(check_result=not_check)
    if review:
        mails = mails.filter(review_result=review)
    if show == 'sendlog':
        mails = mails.exclude(return_code=None)
    elif show == 'reject':
        mails = mails.filter(state='reject').exclude(
            check_result__in=['auto_reject', 'k_auto_reject', 'auto_reject_attach', 'error_format'])
    elif show == 'review':
        state = 'review'

    if state:
        mails = mails.filter(state=state)

    if check_message:
        mails = mails.filter(check_message__icontains=check_message)

    if send == 'success':
        return_code = '250'
    elif send == 'fail':
        return_code = '0'

    if mail_id:
        if mail_id == '0':
            # all_check 搜索出mail_id=0被"收件人白名单"通过, 但其他收件人需要审核的邮件
            if len(all_check) > 1:
                _mail_ids = mails.exclude(mail_id=0).values_list('mail_id', flat=True).distinct()
                mail_ids = mail_model.objects.filter(id__in=_mail_ids).exclude(state='review').values_list('id', flat=True)
                mails = mails.filter(Q(mail_id=0) | Q(mail_id__in=mail_ids))
            else:
                mails = mails.filter(mail_id=0)
        else:
            mails = mails.filter(Q(mail_id=mail_id) | Q(id=mail_id))
    if subject:
        mails = mails.filter(subject__icontains=subject)

    if client_ip:
        mails = mails.filter(client_ip=client_ip)

    if server_id:
        mails = mails.filter(server_id=server_id)

    if reviewer_id:
        mails = mails.filter(reviewer_id=reviewer_id)

    if search:
        mails = mails.filter(
            Q(mail_from__icontains=search) | Q(mail_to__icontains=search) | Q(subject__icontains=search))

    if return_code:
        if return_code == '0':
            mails = mails.exclude(return_code=250)
        else:
            mails = mails.filter(return_code=return_code)
    if customer_report:
        mails = mails.filter(customer_report=customer_report)

    if filter_word:
       mails = mails.filter(check_message__icontains=filter_word)

    if reviewer:
        mails = mails.filter(reviewer__username=reviewer)

    if time_start:
        time_start = datetime.datetime.strptime('{} {}:00'.format(date, time_start), '%Y%m%d %H:%M:%S')
        mails = mails.filter(created__gte=time_start)
    if time_end:
        time_end = datetime.datetime.strptime('{} {}:00'.format(date, time_end), '%Y%m%d %H:%M:%S')
        mails = mails.filter(created__lte=time_end)

    try:
        mails.exists()
    except:
        mails = []

    if show == 'review':
        colums = ['id', 'customer', 'mail_from', 'subject', 'size', 'created', 'check_message', 'check_result']
    elif show == 'sendlog':
        colums = ['id', 'customer', 'mail_from', 'subject', 'size', 'mail_id', 'created', 'mail_to',
                  'return_code', 'deliver_time', 'return_message']
    elif show == 'reject':
        colums = ['id', 'sender_name', 'subject', 'attach_name', 'attach_name', 'check_result']
    else:
        colums = ['id', 'customer', 'mail_from', 'subject', 'size', 'mail_id', 'created', 'mail_to', 'state',
                  'check_result', 'review_result', 'return_code', 'deliver_time', 'return_message']

    if isinstance(mails, query.QuerySet) and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            mails = mails.order_by('-%s' % colums[int(order_column)])
        else:
            mails = mails.order_by('%s' % colums[int(order_column)])

    return mails


def get_date(data):
    date = data.get('date', '')
    if not date:
        date = time.strftime('%Y%m%d')
    else:
        date = date.replace('-', '')
    return date


@login_required
def mail_list(request):
    if request.method == 'POST':
        ids = (request.POST.get('ids', '')).split(',')
        result = request.POST.get('result', '')
        action = request.POST.get('action', '')
        if action == 'dspam':
            _do_dspam(ids, result)
            messages.add_message(request, messages.SUCCESS, u'{}个邮件已提交dsapm学习'.format(len(ids)))
        elif action == 'review_undo':
            _do_review(ids=ids, result=result, request=request, flag=False)
            messages.add_message(request, messages.SUCCESS, u'{}个邮件已纠错放行'.format(len(ids)))
        elif action == 'resend':
            _resend(ids)
            messages.add_message(request, messages.SUCCESS, u'成功重新投递{}封邮件'.format(len(ids)))
        elif action == 'sender_blacklist':
            for id in ids:
                add_sender_blacklist(id, is_global=True, is_domain=False, user=request.user)
            messages.add_message(request, messages.SUCCESS, u'成功添加{}个全局黑名单'.format(len(ids)))
        return HttpResponseRedirect(request.get_full_path())

    data = request.GET
    form = MailSearchForm(data)
    review_status = {}
    study_status = {}
    """
    if data.get('check', '') == 'auto_reject':
        mails = get_all_data(data)
        review_status = dict(mails.values_list("review_result").annotate(Count("id")))
        study_status = dict(mails.values_list("dspam_study").annotate(Count("id")))
    """

    return render_to_response("collect_mail/mail_list.html", {
        'form': form,
        'date': get_date(form.data),
        'show': data.get('show', ''),
        'review_status': review_status,
        'study_status': study_status,
    }, context_instance=RequestContext(request))


def _do_dspam(ids, result):
    """
    :param ids: 学习的ID列表
    :param result: 结果
    :return:
    """
    keys = {}
    # redis = get_redis_connection()
    for k, v in deal_with_ids(ids).iteritems():
        mail_model = get_mail_model(k)
        servers = mail_model.objects.filter(id__in=v).values_list('server_id', flat=True).distinct()
        for s in servers:
            mails = mail_model.objects.filter(id__in=v, server_id=s)
            keys.setdefault(s, []).extend(map(lambda mail: mail.get_mail_filename(), mails))
            # keys.extend(map(lambda mail: mail.get_mail_filename(), mails))

    for k, v in keys.iteritems():
        try:
            redis = get_redis_connection2(k)
        except:
            redis = get_redis_connection2('default')
        map(lambda key: redis.lpush('dspam_collect_{}'.format(result), key), set(v))


def _resend(ids):
    """
    将邮件推送到队列重新投递
    :param ids:
    :return:
    """
    keys = {}
    # redis = get_redis_connection()
    for k, v in deal_with_ids(ids).iteritems():
        mail_model = get_mail_model(k)
        servers = mail_model.objects.filter(id__in=v).values_list('server_id', flat=True).distinct()
        for s in servers:
            mails = mail_model.objects.filter(id__in=v, server_id=s, state__in=['reject', 'finished', 'fail_finished'])
            keys.setdefault(s, []).extend(map(lambda mail: mail.get_mail_filename(), mails))
            mails.update(state='retry')
            # keys.extend(map(lambda mail: mail.get_mail_filename(), mails))
    for k, v in keys.iteritems():
        try:
            redis = get_redis_connection2(k)
        except:
            redis = get_redis_connection2('default')
        map(lambda key: redis.lpush('collect_send', key), set(v))


@login_required
def keyword_blacklist_list(request):
    keyword_blacklists = KeywordBlacklist.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = KeywordBlacklist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            KeywordBlacklist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("collect_mail/keyword_blacklist_list.html", {
        'keyword_blacklists': keyword_blacklists,
    }, context_instance=RequestContext(request))


@login_required
def keyword_blacklist_add(request):
    form = KeywordBlacklistForm()
    if request.method == "POST":
        form = KeywordBlacklistForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('c_keyword_blacklist_list'))
    return render_to_response("collect_mail/keyword_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def keyword_blacklist_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = KeywordBlacklistForm({'keyword': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                form.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('c_keyword_blacklist_list'))
    return render_to_response("collect_mail/keyword_blacklist_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def keyword_blacklist_modify(request, keyword_blacklist_id):
    keyword_blacklist_obj = KeywordBlacklist.objects.get(id=keyword_blacklist_id)
    form = KeywordBlacklistForm(instance=keyword_blacklist_obj)
    if request.method == "POST":
        form = KeywordBlacklistForm(request.POST, instance=keyword_blacklist_obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('c_keyword_blacklist_list'))
    return render_to_response("collect_mail/keyword_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def subject_keyword_blacklist_list(request):
    subject_keyword_blacklists = SubjectKeywordBlacklist.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = SubjectKeywordBlacklist.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            SubjectKeywordBlacklist.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("collect_mail/subject_keyword_blacklist_list.html", {
        'subject_keyword_blacklists': subject_keyword_blacklists,
    }, context_instance=RequestContext(request))


@login_required
def subject_keyword_blacklist_add(request):
    form = SubjectKeywordBlacklistForm()
    if request.method == "POST":
        form = SubjectKeywordBlacklistForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('c_subject_keyword_blacklist_list'))
    return render_to_response("collect_mail/subject_keyword_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def subject_keyword_blacklist_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = SubjectKeywordBlacklistForm({'keyword': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                form.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('c_subject_keyword_blacklist_list'))
    return render_to_response("collect_mail/subject_keyword_blacklist_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def subject_keyword_blacklist_modify(request, subject_keyword_blacklist_id):
    subject_keyword_blacklist_obj = SubjectKeywordBlacklist.objects.get(id=subject_keyword_blacklist_id)
    form = SubjectKeywordBlacklistForm(instance=subject_keyword_blacklist_obj)
    if request.method == "POST":
        form = SubjectKeywordBlacklistForm(request.POST, instance=subject_keyword_blacklist_obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('c_subject_keyword_blacklist_list'))
    return render_to_response("collect_mail/subject_keyword_blacklist_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def mail_review(request):
    form = MailBaseSearchForm(request.GET)
    id = request.GET.get('id', '')
    result = request.GET.get('result', '')
    # date = get_date(request.GET)

    # 单个ajax审核
    if id and result:
        if result.find('_pass') != -1 or result.find('_reject') != -1:
            is_global = True if result.find('global') != -1 else False
            is_domain = True if result.find('domain') != -1 else False
            if result.find('_pass') != -1:
                add_sender_whitelist(id, is_global=is_global, is_domain=is_domain, user=request.user)
                result = 'pass'
            else:
                add_sender_blacklist(id, is_global=is_global, is_domain=is_domain, user=request.user)
                result = 'reject'

        msg, count = _do_review([id], result, request)
        return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")
    # 批量审核
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        result = request.POST.get('result', '')
        if result == 'empty':
            data = {'all_day': 1, 'check': 'spam', 'state': 'review', 'mail_id': '0'}
            mails = get_all_data(data)
            ids = [m.date_id() for m in mails]
            msg, count = _do_review(ids, 'reject', request)
        elif result == 'white_sender_pass':
            for id in ids:
                add_sender_whitelist(id, user=request.user)
            msg, count = _do_review(ids, 'pass', request)
        else:
            msg, count = _do_review(ids, result, request)
        messages.add_message(request, messages.SUCCESS, u'成功{}{}个邮件'.format(msg, count))

    return render_to_response("collect_mail/mail_review.html", {
        'form': form,
        'not_all_pass': ['custom_blacklist', 'spam']
    }, context_instance=RequestContext(request))


def _do_review(ids, result, request, flag=True):
    """
    :param ids: 审核的ID列表
    :param result: 审核结果
    :param flag: 是否正常流程操作， 默认：True, 如果是误判操作，则为False
    :return:
    """
    keys = {}
    # redis = get_redis_connection()
    reviewer = request.user
    review_time = datetime.datetime.now()
    msg = u'通过' if result == 'pass' else u'拒绝'
    for k, v in deal_with_ids(ids).iteritems():
        if flag:
            mails = get_mail_model(k).objects.filter(state='review').filter(Q(id__in=v) | Q(mail_id__in=v))
        else:
            mails = get_mail_model(k).objects.filter(id__in=v)

        servers = mails.values_list('server_id', flat=True).distinct()
        for s in servers:
            keys.setdefault(s, []).extend(map(lambda mail: mail.get_mail_filename(), mails.filter(server_id=s)))
        # keys.extend(map(lambda mail: mail.get_mail_filename(), mails))
        review_result = result if flag else '{}_undo'.format(result)
        if result == 'pass':
            if flag:
                mails.update(review_result=review_result, state='send', reviewer=reviewer, review_time=review_time)
            else:
                mails.update(review_result=review_result, state='send')
        elif result == 'reject':
            if flag:
                mails.update(review_result=review_result, state='reject', reviewer=reviewer, review_time=review_time)
            else:
                mails.update(review_result=review_result, state='reject')

    count = 0
    for k, v in keys.iteritems():
        count += len(v)
        try:
            redis = get_redis_connection2(k)
        except:
            redis = get_redis_connection2('default')
        for m in set(v):
            if result == 'pass':
                redis.lpush('collect_send', m)
                reason = 'review_pass'
            else:
                reason = 'review_reject'
            redis.lpush('dspam_collect_{}'.format(result), m)
            redis.lpush('csender_credit', '{}----{}'.format('_'.join(m.split(',')), reason))

        """
        if result == 'pass':
            map(lambda key: redis.lpush('collect_send', key), set(v))
        map(lambda key: redis.lpush('dspam_collect_{}'.format(result), key), set(v))
        """

    return msg, count


@login_required
def mail_review_undo(request):
    ids = request.GET.get('id', '')
    date, id = ids.split('_')
    mail_obj = get_mail_model(date).objects.get(id=id)
    # if not mail_obj.get_mail_content():
    #     msg = u'操作失败：邮件内容不存在'
    # else:
    undo_review_result = 'pass' if mail_obj.review_result == 'reject' else 'reject'
    _do_review([ids], undo_review_result, request, flag=False)
    msg = u'误判操作成功：{}'.format(undo_review_result)
    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")


def deal_with_ids(ids):
    rs = {}
    for k in ids:
        date, id = k.strip().split('_')
        rs.setdefault(date, []).append(id)
    return rs


def send_mail_file(request):
    if not validate_key(request):
        raise Http404
    date_id = request.GET.get('id', '')
    date, id = date_id.split('_')
    if id and date:
        mail_obj = get_mail_model(date).objects.get(id=id)
        filename = mail_obj.get_mail_path()
        if not os.path.exists(filename):
            filename = mail_obj.get_mail_path_old()
        if os.path.exists(filename):
            wrapper = FileWrapper(file(filename))
            response = HttpResponse(wrapper, content_type='text/plain')
            response['Content-Length'] = os.path.getsize(filename)
            return response
    return HttpResponse('')

def mail_modify_spam(request):
    date_id = request.GET.get('id', False)
    mail_date, mail_id = date_id.split('_')
    action = request.GET.get('action', False)
    auth_key = request.GET.get('auth_key', False)
    decoded = base64.b64decode(auth_key)
    private_tr, action2, mail_date2, mail_id2 = decoded.split('_')
    if mail_id and mail_date and action:
        if action == action2 and mail_date == mail_date2 and mail_id == mail_id2:
            try:
                mail_obj = get_mail_model(mail_date).objects.get(id=mail_id)
            except Exception as e:
                return HttpResponse(u'页面不存在 (404)')

            if action == 'delete':
                file_path = mail_obj.get_mail_path()
                if mail_obj.review_result == 'reject':
                    if os.path.exists(file_path):
                        mail_obj.clear_mail()
                        return HttpResponse(u'删除邮件成功')
                    else:
                        return HttpResponse(u'删除邮件成功')
                else:
                    return HttpResponse(u'邮件正在处理中，不能进行删除操作')

                # mail_obj.clear_mail()
                # return HttpResponse(u'删除邮件成功')

            if action == 'whitelist':
                add_sender_whitelist(date_id, is_global=False, is_domain=False)
                if mail_obj.review_result == 'reject':
                    undo_review_result = 'pass'
                    _do_review([date_id], undo_review_result, request, flag=False)
                    return HttpResponse(u'添加白名单成功')
                else:
                    return HttpResponse(u'添加白名单成功')

                # undo_review_result = 'pass' if mail_obj.review_result == 'reject' else 'reject'
                # _do_review([date_id], undo_review_result, request, flag=False)
                # return HttpResponse(u'添加白名单成功')

            if action == 'deliver':
                if mail_obj.review_result == 'reject':
                    undo_review_result = 'pass'
                    _do_review([date_id], undo_review_result, request, flag=False)
                    return HttpResponse(u'邮件放行成功')
                else:
                    return HttpResponse(u'邮件放行成功')

                # undo_review_result = 'pass' if mail_obj.review_result == 'reject' else 'reject'
                # _do_review([date_id], undo_review_result, request, flag=False)
                # return HttpResponse(u'邮件放行成功')

        else:
            return HttpResponse(u'页面不存在 (404)')
    else:
            return HttpResponse(u'页面不存在 (404)')

@login_required
def mail_read(request):
    date_id = request.GET.get('id', '')
    date, id = date_id.split('_')
    cid = request.GET.get('cid', '')
    aid = request.GET.get('aid', '')
    download = request.GET.get('download', '')
    view_body = request.GET.get('view_body', '')
    view_source = request.GET.get('view_source', '')
    export = request.GET.get('export', '')

    if id and date:
        mail_obj = get_mail_model(date).objects.get(id=id)
        content = mail_obj.get_mail_content()
        parse_obj = ParseEmail(content)
        m = parse_obj.parseMailTemplate()

        if cid or aid:
            attachments = m['attachments']
            if aid:
                attach = attachments[int(aid)]
                response = HttpResponse(attach.get('data', ''),
                                        content_type=attach.get('content_type', '').split(';')[0])
            else:
                for one in attachments:
                    if one.get('content_id') == cid:
                        attach = one
                        response = HttpResponse(attach.get('data', ''),
                                                content_type=attach.get('content_type', '').split(';')[0])
                        break
            if download:
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(
                    attach.get('decode_name', '').replace('\n', ' ').encode('utf-8'))
            return response

        if view_body:
            text = m.get('html_text', '')
            charset = m.get('html_charset', '')
            if not text:
                text = m.get('plain_text', '')
                charset = m.get('plain_charset', '')
            link = '{}?id={}&cid=\g<cid>'.format(reverse('collect_mail_read'), date_id)
            text = re.sub('"cid:(?P<cid>.*?)"', link, text)

            if mail_obj.check_result in ['keyword_blacklist', 'custom_blacklist'] and text and charset:
                s = mail_obj.check_message.split('----', 1)[-1]
                re_s = u'<span style="background-color: yellow"><b style="color:#A94442;">{}</b></span>'.format(
                    s).encode(charset)
                s = s.encode(charset)
                text = text.replace(s, re_s)
            return HttpResponse(text, charset=charset)
        if view_source:
            return render_to_response("collect_mail/txt.html", {
                'content': content.decode('gbk', 'ignore'),
            }, context_instance=RequestContext(request))

        if export:
            response = HttpResponse(content, content_type='text/html')
            response['Content-Disposition'] = 'attachment; filename="eml.eml"'
            return response

        subject = mail_obj.subject
        if mail_obj.check_result in ['subject_blacklist', 'custom_blacklist']:
            s = mail_obj.check_message.split('----', 1)[-1]
            subject = high_light(subject, s)
        hl_mail_from = mail_obj.mail_from
        if mail_obj.check_result == 'sender_blacklist':
            s = mail_obj.check_message.split('----', 1)[-1]
            hl_mail_from = high_light(mail_obj.mail_from, s)
            m['from'] = high_light(m['from'], s)

        return render_to_response("collect_mail/mail_read.html", {
            'm': m,
            'id': id,
            'date': date,
            'mail_obj': mail_obj,
            'subject': subject,
            'hl_mail_from': hl_mail_from,
        }, context_instance=RequestContext(request))
    return HttpResponse(u'no email')


@login_required
def ajax_get_mails(request):
    data = request.GET

    mails = get_all_data(data)

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
        t = TemplateResponse(request, 'collect_mail/ajax_get_mails.html', {'m': m, 'date': m.get_date()})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def check_settings(request):
    settings = CheckSettings.objects.all()
    if settings:
        form = CheckSettingsForm(instance=settings[0])
    else:
        form = CheckSettingsForm()
    if request.method == "POST":
        if settings:
            form = CheckSettingsForm(request.POST, instance=settings[0])
        else:
            form = CheckSettingsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('collect_check_settings'))
    return render_to_response("collect_mail/check_settings.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def report_spam(request):
    ids = request.GET.get('id', '')
    result = request.GET.get('result', '')
    result = 'pass' if result == 'innocent' else 'reject'
    msg = u'已报告'
    _do_dspam([ids], result)
    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")


@login_required
def mail_recheck(request):
    date = request.GET.get('date', '')
    if date:
        mails = get_mail_model(date).objects.filter(check_result='error', state='review', mail_id=0)
        # mails = get_mail_model(date).objects.filter(state='check', mail_id=0)
        for mail in mails:
            mail.state = 'check'
            mail.save()
            redis = get_redis_connection2(mail.server_id)
            try:
                redis.lpush('collect_incheck', mail.get_mail_filename())
            except:
                pass
    messages.add_message(request, messages.SUCCESS, u'出错邮件已重新加入检测')
    return HttpResponseRedirect(reverse('collect_mail_summary'))


@login_required
def statistics(request):
    type = request.GET.get('type', '')
    customer = request.GET.get('customer', '')
    statistics = Statistics.objects.filter(date__gt=(datetime.date.today() - datetime.timedelta(days=10)))
    if type:
        statistics = statistics.filter(type=type)
    if customer:
        statistics = statistics.filter(customer_id=customer)

    return render_to_response("collect_mail/statistics.html", {
        'statistics': statistics,
        'type': type
    }, context_instance=RequestContext(request))


@login_required
def op_keywordlist(request):
    operate = request.GET.get('operate', 'modify')
    msg = u'错误: 没有该关键字信息'
    try:
        # date = request.GET.get('date')
        date, id = request.GET.get('id').split('_')
        mail_obj = get_mail_model(date.replace('-', '')).objects.get(pk=id)
        keyword = mail_obj.check_message.split('----', 1)[0]
        if mail_obj.check_result == 'subject_blacklist' or 'subject_blacklist' in mail_obj.check_message:
            obj = RSubjectKeywordBlacklist.objects.get(keyword=keyword)
            url = reverse('subject_keyword_blacklist_modify', args=(obj.id,))
        elif mail_obj.check_result == 'keyword_blacklist' or 'keyword_blacklist' in mail_obj.check_message:
            obj = RKeywordBlacklist.objects.get(keyword=keyword)
            url = reverse('keyword_blacklist_modify', args=(obj.id,))
        elif mail_obj.check_result == 'sender_blacklist' or 'sender_blacklist' in mail_obj.check_message:
            obj = RSenderBlacklist.objects.get(keyword=keyword)
            url = reverse('sender_blacklist_modify', args=(obj.id,))
        elif mail_obj.check_result == 'sender_whitelist':
            keyword = re.findall('\((.*?)\)', mail_obj.check_message)[0].split('----', 1)[0]
            obj = SenderWhitelist.objects.get(sender=keyword)
            url = reverse('sender_whitelist_modify', args=(obj.id,))
        elif mail_obj.check_result in ['attach_blacklist', 'high_risk'] or 'attach_blacklist' in mail_obj.check_message:
            obj = AttachmentBlacklist.objects.get(keyword=keyword)
            url = reverse('attachment_blacklist_modify', args=(obj.id,))

        if operate == 'modify':
            return HttpResponseRedirect(url)
        elif operate == 'delete':
            obj.delete()
            msg = u'删除成功'
            return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")
    except Exception, e:
        if operate == 'modify':
            return HttpResponse(msg)
        elif operate == 'delete':
            return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")


@login_required
def settings(request):
    settings = Settings.objects.all()
    if settings:
        form = SettingsForm(instance=settings[0])
    else:
        form = SettingsForm()
    if request.method == "POST":
        if settings:
            form = SettingsForm(request.POST, instance=settings[0])
        else:
            form = SettingsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('collect_settings'))
    return render_to_response("collect_mail/settings.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def deliver_logs(request, id):
    date, mail_id = id.split('_')
    logs = DeliverLog.objects.filter(date=date, mail_id=mail_id)
    m = get_mail_model(date).objects.get(id=mail_id)
    return render_to_response("collect_mail/deliver_logs.html", {
        'logs': logs,
        'm': m,
    }, context_instance=RequestContext(request))


@login_required
def high_risk_flag_list(request):
    high_risk_flags = HighRiskFlag.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = HighRiskFlag.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            HighRiskFlag.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("collect_mail/high_risk_flag_list.html", {
        'high_risk_flags': high_risk_flags,
    }, context_instance=RequestContext(request))


@login_required
def high_risk_flag_add(request):
    form = HighRiskFlagForm()
    if request.method == "POST":
        form = HighRiskFlagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('c_high_risk_flag_list'))
    return render_to_response("collect_mail/high_risk_flag_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def high_risk_flag_batch_add(request):
    if request.method == "POST":
        words = request.POST.get('words', '')
        success, fail = 0, 0
        for w in words.split('\n'):
            form = HighRiskFlagForm({'keyword': w.replace('\r', '')})
            if form.is_valid():
                success += 1
                form.save()
            else:
                fail += 1
        messages.add_message(request, messages.SUCCESS, u'批量添加成功{}个, 失败{}个'.format(success, fail))
        return HttpResponseRedirect(reverse('c_high_risk_flag_list'))
    return render_to_response("collect_mail/high_risk_flag_batch_add.html", {
    }, context_instance=RequestContext(request))


@login_required
def high_risk_flag_modify(request, high_risk_flag_id):
    high_risk_flag_obj = HighRiskFlag.objects.get(id=high_risk_flag_id)
    form = HighRiskFlagForm(instance=high_risk_flag_obj)
    if request.method == "POST":
        form = HighRiskFlagForm(request.POST, instance=high_risk_flag_obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('c_high_risk_flag_list'))
    return render_to_response("collect_mail/high_risk_flag_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def check_statistics(request):
    start = request.GET.get('start', '')
    end = request.GET.get('end', '')
    date_end = datetime.datetime.today()
    date_start = date_end - datetime.timedelta(days=30)
    if start or end:
        if start:
            date_start = datetime.datetime.strptime(start, '%Y-%m-%d')
        if end:
            date_end = datetime.datetime.strptime(end, '%Y-%m-%d')
        if end and not start:
            date_end = date_end - datetime.timedelta(days=30)

    res = CheckStatistics.objects.filter(date__gte=date_start, date__lte=date_end)

    return render_to_response("collect_mail/check_statistics.html", {
        'res': res
    }, context_instance=RequestContext(request))


@login_required
def state_logs(request, id):
    date, mail_id = id.split('_')
    logs = MailStateLog.objects.filter(date=date, mail_id=mail_id)
    m = get_mail_model(date).objects.get(id=mail_id)
    return render_to_response("collect_mail/state_logs.html", {
        'logs': logs,
        'm': m,
    }, context_instance=RequestContext(request))


@login_required
def review_statistics(request):
    start = request.GET.get('start', '')
    end = request.GET.get('end', '')
    type = request.GET.get('type', 'all')
    date_end = datetime.datetime.today()
    date_start = date_end - datetime.timedelta(days=30)
    if start or end:
        if start:
            date_start = datetime.datetime.strptime(start, '%Y-%m-%d')
        if end:
            date_end = datetime.datetime.strptime(end, '%Y-%m-%d')
        if end and not start:
            date_end = date_end - datetime.timedelta(days=30)

    res = ReviewStatistics.objects.filter(date__gte=date_start, date__lte=date_end, type=type)

    return render_to_response("collect_mail/review_statistics.html", {
        'res': res
    }, context_instance=RequestContext(request))

@login_required
def resent(request):
    ids = request.GET.get('id', '')
    date, id = ids.split('_')
    msg = u'发送失败，只有发送完成/失败的邮件可以再次发送'
    m = get_mail_model(date).objects.get(id=id)
    if m.state in ['finished', 'fail_finished']:
        redis = get_redis_connection2(m.server_id)
        redis.lpush('collect_send', m.get_mail_filename())
        m.state = 'retry'
        m.save()
        msg = u'已再次发送邮件'
    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")

def _get_active_receiver_list(data, date):
    mail_model = get_mail_model(date)
    customer_id = data.get('customer_id', '')

    if customer_id:
        mails = mail_model.objects.filter(customer_id=customer_id)
    else:
        mails = mail_model.objects.all()
    mails = mails.values("mail_to").annotate(total_all=Count("id"), size=Sum("size"),
                                             total=Sum(Case(When(mail_id=0, then=Value(1)), default=Value(0),
                                                            output_field=IntegerField())),
                                             total_success=Sum(
                                                 Case(When(state='finished', then=Value(1)), default=Value(0),
                                                      output_field=IntegerField())),
                                             size_success=Sum(
                                                 Case(When(state='finished', then='size'), default=Value(0),
                                                      output_field=IntegerField())),
                                             total_reject=Sum(Case(When(
                                                 Q(state='reject') | Q(state='c_reject'),
                                                 then=Value(1)), default=Value(0), output_field=IntegerField())),
                                             size_reject=Sum(Case(When(
                                                 Q(state='reject') | Q(state='c_reject'),
                                                 then='size'), default=Value(0), output_field=IntegerField())),
                                             total_fail=Sum(Case(When(
                                                 Q(state='fail_finished') | Q(state='bounce'),
                                                 then=Value(1)), default=Value(0), output_field=IntegerField())),
                                             size_fail=Sum(Case(When(
                                                 Q(state='fail_finished') | Q(state='bounce'),
                                                 then='size'), default=Value(0), output_field=IntegerField())),
                                             total_out=Sum(Case(When(
                                                 Q(state='finished') | Q(state='fail_finished') | Q(state='bounce'),
                                                 then=Value(1)), default=Value(0), output_field=IntegerField())),
                                             size_out=Sum(Case(When(
                                                 Q(state='finished') | Q(state='fail_finished') | Q(state='bounce'),
                                                 then='size'), default=Value(0), output_field=IntegerField())),
                                             )
    try:
        mails.exists()
    except:
        mails = []
    return mails


def get_active_receiver_list(data):
    date = data.get('date', '')
    if not date:
        date = datetime.date.today().strftime('%Y%m%d')
    else:
        date = date.replace('-', '')
    return _get_active_receiver_list(data, date)

@login_required
def active_receiver_list(request):
    data = request.GET
    form = ActiveSenderForm(data)

    mails = get_active_receiver_list(data)
    customer = None
    customer_id = request.GET.get('customer_id', '')
    if customer_id:
        customer = Customer.objects.get(id=customer_id)
    return render_to_response("collect_mail/active_receiver_list.html", {
        'mails': mails,
        'form': form,
        'customer': customer
    }, context_instance=RequestContext(request))

