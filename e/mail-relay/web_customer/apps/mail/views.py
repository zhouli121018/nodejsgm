# coding=utf-8
import json

import base64
import datetime
import time
import re

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib import messages
from django.db.models import Q, query
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.db.models import Count, Sum, Case, When, Value, IntegerField
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from redis_cache import get_redis_connection as get_redis_connection2

from forms import MailSearchForm, ActiveSenderForm, MailSummaryForm
from lib.common import get_date
from lib.statistic import get_real_statistic, get_summary_statistic
from lib.parse_email import ParseEmail
from models import get_mail_model, DeliverLog, STATE_RELATE, Statistics, InvalidMail
from apps.core.models import CustomerSetting
from apps.core.forms import CustomerRelaySettingForm
from templatetags.mail_tags import get_rate


@login_required
def mail_list(request):
    data = request.GET
    export = data.get('export', '')
    form = MailSearchForm(data)


    if export == '1':
        from excel_response import ExcelResponse

        list = [[_(u'发件人'), _(u'收件人'), _(u'大小'), _(u'客户端IP'), _(u'入站时间'), _(u'出站时间'), _(u'主题'), _(u'状态')]]
        name = 'relay_{}'.format(data.get('date', datetime.date.today().strftime('%Y%m%d')).replace('-', ''))
        mails = get_all_data(data, request.user)
        for m in mails:
            created = m.created.strftime("%Y-%m-%d %H:%M:%S") if m.created else ''
            deliver_time = m.deliver_time.strftime("%Y-%m-%d %H:%M:%S") if m.deliver_time else ''
            list.append([m.mail_from, m.mail_to, m.size, m.client_ip, created, deliver_time, m.subject,
                         m.get_state_display()])
        return ExcelResponse(list, name, encoding='gbk')

    return render_to_response("mail/mail_list.html", {
        'form': form,
        'date': get_date(form.data),
    }, context_instance=RequestContext(request))


@login_required
def ajax_get_mails(request):
    data = request.GET

    mails = get_all_data(data, user=request.user)

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


def get_all_data(data, user):
    all_day = data.get('all_day', '')
    date_start = data.get('date_start', '')
    date_end = data.get('date_end', '')
    date = data.get('date', '').replace('-', '')
    if all_day:
        date_end = datetime.datetime.today()
        date_start = date_end - datetime.timedelta(days=20)
        date = date_start
        mails = []
        while date <= date_end:
            date = date + datetime.timedelta(days=1)
            mails.extend(get_search_data(data, date.strftime('%Y-%m-%d'), user))
    elif date_start and date_end:
        date_start = datetime.datetime.strptime(date_start.replace('-', ''), '%Y%m%d')
        date_end = datetime.datetime.strptime(date_end.replace('-', ''), '%Y%m%d')
        mails = []
        while date_start <= date_end:
            try:
                mails.extend(get_search_data(data, date_start.strftime('%Y-%m-%d'), user=user))
            except:
                pass
            date_start = date_start + datetime.timedelta(days=1)
    else:
        mails = get_search_data(data, date, user=user)
    return mails


