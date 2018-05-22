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
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, Http404
from django.core.urlresolvers import reverse
from django.db.models import Q, query, F
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template.response import TemplateResponse
from django.db.models import Count, Sum, Case, When, Value, IntegerField
from django.core.cache import cache
from django.core.servers.basehttp import FileWrapper
from redis_cache import get_redis_connection as get_redis_connection2
from lib.django_redis import get_redis as get_redis_connection

from apps.mail.models import get_mail_model, KeywordBlacklist, CheckSettings, \
    SubjectKeywordBlacklist, BounceSettings, Statistics, \
    SenderBlacklist, Settings, DeliverLog, SpfError, CustomKeywordBlacklist, \
    AttachmentBlacklist, MailStateLog, BulkCustomer, CheckStatistics, ReviewStatistics, \
    NoticeSettings, RecipientWhitelist, TempSenderBlacklist, SenderBlockedRecord, SpamRptSettings, SenderCreditSettings, \
    SenderCredit, SenderCreditLog, RelaySenderWhitelist, CreditIntervalSettings, EdmCheckSettings
from apps.core.models import Customer, IpPool, Cluster, Notification
from apps.mail.forms import MailSearchForm, CheckSettingsForm, \
    BounceSettingsForm, MailBaseSearchForm, SettingsForm, DateSearchForm, SpfErrorForm, BulkCustomerForm, \
    NoticeSettingsForm, RecipientWhitelistForm, SpamRptSettingsForm, SenderCreditSettingsForm, \
    SenderCreditBaseSearchForm, CreditIntervalSettingsForm, SenderCreditForm, EdmCheckSettingsForm, ActiveSenderForm
from apps.collect_mail.views import get_all_data as get_all_data2
from lib.parse_email import ParseEmail
from lib.email_sender import MailSender
from lib.tools import validate_key
from lib.report_spam import dspamc
from lib.common import high_light


@login_required
def mail_summary(request):
    if request.method == "POST":
        action = request.POST.get("action", '')
        if action == "refresh":
            redis = get_redis_connection()
            map(lambda k: redis.delete(k), filter(lambda k: k.startswith(':1:_cache:relay_mail_status'), redis.keys()))
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

    return render_to_response("mail/mail_summary.html", {
        'res': res
    }, context_instance=RequestContext(request))


def get_state_data(date_str):
    key = '_cache:relay_mail_status:{}'.format(date_str)
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
    rs['state']['review'] = model.objects.filter(state='review').exclude(check_result__in=['spam', 'k_auto_reject']).count()
    cache.set(key, rs, 0)
    return rs


