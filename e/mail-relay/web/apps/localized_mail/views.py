# coding=utf-8
import time
import datetime
import re
import json

from django.contrib.auth.decorators import login_required

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q, query
from django.db.models import Count
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from lib.django_redis import get_redis as get_redis_connection

from apps.localized_mail.models import LocalizedMail
from apps.localized_mail.forms import MailSearchForm
from lib.parse_email import ParseEmail
from lib.common import high_light


@login_required
def mail_summary(request):
    # for m in get_mail_model('20170531').objects.filter(customer_id=2291):
    #     LocalizedMail.objects.create(customer_id=2291, mail_from=m.mail_from,
    #                                  mail_to=m.mail_to, state=m.state,
    #                                  created=m.created, subject=m.subject,
    #                                  check_result=m.check_result, check_message=m.check_message,
    #                                  mail_id=m.date_id()
    #     )
    if request.method == "POST":
        action = request.POST.get("action", '')
        if action == "refresh":
            redis = get_redis_connection()
            map(lambda k: redis.delete(k),
                filter(lambda k: k.startswith(':1:_cache:localized_mail_status'), redis.keys()))
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
        res[date.strftime('%Y-%m-%d')] = get_state_data(date)

        date = date + datetime.timedelta(days=1)
        index += 1

    return render_to_response("localized_mail/mail_summary.html", {
        'res': res
    }, context_instance=RequestContext(request))


def get_state_data(date):
    key = '_cache:localized_mail_status:{}'.format(date.strftime('%Y-%m-%d'))
    if datetime.date.today() != date.date():
        rs = cache.get(key)
        if rs:
            return rs
    rs = {}
    mails = LocalizedMail.objects.filter(created_date=date.date())
    try:
        rs['count'] = mails.count()
    except:
        return rs
    rs['state'] = dict(mails.values_list("state").annotate(Count("id")))
    rs['check'] = dict(mails.values_list("check_result").annotate(Count("id")))
    cache.set(key, rs, 0)
    return rs

def get_search_data(data):
    date = data.get('date', '')
    customers = data.get('customers', '')
    mail_from = data.get('mail_from', '')
    mail_to = data.get('mail_to', '')
    subject = data.get('subject', '')
    state = data.get('state', '')
    check = data.get('check', '')
    origin = data.get('origin', '')
    check_message = data.get('check_message', '')
    customer = data.get('customer', '')
    search = data.get('search[value]', '')
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')
    show = data.get('show', '')
    reviewer_id = data.get('reviewer_id', '')
    reviewer = data.get('reviewer', '')
    try:
        check_list = filter(lambda a: bool(a), data.getlist('check', ''))
    except BaseException, e:
        check_list = []

    mails = LocalizedMail.objects.all()
    if date:
        date = datetime.datetime.strptime(date.replace('-', ''), '%Y%m%d')
        mails = mails.filter(created_date=date)

    if customers:
        mails = mails.filter(Q(customer__company__icontains=customers) | Q(customer__username__icontains=customers))
    if mail_from:
        mails = mails.filter(mail_from__icontains=mail_from)
    if mail_to:
        mails = mails.filter(mail_to__icontains=mail_to)
    if customer:
        mails = mails.filter(customer_id=customer)
    if origin:
        mails = mails.filter(origin=origin)

    if check_list:
        mails = mails.filter(check_result__in=check_list)
    elif check:
        if check == 'subject_and_keyword':
            mails = mails.filter(check_result__in=['keyword_blacklist', 'subject_blacklist', 'sender_blacklist'])
        else:
            mails = mails.filter(check_result=check)
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

    if subject:
        mails = mails.filter(subject__icontains=subject)

    if reviewer_id:
        mails = mails.filter(reviewer_id=reviewer_id)

    if search:
        mails = mails.filter(
            Q(mail_from__icontains=search) | Q(mail_to__icontains=search) | Q(subject__icontains=search))

    if reviewer:
        mails = mails.filter(reviewer__username=reviewer)

    try:
        mails.exists()
    except:
        mails = []

    if show == 'review':
        colums = ['id', 'customer', 'mail_from', 'subject', 'size', 'created', 'check_message', 'check_result']
    else:
        colums = ['id', 'customer', 'mail_from', 'subject', 'size', 'created', 'state', 'check_result', 'reviewer', 'review_time']

    if isinstance(mails, query.QuerySet) and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            mails = mails.order_by('-%s' % colums[int(order_column)])
        else:
            mails = mails.order_by('%s' % colums[int(order_column)])
    return mails