def get_search_data(data, date='', user=''):
    if not date:
        date = data.get('date', '')
    mail_from = data.get('mail_from', '')
    mail_to = data.get('mail_to', '')
    state = data.get('state', '')
    send = data.get('send', '')
    bounce = data.get('bounce', '')
    mail_id = data.get('mail_id', '')
    error_type = data.get('error_type', '')
    ip = data.get('ip', '')
    subject = data.get('subject', '')
    search = data.get('search[value]', '')
    order_column = data.get('order[0][column]', '')
    order_dir = data.get('order[0][dir]', '')

    if not date:
        date = time.strftime('%Y-%m-%d')

    return_code = data.get('return_code', '')

    if not date:
        date = time.strftime('%Y%m%d')
    else:
        date = date.replace('-', '')
    mail_model = get_mail_model(date)

    if user:
        mails = mail_model.objects.filter(customer=user)
    else:
        mails = mail_model.objects.all()
    if mail_from:
        mails = mails.filter(mail_from__icontains=mail_from)
    if mail_to:
        mails = mails.filter(mail_to__icontains=mail_to)
    if error_type:
        mails = mails.filter(error_type=error_type)
    if ip:
        mails = mails.filter(client_ip=ip)

    if state:
        if state == 'analysis':
            mails = mails.filter(state__in=['check', 'review', 'dispatch'])
        elif state == 'out_all':
            mails = mails.filter(state__in=['finished', 'fail_finished', 'bounce'])
        elif state == 'fail_finished':
            mails = mails.filter(state__in=['fail_finished', 'bounce'])
        elif state == 'rejects':
            mails = mails.filter(state__in=['reject', 'c_reject'])
        else:
            mails = mails.filter(state=state)

    if send == 'success':
        return_code = '250'
    elif send == 'fail':
        return_code = '0'

    if bounce:
        mails = mails.filter(bounce_result=bounce)

    if mail_id:
        if mail_id == '0':
            mails = mails.filter(mail_id=0)
        else:
            mails = mails.filter(Q(mail_id=mail_id) | Q(id=mail_id))

    if subject:
        mails = mails.filter(subject__icontains=subject)

    if search:
        mails = mails.filter(
            Q(mail_from__icontains=search) | Q(mail_to__icontains=search) | Q(subject__icontains=search))

    if return_code:
        if return_code == '0':
            mails = mails.exclude(return_code=250)
        else:
            mails = mails.filter(return_code=return_code)
    try:
        mails.exists()
    except:
        mails = []

    colums = ['mail_from', 'size', 'mail_to', 'id', 'client_ip', 'created', 'subject', 'state']

    if isinstance(mails, query.QuerySet) and order_column and int(order_column) < len(colums):
        if order_dir == 'desc':
            mails = mails.order_by('-%s' % colums[int(order_column)])
        else:
            mails = mails.order_by('%s' % colums[int(order_column)])

    return mails


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
    can_view_mail = request.user.customer_setting.can_view_mail

    if id and date:
        mail_obj = get_mail_model(date).objects.get(id=id)
        content = mail_obj.get_mail_content()
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
            if not can_view_mail:
                return HttpResponse()
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
            if not can_view_mail:
                return HttpResponse()
            return render_to_response("mail/txt.html", {
                'content': content.decode('gbk', 'ignore'),
            }, context_instance=RequestContext(request))

        if export:
            if not can_view_mail:
                return HttpResponse()
            response = HttpResponse(content, content_type='text/html')
            response['Content-Disposition'] = 'attachment; filename="eml.eml"'
            return response

        subject = mail_obj.subject

        return render_to_response("mail/mail_read.html", {
            'm': m,
            'id': id,
            'date': date,
            'mail_obj': mail_obj,
            'subject': subject,
        }, context_instance=RequestContext(request))
    return HttpResponse(u'no email')


@login_required
def mail_review(request):
    id = request.GET.get('id', '')
    result = request.GET.get('result', '')

    # date = get_date(request.GET)

    # 单个ajax审核
    key = 'customer_pass_undo'
    if id and result:
        date, id = id.split('_', 1)
        m = get_mail_model(date).objects.get(customer=request.user, id=id)
        m.review_result = result
        redis = get_redis_connection2(m.server_id)
        if result in ['c_pass', 'c_pass_undo']:
            if result == 'c_pass_undo':
                if not redis.exists(key):
                    redis.expire(key, 24*60*60)
                try:
                    undo_count = int(redis.hget(key, request.user.id))
                except:
                    undo_count = 0
                redis.hincrby(key, request.user.id, 1)
                if undo_count >= 100:
                    msg = _(u'操作失败') % {}
                    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")
            m.state = 'dispatch'
            msg = _(u'已放行') % {}
        else:
            m.state = 'c_reject'
            msg = _(u'已拒绝') % {}
        m.save()
        if result in ['c_pass', 'c_pass_undo']:
            redis.lpush('relay_dispatch', m.get_mail_filename())
        return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")


@login_required
def deliver_logs(request, id):
    date, mail_id = id.split('_')
    logs = DeliverLog.objects.filter(date=date, mail_id=mail_id)
    m = get_mail_model(date).objects.get(id=mail_id)
    return render_to_response("mail/deliver_logs.html", {
        'logs': logs,
        'm': m,
    }, context_instance=RequestContext(request))


def _get_active_sender_list(data, date, user=''):
    mail_model = get_mail_model(date)

    if user:
        mails = mail_model.objects.filter(customer=user)
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


def get_active_sender_list(data, user):
    date = data.get('date', '')
    if not date:
        date = datetime.date.today().strftime('%Y%m%d')
    else:
        date = date.replace('-', '')
    return _get_active_sender_list(data, date, user)