def get_all_data(data):
    all_day = data.get('all_day', '')
    date_start = data.get('date_start', '')
    if all_day:
        date_end = datetime.datetime.today()
        date_start = date_end - datetime.timedelta(days=10)
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
    state = data.get('state', '')
    check = data.get('check', '')
    reviewer_id = data.get('reviewer_id', '')
    check_list = data.getlist('check', '')
    try:
        not_check = filter(lambda a: bool(a), data.getlist('not_check', ''))
    except BaseException, e:
        not_check = []
    review = data.get('review', '')
    send = data.get('send', '')
    bounce = data.get('bounce', '')
    mail_id = data.get('mail_id', '')
    error_type = data.get('error_type', '')
    dspam_study = data.get('dspam_study', '')
    ip = data.get('ip', '')
    ip_pool = data.get('ip_pool', '')
    cluster = data.get('cluster', '')
    customer = data.get('customer', '')
    subject = data.get('subject', '')
    customer_report = data.get('customer_report', '')
    search = data.get('search[value]', '')
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    show = data.get('show', '')
    client_ip = data.get('client_ip', '')
    server_id = data.get('server_id', '')
    return_message = data.get('return_message', '')
    bulk_sample = data.get('bulk_sample', '')
    filter_word = data.get('filter_word', '')
    reviewer = data.get('reviewer', '')
    is_del_attach = data.get('is_del_attach', '')
    all_check = data.get('all_check', '')
    time_start = data.get('time_start', '')
    time_end = data.get('time_end', '')

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
    if error_type:
        mails = mails.filter(error_type=error_type)
    if dspam_study:
        mails = mails.filter(dspam_study=dspam_study)
    if ip:
        mails = mails.filter(deliver_ip=ip)
    if ip_pool:
        ips = list(IpPool.objects.get(id=ip_pool).clusterip_set.values_list('ip', flat=True))
        mails = mails.filter(deliver_ip__in=ips)
    if cluster:
        ips = list(Cluster.objects.get(id=cluster).cluster.values_list('ip', flat=True))
        mails = mails.filter(deliver_ip__in=ips)
    if customer:
        mails = mails.filter(customer_id=customer)

    if isinstance(check_list, list) and len(check_list) > 1:
        mails = mails.filter(check_result__in=check_list)
    elif check:
        if check == 'subject_and_keyword':
            mails = mails.filter(check_result__in=['keyword_blacklist', 'subject_blacklist', 'sender_blacklist'])
        else:
            mails = mails.filter(check_result=check)

    if not_check:
        mails = mails.exclude(check_result__in=not_check)
    if review:
        mails = mails.filter(review_result=review)
    if show == 'sendlog':
        mails = mails.exclude(return_code=None)
    elif show == 'bouncelog':
        mails = mails.exclude(bounce_result=None)
    elif show == 'review':
        state = 'review'
    elif show == 'reject':
        mails = mails.filter(state='reject').exclude(
            check_result__in=['auto_reject', 'k_auto_reject', 'auto_reject_attach', 'error_format'])

    if state:
        mails = mails.filter(state=state)
    if reviewer_id:
        mails = mails.filter(reviewer_id=reviewer_id)
    if bulk_sample:
        mails = mails.filter(bulk_sample=True)

    if send == 'success':
        return_code = '250'
    elif send == 'fail':
        return_code = '0'

    if bounce:
        mails = mails.filter(bounce_result=bounce)


    if subject:
        mails = mails.filter(subject__icontains=subject)

    if client_ip:
        mails = mails.filter(client_ip=client_ip)
    if server_id:
        mails = mails.filter(server_id=server_id)

    if return_message:
        mails = mails.filter(return_message__icontains=return_message)

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

    if is_del_attach:
        mails = mails.filter(is_del_attach=True)

    if mail_id:
        if mail_id == '0':
            # all_check 搜索出mail_id=0被"收件人白名单"通过, 但其他收件人需要审核的邮件
            if all_check:
                _mail_ids = mails.exclude(mail_id=0).values_list('mail_id', flat=True).distinct()
                mail_ids = mail_model.objects.filter(id__in=_mail_ids).exclude(state='review').values_list('id', flat=True)
                mails = mails.filter(Q(mail_id=0) | Q(mail_id__in=mail_ids))
            else:
                mails = mails.filter(mail_id=0)
        else:
            mails = mails.filter(Q(mail_id=mail_id) | Q(id=mail_id))
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
        colums = ['id', 'customer', 'mail_from', 'subject', 'size', 'mail_id', 'created', 'mail_to', 'deliver_ip',
                  'return_code', 'deliver_time', 'return_message']
    elif show == 'bouncelog':
        colums = ['id', 'customer', 'mail_from', 'subject', 'size', 'mail_id', 'created', 'bounce_time',
                  'bounce_result', 'bounce_message']
    elif show == 'bulk_sample':
        colums = ['id', 'customer', 'mail_from', 'subject', 'size', 'mail_id', 'created', 'mail_to', 'state']
    elif show == 'reject':
        colums = ['id', 'sender_name', 'subject', 'attach_name', 'attach_name', 'check_result']
    else:
        colums = ['id', 'customer', 'mail_from', 'subject', 'size', 'mail_id', 'created', 'mail_to', 'state',
                  'check_result', 'review_result', 'deliver_ip', 'return_code', 'deliver_time', 'return_message',
                  'bounce_time',
                  'bounce_result', 'bounce_message']

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
def mail_list(request, template_name="mail/mail_list.html"):
    if request.method == 'POST':
        ids = (request.POST.get('ids', '')).split(',')
        result = request.POST.get('result', '')
        action = request.POST.get('action', '')
        if action == 'dspam':
            _do_dspam(ids, result)
            messages.add_message(request, messages.SUCCESS, u'{}个邮件已提交dsapm学习'.format(len(ids)))
        elif action == 'review_undo':
            _do_review(ids, result, request, flag=False)
            messages.add_message(request, messages.SUCCESS, u'{}个邮件已纠错放行'.format(len(ids)))
        elif action == 'add_reci_whitelist':
            add_recipient_whitelist(ids, user=request.user)
            messages.add_message(request, messages.SUCCESS, u'成功添加{}个收件人白名单'.format(len(ids)))
        elif action == 'resend':
            _resend(ids)
            messages.add_message(request, messages.SUCCESS, u'成功重新投递{}封邮件'.format(len(ids)))

        return HttpResponseRedirect(request.get_full_path())

    data = request.GET
    show = data.get('show', '')
    form = MailSearchForm(data) if show != 'bulk_sample' else MailBaseSearchForm(data)
    review_status = {}
    study_status = {}
    if data.get('check', '') == 'auto_reject':
        mails = get_all_data(data)
        review_status = dict(mails.values_list("review_result").annotate(Count("id")))
        study_status = dict(mails.values_list("dspam_study").annotate(Count("id")))

    # mails = get_all_data(data)
    return render_to_response(template_name, {
        # 'mails': mails,
        'form': form,
        'date': get_date(form.data),
        'review_status': review_status,
        'study_status': study_status,
        'show': data.get('show', '')
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
        map(lambda key: redis.lpush('dspam_{}'.format(result), key), set(v))


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
            mails.update(state='dispatch', dispatch_data=None)
            # keys.extend(map(lambda mail: mail.get_mail_filename(), mails))

    for k, v in keys.iteritems():
        try:
            redis = get_redis_connection2(k)
        except:
            redis = get_redis_connection2('default')
        map(lambda key: redis.lpush('relay_dispatch', key), set(v))


@login_required
def forbiden_rcpt_white(request):
    ids = request.GET.get('id', '')
    result = request.GET.get('result', '')
    msg = u'已禁用白名单'
    user = request.user
    if ids and result:
        for mail_id in [ids]:
            date, id = mail_id.split('_')
            mail_obj = get_mail_model(date).objects.get(id=id)
            mail_to = mail_obj.mail_to
            if mail_to:
                mail_to = mail_to.lower()
                obj, bool = RecipientWhitelist.objects.get_or_create(keyword=mail_to)
                obj.disabled = True
                obj.is_domain = False
                if user:
                    if bool:
                        obj.creater = user
                    else:
                        obj.operater = user
                obj.save()
    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")

def add_recipient_whitelist(mail_ids=None, is_domain=False, user=None,):
    mail_ids = mail_ids if mail_ids else []
    for mail_id in mail_ids:
        date, id = mail_id.split('_')
        mail_obj = get_mail_model(date).objects.get(id=id)
        mail_to = mail_obj.mail_to
        if mail_to:
            mail_to = mail_to.lower()
            if is_domain:
                mail_to = mail_to.split('@')[-1]

            form = RecipientWhitelistForm({
                'keyword': mail_to,
                'disabled': False,
                'is_domain': is_domain,
            })
            if form.is_valid():
                obj = form.save()
                if user:
                    obj.creater = user
                    obj.save()

            # obj, bool = RecipientWhitelist.objects.get_or_create(keyword=mail_from, disabled=False, is_domain=is_domain)
            # if user:
            #     if bool:
            #         obj.creater = user
            #     else:
            #         obj.operater = user
            #     obj.save()

@login_required
def mail_review(request):
    form = MailBaseSearchForm(request.GET)
    id = request.GET.get('id', '')
    result = request.GET.get('result', '')
    # date = get_date(request.GET)

    # 单个ajax审核
    if id and result:
        if result in ['pass', 'reject']:
            msg, count = _do_review([id], result, request)
            return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")
        if result.endswith('_pass'):
            is_domain = True if result.find('domain') != -1 else False
            add_recipient_whitelist(mail_ids=[id], is_domain=is_domain, user=request.user)
            msg, count = _do_review(ids=[id], result='pass', request=request, flag=True)
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
        elif result == 'recipient_whitelist_pass':
            is_domain = True if result.find('domain') != -1 else False
            add_recipient_whitelist(mail_ids=ids, is_domain=is_domain, user=request.user)
            msg, count = _do_review(ids=ids, result='pass', request=request, flag=True)
        elif result == 'reject_sender':
            # 拒绝所有邮件并封发件人一天
            mails = get_all_data(request.GET)
            ids = []
            mail_froms = {}
            for m in mails:
                ids.append(m.date_id())
                mail_froms.setdefault(m.customer_id, []).append(m.mail_from)
            msg, count = _do_review(ids, 'reject', request)
            days = 1
            for customer_id, v in mail_froms.iteritems():
                for mail_from in set(v):
                    expire_time = datetime.datetime.now() + datetime.timedelta(days=days)
                    SenderBlockedRecord.objects.create(sender=mail_from, customer_id=customer_id, blocked_days=days, opter=request.user)
                    if TempSenderBlacklist.objects.filter(sender=mail_from, expire_time__gt=expire_time):
                        pass
                    elif TempSenderBlacklist.objects.filter(sender=mail_from, expire_time__gt=datetime.datetime.now()):
                        obj = TempSenderBlacklist.objects.filter(sender=mail_from, expire_time__gt=datetime.datetime.now()).first()
                        obj.expire_time = expire_time
                        obj.save()
                    else:
                        TempSenderBlacklist.objects.create(sender=mail_from, customer_id=customer_id, operater=request.user, expire_time=expire_time)
        else:
            msg, count = _do_review(ids, result, request)
        messages.add_message(request, messages.SUCCESS, u'成功{}{}个邮件'.format(msg, count))

    return render_to_response("mail/mail_review.html", {
        'form': form,
        'not_all_pass': ['custom_blacklist', 'subject_and_keyword', 'spam']
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
            # 将mail_id=0的邮件 保存到POP目录
            # map(lambda mail: mail.save_mail_for_pop(), mails.filter(mail_id=0))
            # map(lambda m: dspamc(file_path=m.get_mail_path(), report='innocent', sig=m.dspam_sig), mails)
            if flag:
                mails.update(review_result=review_result, state='dispatch', reviewer=reviewer, review_time=review_time)
            else:
                mails.update(review_result=review_result, state='dispatch')
        elif result == 'reject':
            # map(lambda m: dspamc(file_path=m.get_mail_path(), report='spam', sig=m.dspam_sig), mails)
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
                redis.lpush('relay_dispatch', m)
                reason = 'review_pass'
            else:
                reason = 'review_reject'
            redis.lpush('dspam_{}'.format(result), m)
            redis.lpush('sender_credit', '{}----{}'.format('_'.join(m.split(',')), reason))
        #if result == 'pass':
        #    map(lambda key: redis.lpush('relay_dispatch', key), set(v))
        #map(lambda key: redis.lpush('dspam_{}'.format(result), key), set(v))

    return msg, count


@login_required
def mail_review_undo(request):
    ids = request.GET.get('id', '')
    whitelist = request.GET.get('whitelist', '')
    date, id = ids.split('_')
    mail_obj = get_mail_model(date).objects.get(id=id)
    #if not mail_obj.get_mail_content():
    #    msg = u'操作失败：邮件内容不存在'
    #else:
    undo_review_result = 'pass' if mail_obj.review_result == 'reject' else 'reject'
    _do_review([ids], undo_review_result, request, flag=False)
    msg = u'误判操作成功：{}'.format(undo_review_result)
    if whitelist:
        add_recipient_whitelist([ids], user=request.user)
        msg += u',并加白名单成功'

    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")


def _save_review_result(redis, sender, receiver, result):
    """
    :param redis:
    :param sender:
    :param receiver:
    :param result: 'pass' or 'reject'
    """

    lua = redis.register_script('''
        local sender_receiver, result, time = ARGV[1], ARGV[2], tonumber(ARGV[3])
        local a, b

        a = redis.call('hget', KEYS[1], sender_receiver)
        if a then
            b = cjson.decode(a)
            if b.result == result then
                table.insert(b.history, time)
            else
                b = {result = result, history = {time}}
            end
        else
            b = {result = result, history = {time}}
        end
        redis.call('hset', KEYS[1], sender_receiver, cjson.encode(b))
    ''')

    lua(keys=['relay_review_history'],
        args=['{},{}'.format(sender, receiver), result, time.time()])


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
    is_del_attach = request.GET.get('is_del_attach', '')

    if id and date:
        mail_obj = get_mail_model(date).objects.get(id=id)
        content = mail_obj.get_mail_content(is_del_attach=is_del_attach)
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
            link = '{}?id={}&cid=\g<cid>'.format(reverse('mail_read'), date_id)
            text = re.sub('"cid:(?P<cid>.*?)"', link, text)

            if mail_obj.check_result in ['keyword_blacklist', 'custom_blacklist'] and text and charset:
                s = mail_obj.check_message.split('----', 1)[-1]
                re_s = u'<span style="background-color: yellow"><b style="color:#A94442;">{}</b></span>'.format(
                    s).encode(charset)
                s = s.encode(charset)
                text = text.replace(s, re_s)
            return HttpResponse(text, charset=charset)
        if view_source:
            return render_to_response("mail/txt.html", {
                'content': content.decode('gbk', 'ignore'),
            }, context_instance=RequestContext(request))

        if export:
            response = HttpResponse(content, content_type='text/html')
            response['Content-Disposition'] = 'attachment; filename="eml.eml"'
            return response

        try:
            sender_obj = SenderCredit.objects.get(sender=mail_obj.mail_from.lower())
            sender_credit = sender_obj.credit
        except SenderCredit.DoesNotExist:
            sender_credit = 1000
        blocked_obj = SenderBlockedRecord.objects.filter(sender=mail_obj.mail_from)


        subject = mail_obj.subject
        if mail_obj.check_result in ['subject_blacklist', 'custom_blacklist']:
            s = mail_obj.check_message.split('----', 1)[-1]
            subject = high_light(subject, s)
        hl_mail_from = mail_obj.mail_from
        if mail_obj.check_result == 'sender_blacklist':
            s = mail_obj.check_message.split('----', 1)[-1]
            hl_mail_from = high_light(mail_obj.mail_from, s)
            m['from'] = high_light(m['from'], s)

        return render_to_response("mail/mail_read.html", {
            'm': m,
            'id': id,
            'date': date,
            'mail_obj': mail_obj,
            'subject': subject,
            'hl_mail_from': hl_mail_from,
            'blocked_obj': blocked_obj,
            'sender_credit': sender_credit,
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
        t = TemplateResponse(request, 'mail/ajax_get_mails.html', {'m': m, 'date': m.get_date()})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")


@login_required
def check_settings(request):
    settings = CheckSettings.objects.all()
    type = request.GET.get('type', '')
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
            # 需要重新更新动态发件人名单
            redis = get_redis_connection()
            # redis.delete('relay_spam_sender')
            redis.hset('relay_spam_sender_history', 'is_need_update', 'True')
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('check_settings'))
    if type == 'relay':
        template_name = "mail/check_settings_relay.html"
    elif type == 'collect':
        template_name = "mail/check_settings_collect.html"
    else:
        template_name = "mail/check_settings.html"
    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def report_spam(request):
    ids = request.GET.get('id', '')
    result = request.GET.get('result', '')
    result = 'pass' if result == 'innocent' else 'reject'
    msg = u'已报告'
    _do_dspam([ids], result)
    """
    if id and result in ['innocent', 'spam'] and date:
        mail_obj = get_mail_model(date).objects.get(id=id)
        dspamc(file_path=mail_obj.get_mail_path(), report=result, sig=mail_obj.dspam_sig)
        dspam_study = 1 if result == 'spam' else 2
        mail_obj.dspam_study = dspam_study
        mail_obj.save()
        msg = u'已报告'
    """
    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")


@login_required
def bounce_settings(request):
    settings = BounceSettings.objects.all()
    if settings:
        form = BounceSettingsForm(instance=settings[0])
    else:
        form = BounceSettingsForm()
    if request.method == "POST":
        if settings:
            form = BounceSettingsForm(request.POST, instance=settings[0])
        else:
            form = BounceSettingsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('bounce_settings'))
    return render_to_response("mail/bounce_settings.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def mail_recheck(request):
    date = request.GET.get('date', '')
    # redis = get_redis_connection()
    if date:
        mails = get_mail_model(date).objects.filter(check_result='error', state='review', mail_id=0)
        # mails = get_mail_model(date).objects.filter(state='check', mail_id=0)
        for mail in mails:
            mail.state = 'check'
            mail.save()
            redis = get_redis_connection2(mail.server_id)
            try:
                redis.lpush('relay_incheck', mail.get_mail_filename())
            except:
                pass
    messages.add_message(request, messages.SUCCESS, u'出错邮件已重新加入检测')
    return HttpResponseRedirect(reverse('mail_summary'))


@login_required
def bulk_list(request):
    redis = get_redis_connection()
    bulk_dict = redis.hgetall('relay_incheck_bulk_expire')
    try:
        experied_time = CheckSettings.objects.all()[0].bulk_expire
    except:
        experied_time = 7
    bulk_list = []
    for k, v in bulk_dict.iteritems():
        customer_id, subject = k.split(',', 1)
        customers = Customer.objects.filter(id=customer_id)
        customer = customers[0] if customers else u'已删除客户({})'.format(customer_id)
        bulk_list.append({
            'customer_id': customer_id,
            'customer': customer,
            'subject': subject,
            'count': redis.hget('relay_incheck_bulk', k),
            'created': datetime.datetime.fromtimestamp(float(v)),
            'expired': datetime.datetime.fromtimestamp(float(v) + experied_time * 24 * 60 * 60),
        }
        )
    if request.method == 'POST':
        ids = (request.POST.get('ids', '')).split(',')
        customer_id = request.POST.get('id', '')
        subject = request.POST.get('subject', '')
        if not customer_id:
            for i in ids:
                customer_id, subject = i.split('____', 1)
                delete_bulk(redis, customer_id, subject)
            messages.add_message(request, messages.SUCCESS, u'成功删除{}个群封主题'.format(len(ids)))
        else:
            delete_bulk(redis, customer_id, subject)
            messages.add_message(request, messages.SUCCESS, u'成功删除群封主题: {}'.format(subject))
        return HttpResponseRedirect(reverse('bulk_list'))
    return render_to_response("mail/bulk_list.html", {
        'bulks': bulk_list,
    }, context_instance=RequestContext(request))


def delete_bulk(redis, customer_id, subject):
    if not subject:
        subject = ' '
    key = u'{},{}'.format(customer_id, subject)
    redis.hdel('relay_incheck_bulk', key)
    redis.hdel('relay_incheck_subject', key)
    redis.hdel('relay_incheck_bulk_expire', key)


@login_required
def statistics(request):
    type = request.GET.get('type', '')
    ip = request.GET.get('ip', '')
    ip_pool = request.GET.get('ip_pool', '')
    cluster = request.GET.get('cluster', '')
    customer = request.GET.get('customer', '')
    statistics = Statistics.objects.filter(date__gt=(datetime.date.today() - datetime.timedelta(days=10)))
    if type:
        statistics = statistics.filter(type=type)
    if ip:
        statistics = statistics.filter(ip=ip)
    if ip_pool:
        statistics = statistics.filter(ip_pool_id=ip_pool)
    if cluster:
        statistics = statistics.filter(cluster_id=cluster)
    if customer:
        statistics = statistics.filter(customer_id=customer)

    return render_to_response("mail/statistics.html", {
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
        if mail_obj.check_result == 'subject_blacklist' or mail_obj.check_message.find('subject_blacklist') != -1:
            obj = SubjectKeywordBlacklist.objects.get(keyword=keyword)
            url = reverse('subject_keyword_blacklist_modify', args=(obj.id,))
        elif mail_obj.check_result == 'keyword_blacklist' or mail_obj.check_message.find('keyword_blacklist') != -1:
            obj = KeywordBlacklist.objects.get(keyword=keyword)
            url = reverse('keyword_blacklist_modify', args=(obj.id,))
        elif mail_obj.check_result == 'sender_blacklist' or mail_obj.check_message.find('sender_blacklist') != -1:
            obj = SenderBlacklist.objects.get(keyword=keyword)
            url = reverse('sender_blacklist_modify', args=(obj.id,))
        elif mail_obj.check_result == 'custom_blacklist':
            obj = CustomKeywordBlacklist.objects.filter(keyword=keyword)[0]
            url = reverse('custom_keyword_blacklist_modify', args=(obj.id,))
        elif mail_obj.check_result == 'attach_blacklist' or 'attach_blacklist' in mail_obj.check_message:
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
            return HttpResponseRedirect(reverse('settings'))
    return render_to_response("mail/settings.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def deliver_logs(request, id):
    date, mail_id = id.split('_')
    logs = DeliverLog.objects.filter(date=date, mail_id=mail_id)
    m = get_mail_model(date).objects.get(id=mail_id)
    return render_to_response("mail/deliver_logs.html", {
        'logs': logs,
        'm': m,
    }, context_instance=RequestContext(request))


@login_required
def spf_error_list(request):
    list = SpfError.objects.all()
    # if request.method == "POST":
    # ids = (request.POST.get('ids', '')).split(',')
    #     status = int(request.POST.get('status', ''))
    #     if int(status) == -1:
    #         objs = SpfError.objects.filter(id__in=ids)
    #         objs.update(status='dealed')
    #         msg = u'成功处理%s个' % len(ids)
    #     messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("mail/spf_error_list.html", {
        'list': list,
    }, context_instance=RequestContext(request))


@login_required
def spf_error_modify(request, id):
    obj = SpfError.objects.get(id=id)
    form = SpfErrorForm(instance=obj)
    if request.method == "POST":
        form = SpfErrorForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            obj.status = 'dealed'
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'已处理')
            return HttpResponseRedirect(reverse('spf_error_list'))
    return render_to_response("mail/spf_error_modify.html", {
        'form': form,
        'obj': obj,
    }, context_instance=RequestContext(request))


@login_required
def bulk_customer_list(request):
    date = request.GET.get('date', time.strftime('%Y%m%d')).replace('-', '')
    mail_model = get_mail_model(date)
    customers = mail_model.objects.filter(check_result='bulk_email').values('customer', 'customer__username',
                                                                            'customer__company').annotate(
        count=Count("customer")).order_by('-count')
    for c in customers:
        c['mail_from'] = mail_model.objects.filter(check_result='bulk_email', customer=c['customer']).values_list(
            'mail_from', flat=True).distinct()
    form = DateSearchForm(request.GET)
    try:
        customers.exists()
    except:
        customers = []

    return render_to_response("mail/bulk_customer_list.html", {
        'customers': customers,
        'form': form,
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
    model.save()
    class_name = 'glyphicon-ok' if t else 'glyphicon-remove'
    msg = u'<span class="glyphicon {}"><span class="hidden">{}</span></span>'.format(class_name, t)

    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")


@login_required
def state_logs(request, id):
    date, mail_id = id.split('_')
    logs = MailStateLog.objects.filter(date=date, mail_id=mail_id)
    m = get_mail_model(date).objects.get(id=mail_id)
    return render_to_response("mail/state_logs.html", {
        'logs': logs,
        'm': m,
    }, context_instance=RequestContext(request))


@login_required
def bulk_customer(request):
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
    cus = BulkCustomer.objects.filter(date__gte=date_start, date__lte=date_end).order_by('-date', '-recent_count')
    res_list = []
    cus_list = []
    for c in cus:
        customer_id = c.customer_id
        if customer_id not in cus_list:
            cus_list.append(customer_id)
            res_list.append(c)
    # if request.method == "POST":
    # id = request.POST.get('id', '')
    #     c = BulkCustomer.objects.get(id=id)
    #     c.status = 'dealed'
    #     c.save()
    #     messages.add_message(request, messages.SUCCESS, u'删除成功')
    #     return HttpResponseRedirect(reverse('bulk_customer'))

    return render_to_response("mail/bulk_customer.html", {
        'cus': res_list
    }, context_instance=RequestContext(request))


@login_required
def bulk_customer_modify(request, id):
    obj = BulkCustomer.objects.get(id=id)
    form = BulkCustomerForm(instance=obj)
    if request.method == "POST":
        form = BulkCustomerForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            obj.status = 'dealed'
            obj.save()
            messages.add_message(request, messages.SUCCESS, u'已处理')
            return HttpResponseRedirect(reverse('bulk_customer'))
    return render_to_response("mail/bulk_customer_modify.html", {
        'form': form,
        'obj': obj,
    }, context_instance=RequestContext(request))


@login_required
def ajax_get_bulk_sender(request):
    id = request.GET.get('id', '').split('_')[0]
    obj = BulkCustomer.objects.get(id=id)
    sender_info = obj.sender
    msg = ''
    for l in json.loads(sender_info):
        msg += u'<a href="/mail/mail_list?date={}&customer_id={}&mail_from={}&review=reject">{}</a>: {}</br>'.format(
            obj.date.strftime('%Y-%m-%d'), obj.customer.id, l['mail_from'], l['mail_from'], l['count'])
    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")


@login_required
def get_bulk_sender(request):
    id = request.GET.get('id', '').split('_')[0]
    obj = BulkCustomer.objects.get(id=id)
    sender_info = json.loads(obj.sender)
    return render_to_response("mail/bulk_sender.html", {
        'sender_info': sender_info,
        'obj': obj,
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

    return render_to_response("mail/check_statistics.html", {
        'res': res
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

    return render_to_response("mail/review_statistics.html", {
        'res': res
    }, context_instance=RequestContext(request))


@login_required
def notice_settings(request):
    settings = NoticeSettings.objects.all()
    if settings:
        form = NoticeSettingsForm(instance=settings[0])
    else:
        form = NoticeSettingsForm()
    if request.method == "POST":
        if settings:
            form = NoticeSettingsForm(request.POST, instance=settings[0])
        else:
            form = NoticeSettingsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('notice_settings'))
    return render_to_response("mail/notice_settings.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def mail_reject(request):
    form = MailBaseSearchForm(request.GET)
    data = request.GET
    export = data.get('export', '')
    type = data.get('type', 'relay')
    field = data.get('field', '')

    if export == '1':
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={}_{}.txt'.format(type, field)
        if type == 'relay':
            mails = get_all_data(data)
        else:
            mails = get_all_data2(data)

        if field:
            list = []
            for m in mails:
                if field == 'sender_name' and m.sender_name:
                    list.append(m.sender_name)
                elif field == 'subject' and m.subject:
                    list.append(m.subject)
                elif field == 'attach_name' and m.attach_name:
                    attach_list = m.attach_name.split('----') if m.attach_name else []
                    for a in attach_list:
                        list.append(a)
            response.write('\n'.join(list))
        else:
            list = [[u'主题', u'发件姓名',  u'附件名称']]
            for m in mails:
                attach_list = m.attach_name.split('----') if m.attach_name else []
                list.append([
                    m.subject or '',
                    m.sender_name or '',
                    ','.join(attach_list),
                ])
            response.write('\n'.join(['\t'.join(l) for l in list]))
        return response

    return render_to_response("mail/mail_reject.html", {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def ajax_add_tmp_sender_blacklist(request):
    ids = request.GET.get('id', '')
    customer_id = int(request.GET.get('customer_id', ''))
    mail_from = request.GET.get('mail_from', '')
    days = int(request.GET.get('days', ''))
    expire_time = datetime.datetime.now() + datetime.timedelta(days=days)
    SenderBlockedRecord.objects.create(sender=mail_from, customer_id=customer_id, blocked_days=days, opter=request.user)
    _do_review([ids], 'reject', request, flag=True)

    if TempSenderBlacklist.objects.filter(sender=mail_from, expire_time__gt=expire_time):
        msg = u'已存在'
    elif TempSenderBlacklist.objects.filter(sender=mail_from, expire_time__gt=datetime.datetime.now()):
        obj = TempSenderBlacklist.objects.filter(sender=mail_from, expire_time__gt=datetime.datetime.now()).first()
        obj.expire_time = expire_time
        obj.save()
        msg = u'追加封闭{}天'.format(days)
    else:
        TempSenderBlacklist.objects.create(sender=mail_from, customer_id=customer_id, operater=request.user, expire_time=expire_time)
        msg = u'已封{}天'.format(days)
    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")

@login_required
def spam_rpt_settings(request):
    settings = SpamRptSettings.objects.all()
    if settings:
        form = SpamRptSettingsForm(instance=settings[0])
    else:
        form = SpamRptSettingsForm()
    if request.method == "POST":
        if settings:
            form = SpamRptSettingsForm(request.POST, instance=settings[0])
        else:
            form = SpamRptSettingsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('spam_rpt_settings'))
    return render_to_response("mail/spam_rpt_settings.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def sender_credit_settings(request):
    settings = SenderCreditSettings.objects.all()
    if settings:
        form = SenderCreditSettingsForm(instance=settings[0])
    else:
        form = SenderCreditSettingsForm()
    if request.method == "POST":
        if settings:
            form = SenderCreditSettingsForm(request.POST, instance=settings[0])
        else:
            form = SenderCreditSettingsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('sender_credit_settings'))
    return render_to_response("mail/sender_credit_settings.html", {
        'form': form,
    }, context_instance=RequestContext(request))

def _get_sender_credit_data(data, flag=False):
    sender = data.get('sender', False)
    if flag:
        lists = SenderCredit.objects.all()
        if sender:
            lists = lists.filter(sender__icontains=sender)
    else:
        lists = SenderCreditLog.objects.all()
        if sender:
            lists = lists.filter(sender__icontains=sender)
    return lists

@login_required
def sender_credit(request):
    data = request.GET
    form = SenderCreditBaseSearchForm(data)
    lists = _get_sender_credit_data(data, flag=True)
    try:
        count = lists.count()
    except:
        count = len(lists)

    return render_to_response('mail/sender_credit.html',{
        'form': form,
        'count': count,
    }, context_instance=RequestContext(request))

@login_required
def ajax_get_sender_credit(request):
    data = request.GET
    lists = _get_sender_credit_data(data, flag=True)
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    if search:
        lists = lists.filter( Q(sender__icontains=search) )

    colums = ['id', 'sender', 'credit', 'update_time', 'id']

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
        t = TemplateResponse(request, 'mail/ajax_get_sender_credit.html', {'d': m})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

@login_required
def sender_credit_modify(request, sender_credit_id):
    obj = SenderCredit.objects.get(id=sender_credit_id)
    form = SenderCreditForm(instance=obj)
    if request.method == 'POST':
        form = SenderCreditForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息修改成功')
            return HttpResponseRedirect(reverse('sender_credit'))
    return render_to_response("mail/sender_credit_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def ajax_update_sender_credit(request):
    mail_from = request.GET.get('mail_from', '').lower()
    refreash_credit = int(request.GET.get('credit', 0))
    obj, bool = SenderCredit.objects.get_or_create(sender=mail_from)
    if bool:
        credit = 1000 + refreash_credit
    else:
        credit = obj.credit + refreash_credit
    obj.credit = credit
    obj.save()
    return HttpResponse(json.dumps({'msg': credit}), content_type="application/json")

@login_required
def sender_credit_log(request):
    data = request.GET
    form = SenderCreditBaseSearchForm(data)
    sender = data.get('sender', False)
    lists = SenderCreditLog.objects.filter(sender__icontains=sender)
    #lists = _get_sender_credit_data(data, flag=False)
    try:
        count = lists.count()
    except:
        count = len(lists)

    return render_to_response('mail/sender_credit_log.html',{
        'form': form,
        'count': count,
    }, context_instance=RequestContext(request))

@login_required
def ajax_get_sender_credit_log(request):
    data = request.GET
    lists = _get_sender_credit_data(data, flag=False)
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    search = data.get('search[value]', '')
    if search:
        lists = lists.filter( Q(sender__icontains=search) )

    colums = ['id', 'sender', 'mail_id', 'expect_value', 'value', 'reason', 'create_time', 'id']

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
        t = TemplateResponse(request, 'mail/ajax_get_sender_credit_log.html', {'d': m})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

@login_required
def add_relay_sender_whitelist(request):
    sender = request.GET.get('sender', '')
    msg = u'已添加发件人白名单'
    user = request.user
    if sender:
        sender = sender.lower()
        obj, bool = RelaySenderWhitelist.objects.get_or_create(sender=sender)
        if user:
            if bool:
                obj.creater = user
            else:
                obj.operater = user
            obj.disabled = False
            obj.save()
        return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")

@login_required
def credit_interval_settings(request):
    credit_obj = CreditIntervalSettings.objects.all()
    form = CreditIntervalSettingsForm()
    if request.method == "POST":
        form = CreditIntervalSettingsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, u'信息添加成功')
            return HttpResponseRedirect(reverse('credit_interval_settings'))
    return render_to_response("mail/credit_interval_settings.html", {
        'form': form,
        'credit_obj': credit_obj,
    }, context_instance=RequestContext(request))

@login_required
def credit_interval_settings_change_status(request):
    if request.method == "POST":
        status = request.POST.get('status', '')
        id = request.POST.get('id', '')
        obj = CreditIntervalSettings.objects.get(id=id)
        if status == 'delete':
            obj.delete()
            msg = u'删除成功'
        messages.add_message(request, messages.SUCCESS, msg)
        return HttpResponseRedirect(reverse('credit_interval_settings'))
    return HttpResponse('no message')

@login_required
def operation_doc(request):
    return render_to_response("mail/operation_doc.html", {}, context_instance=RequestContext(request))

@login_required
def edm_check_settings_list(request):
    edm_check_settingss = EdmCheckSettings.objects.all()
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        status = int(request.POST.get('status', ''))
        if int(status) == -1:
            objs = EdmCheckSettings.objects.filter(id__in=ids)
            objs.delete()
            msg = u'成功删除%s个' % len(ids)
        else:
            EdmCheckSettings.objects.filter(id__in=ids).update(disabled=status)
            tip = u'禁用' if status else u'启用'
            msg = u'成功%s%s个' % (tip, len(ids))
        messages.add_message(request, messages.SUCCESS, msg)
    return render_to_response("mail/edm_check_settings_list.html", {
        'edm_check_settingss': edm_check_settingss,
    }, context_instance=RequestContext(request))


@login_required
def edm_check_settings_add(request):
    form = EdmCheckSettingsForm()
    if request.method == "POST":
        form = EdmCheckSettingsForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.add_message(request, messages.SUCCESS, u'设置添加成功')
            return HttpResponseRedirect(reverse('edm_check_settings_list'))
    return render_to_response("mail/edm_check_settings_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def edm_check_settings_modify(request, id):
    edm_check_settings_obj = EdmCheckSettings.objects.get(id=id)
    form = EdmCheckSettingsForm(instance=edm_check_settings_obj)
    if request.method == "POST":
        form = EdmCheckSettingsForm(request.POST, instance=edm_check_settings_obj)
        if form.is_valid():
            obj = form.save()
            messages.add_message(request, messages.SUCCESS, u'设置修改成功')
            return HttpResponseRedirect(reverse('edm_check_settings_list'))
    return render_to_response("mail/edm_check_settings_modify.html", {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def sender_warning(request):
    mail_from = request.GET.get('sender', '')
    bounce_setting = BounceSettings.objects.first()
    notice_setting = NoticeSettings.objects.first()
    s = MailSender()
    subject = u'群发垃圾病毒邮件提醒'
    content = notice_setting.sender_warning_content.format(**{
        'mail_from': mail_from
    })
    code, return_msg = s.send_email(bounce_setting.server, bounce_setting.port, bounce_setting.mailbox,
                             bounce_setting.password,
                             mail_from, subject, content)
    if code == 250:
        is_email = True
        msg = u'发送成功'
    else:
        is_email = False
        msg = u'发送失败({})'.format(return_msg)
    Notification.objects.create(subject=subject, content=u'({}){}'.format(msg, content), type='s_warning', is_email=is_email)

    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")


def _get_active_sender_list(data, date):
    mail_model = get_mail_model(date)
    customer_id = data.get('customer_id', '')

    if customer_id:
        mails = mail_model.objects.filter(customer_id=customer_id)
    else:
        mails = mail_model.objects.all()
    mails = mails.values("mail_from").annotate(total_all=Count("id"), size=Sum("size"),
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


def get_active_sender_list(data):
    date = data.get('date', '')
    if not date:
        date = datetime.date.today().strftime('%Y%m%d')
    else:
        date = date.replace('-', '')
    return _get_active_sender_list(data, date)


@login_required
def active_sender_list(request):
    data = request.GET
    form = ActiveSenderForm(data)
    mails = get_active_sender_list(data)
    customer = None
    customer_id = request.GET.get('customer_id', '')
    if customer_id:
        customer = Customer.objects.get(id=customer_id)
    return render_to_response("mail/active_sender_list.html", {
        'mails': mails,
        'form': form,
        'customer': customer
    }, context_instance=RequestContext(request))