@login_required
def mail_list(request):

    data = request.GET
    form = MailSearchForm(data)
    review_status = {}
    study_status = {}
    id = request.GET.get('id', '')
    result = request.GET.get('result', '')

    # 单个ajax审核
    if id and result:
        msg, count = _do_review([id], result, request)
        return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")
    # 批量审核
    if request.method == "POST":
        ids = (request.POST.get('ids', '')).split(',')
        result = request.POST.get('result', '')
        if result == 'empty':
            data = {'all_day': 1, 'check': 'spam', 'state': 'review', 'mail_id': '0'}
            mails = get_search_data(data)
            ids = [m.id for m in mails]
            msg, count = _do_review(ids, 'reject', request)
        elif result == 'white_sender_pass':
            msg, count = _do_review(ids, 'pass', request)
        else:
            msg, count = _do_review(ids, result, request)
        messages.add_message(request, messages.SUCCESS, u'成功{}{}个邮件'.format(msg, count))

    return render_to_response("localized_mail/mail_list.html", {
        'form': form,
        'show': data.get('show', ''),
        'review_status': review_status,
        'study_status': study_status,
    }, context_instance=RequestContext(request))

@login_required
def ajax_get_mails(request):
    data = request.GET

    mails = get_search_data(data)

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
        t = TemplateResponse(request, 'localized_mail/ajax_get_mails.html', {'m': m})
        t.render()
        rs["aaData"].append(re.findall(re_str, t.content, re.DOTALL))
    return HttpResponse(json.dumps(rs, ensure_ascii=False), content_type="application/json")

@login_required
def mail_read(request):
    id = request.GET.get('id', '')
    cid = request.GET.get('cid', '')
    aid = request.GET.get('aid', '')
    download = request.GET.get('download', '')
    view_body = request.GET.get('view_body', '')
    view_source = request.GET.get('view_source', '')
    export = request.GET.get('export', '')

    if id:
        mail_obj = LocalizedMail.objects.get(id=id)
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
            link = '{}?id={}&cid=\g<cid>'.format(reverse('localized_mail_read'), id)
            text = re.sub('"cid:(?P<cid>.*?)"', link, text)

            if mail_obj.check_result in ['keyword_blacklist', 'custom_blacklist'] and text and charset:
                s = mail_obj.check_message.split('----', 1)[-1]
                re_s = u'<span style="background-color: yellow"><b style="color:#A94442;">{}</b></span>'.format(
                    s).encode(charset)
                s = s.encode(charset)
                text = text.replace(s, re_s)
            return HttpResponse(text, charset=charset)
        if view_source:
            return render_to_response("localized_mail/txt.html", {
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

        return render_to_response("localized_mail/mail_read.html", {
            'm': m,
            'id': id,
            'mail_obj': mail_obj,
            'subject': subject,
            'hl_mail_from': hl_mail_from,
        }, context_instance=RequestContext(request))
    return HttpResponse(u'no email')


def _do_review(ids, result, request):
    """
    :param ids: 审核的ID列表
    :param result: 审核结果
    :param flag: 是否正常流程操作， 默认：True, 如果是误判操作，则为False
    :return:
    """
    keys = {}
    redis = get_redis_connection()
    reviewer = request.user
    review_time = datetime.datetime.now()
    msg = u'通过' if result == 'pass' else u'拒绝'
    mails = LocalizedMail.objects.filter(id__in=ids, state='review')
    count = mails.count()
    if result == 'pass':
        mails.update(state='passing', reviewer=reviewer, review_time=review_time)
    elif result == 'reject':
        mails.update(state='rejecting', reviewer=reviewer, review_time=review_time)
    map(lambda key: redis.lpush('control_review_result', key), ids)
    return msg, count