@login_required
def active_sender_list(request):
    data = request.GET
    form = ActiveSenderForm(data)

    mails = get_active_sender_list(data, request.user)
    return render_to_response("mail/active_sender_list.html", {
        'mails': mails,
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def mail_summary(request):
    form = MailSummaryForm(request.GET)
    export = request.GET.get('export', '')
    stype = request.GET.get('stype', 'day')
    try:
        date_start = datetime.datetime.strptime(request.GET.get('date_start'), '%Y-%m-%d')
    except:
        date_start = ''
    try:
        date_end = datetime.datetime.strptime(request.GET.get('date_end'), '%Y-%m-%d')
    except:
        date_end = ''

    today = datetime.datetime.today()
    if not date_end:
        date_end = today
    if not date_start:
        if stype == 'week':
            date_start = date_end - datetime.timedelta(days=180)
        elif stype == 'month':
            t = date_end - datetime.timedelta(days=180)
            date_start = datetime.datetime(t.year, t.month, 1)
        else:
            date_start = date_end - datetime.timedelta(days=30)
    res = get_summary_statistic(request.user.id, 'relay', stype, date_start, date_end)

    if export == '1':
        from excel_response import ExcelResponse

        list = [[_(u'日期'), _(u'邮件封数'), _(u'入站数量'), _(u'入站流量'), _(u'垃圾数量'), _(u'垃圾流量'),
                 _(u'出站数量'), _(u'出站流量'), _(u'成功数量'), _(u'成功流量'), _(u'失败数量'),
                 _(u'失败流量'), _(u'垃圾率'), _(u'出站成功率')]]

        for r in res:
            list.append([r['key'], r['total_all'],
                         r['all'][0], filesizeformat(r['all'][1]),
                         r['reject'][0], filesizeformat(r['reject'][1]),
                         r['out_all'][0], filesizeformat(r['out_all'][1]),
                         r['finished'][0], filesizeformat(r['finished'][1]),
                         r['fail_finished'][0], filesizeformat(r['fail_finished'][1]),
                         get_rate(r['reject'][0], r['all'][0]),
                         get_rate(r['finished'][0], r['out_all'][0]),
            ])
        return ExcelResponse(list, 'relay_summary', encoding='gbk')

    return render_to_response("mail/mail_summary.html", {
        'res': res,
        'stype': stype,
        'date_start': date_start,
        'date_end': date_end,
        'form': form
    }, context_instance=RequestContext(request))


@login_required
def customer_report(request):
    id = request.GET.get('id', '')
    if id:
        date, id = id.split('_', 1)
        m = get_mail_model(date).objects.get(customer=request.user, id=id)
        if m.customer_report == 0:
            m.customer_report = 1
            m.save()
        return HttpResponse(json.dumps({'msg': _(u'已举报垃圾邮件') % {}}), content_type="application/json")


@login_required
def setting(request):
    setting, _ = CustomerSetting.objects.get_or_create(customer=request.user)
    form = CustomerRelaySettingForm(instance=setting)
    if request.method == "POST":
        form = CustomerRelaySettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, _(u'信息修改成功'))
            return HttpResponseRedirect(reverse('mail_setting'))
    return render_to_response("mail/mail_setting.html", {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def statistics(request):
    form = MailSummaryForm(request.GET)
    start = request.GET.get('date_start', '')
    end = request.GET.get('date_end', '')
    date_end = datetime.datetime.today()
    date_start = date_end - datetime.timedelta(days=14)
    if start or end:
        if start:
            date_start = datetime.datetime.strptime(start, '%Y-%m-%d')
        if end:
            date_end = datetime.datetime.strptime(end, '%Y-%m-%d')
        if end and not start:
            date_end = date_end - datetime.timedelta(days=30)
    statistics = Statistics.objects.filter(date__gte=date_start, date__lte=date_end, customer=request.user)

    return render_to_response("mail/statistics.html", {
        'statistics': statistics,
        'date_start': date_start,
        'date_end': date_end,
        'form': form
    }, context_instance=RequestContext(request))


def dowload_mail_attachment(request):
    date_id = request.GET.get('id', '')
    date_id_decoded = base64.b64decode(date_id)
    date, id = date_id_decoded.split('_')

    private_key = request.GET.get('key', '')
    decoded = base64.b64decode(private_key)
    private, date2, id2 = decoded.split('_')

    aid_base64 = request.GET.get('aid', '')
    aid = base64.b64decode(aid_base64)

    download = request.GET.get('download', '')
    response = HttpResponseNotFound('<h1>No email</h1>')

    cid = request.GET.get('cid', '')

    if id and date:
        if private == 'MAILDOWNLOAD' and id == id2 and date == date2:
            try:
                mail_obj = get_mail_model(date).objects.get(id=id)
                content = mail_obj.get_mail_content()
                parse_obj = ParseEmail(content)
                m = parse_obj.parseMailTemplate()
                attachments = m['attachments']
                if aid or cid:
                    if aid:
                        attach = attachments[int(aid)]
                        response = HttpResponse(
                            attach.get('data', ''),
                            content_type=attach.get('content_type', '').split(';')[0]
                        )
                    else:
                        for one in attachments:
                            if one.get('content_id') == cid:
                                attach = one
                                response = HttpResponse(attach.get('data', ''),
                                                        content_type=attach.get('content_type', '').split(';')[0])
                                break
                    if download:
                        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
                            attach.get('decode_name', '').encode('utf-8'))
            except Exception as e:
                response = HttpResponseNotFound('<h1>网络附件已过期</h1>')
    return response


def dowload_mail_real_attachment(request):
    date_id = request.GET.get('id', '')
    date_id_decoded = base64.b64decode(date_id)
    date, id = date_id_decoded.split('_')

    private_key = request.GET.get('key', '')
    decoded = base64.b64decode(private_key)
    private, date2, id2 = decoded.split('_')

    aid_base64 = request.GET.get('aid', '')
    aid = base64.b64decode(aid_base64)

    download = request.GET.get('download', '')
    response = HttpResponseNotFound('<h1>No email</h1>')

    cid = request.GET.get('cid', '')

    if id and date:
        if private == 'MAILDOWNLOAD' and id == id2 and date == date2:
            try:
                mail_obj = get_mail_model(date).objects.get(id=id)
                content = mail_obj.get_mail_content()
                parse_obj = ParseEmail(content)
                m = parse_obj.parseMailTemplate()
                attachments = m['attachments']
                real_attachments = m['real_attachments']
                if aid or cid:
                    if aid:
                        attach = real_attachments[int(aid)]
                        response = HttpResponse(
                            attach.get('data', ''),
                            content_type=attach.get('content_type', '').split(';')[0]
                        )
                    if cid:
                        for one in attachments:
                            if one.get('content_id') == cid:
                                attach = one
                                response = HttpResponse(attach.get('data', ''),
                                                        content_type=attach.get('content_type', '').split(';')[0])
                                break
                    if download:
                        # temp = tempfile.TemporaryFile()
                        #temp.write(attach.get('data', ''))
                        #temp.close()
                        #wrapper = FileWrapper(temp)
                        #response = HttpResponse(wrapper, content_type='application/octet-stream')
                        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
                            attach.get('decode_name', '').encode('utf-8'))
            except Exception as e:
                response = HttpResponseNotFound('<h1>网络附件已过期</h1>')
    return response


@login_required
def invalid_address(request):
    addresses = request.GET.get('addresses', '')
    address = addresses.split(',')
    address = [addr.strip() for addr in address if addr]
    addresses = addresses.replace(',', '\r\n')
    if len(address) >= 5:
        messages.add_message(request, messages.ERROR, _(u'查询个数超过5个'))
        lists = []
    else:
        lists = InvalidMail.objects.filter(mail__in=address)

    return render_to_response('mail/invalid_address.html', {
        'addresses': addresses,
        'lists': lists,
        'total': InvalidMail.objects.count()
    }, context_instance=RequestContext(request))


@login_required
def ajax_delete_invalid_address(request):
    addr = request.POST.get('addr', '').strip()
    InvalidMail.objects.filter(mail=addr).delete()
    return HttpResponse(json.dumps({'msg': 'Y', }), content_type="application/json")

@login_required
def resent(request):
    ids = request.GET.get('id', '')
    date, id = ids.split('_')
    msg =  _(u'发送失败，只有发送完成/失败的邮件可以再次发送') % {}
    m = get_mail_model(date).objects.get(id=id)
    if m.state in ['finished', 'fail_finished']:
        try:
            redis = get_redis_connection2(m.server_id)
        except:
            redis = get_redis_connection2('default')
        redis.lpush('relay_dispatch', m.get_mail_filename())
        m.dispatch_data = None
        m.save()
        msg =  _(u'已再次发送邮件') % {}
    return HttpResponse(json.dumps({'msg': msg}), content_type="application/json")
