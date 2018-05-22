# coding=utf-8
import datetime
import json
import re
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect
from lib.statistic import get_real_statistic, get_statistic
from apps.mail.models import get_mail_model, STATE_RELATE
from apps.collect_mail.models import get_mail_model as get_mail_model2
from apps.core.forms import CustomerSettingForm
from apps.core.models import CustomerSetting, UrlRemark
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
# from django.conf.urls import i18n
# from django.utils.http import is_safe_url, urlunquote
from django.utils.translation import (
    LANGUAGE_SESSION_KEY, check_for_language, get_language, to_locale,
)



def set_language_session(sender, user, **kwargs):
    """
    A signal receiver which updates the last_login date for
    the user logging in.
    """
    kwargs['request'].session['_language'] = user.lang_code


user_logged_in.connect(set_language_session)


@login_required
def set_lang(request):
    next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = HttpResponseRedirect(next)
    lang_code = request.POST.get('language_code', None)
    if not lang_code:
        lang_code = request.LANGUAGE_CODE
    if not lang_code or lang_code not in ('en', 'zh-cn'):
        lang_code = settings.LANGUAGE_CODE
    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session[LANGUAGE_SESSION_KEY] = lang_code
        request.user.lang_code = lang_code
        request.user.save()
    return response


@login_required
def home(request, template_name='home.html'):
    # return HttpResponseRedirect(reverse('mail_summary'))
    # return HttpResponse('home')
    date = request.GET.get('date', '')
    relay_statistic = get_real_statistic(request.user.id, date, 'relay')
    collect_statistic = get_real_statistic(request.user.id, date, 'collect')

    s, _ = CustomerSetting.objects.get_or_create(customer=request.user)
    setting_form = CustomerSettingForm(instance=s)
    user_type = request.user.type
    status = request.user.status
    gateway_status = request.user.gateway_status
    warning_msg = ''
    if user_type in ['relay', 'all'] and status in ['expiring', 'expired']:
        if status == 'expiring':
            warning_msg += u'中继账户将在 <strong class="warning"> <small>{}</small> </strong> 到期，届时相关服务将停止，请及时处理。'.format(
                request.user.service_end)
        else:
            warning_msg += u'中继账户已过期，相关服务已停止，请联系客服。'

    if user_type in ['collect', 'all'] and gateway_status in ['expiring', 'expired']:
        if status == 'expiring':
            warning_msg += u'网关账户将在 <strong class="warning"> <small>{}</small> </strong> 到期，届时相关服务将停止，请及时处理。'.format(
                request.user.gateway_service_end)
        else:
            warning_msg += u'网关账户已过期，相关服务已停止，请联系客服。'

    return render_to_response(template_name, {
        'relay_statistic': relay_statistic,
        'collect_statistic': collect_statistic,
        'setting_form': setting_form,
        'warning_msg': warning_msg
    }, context_instance=RequestContext(request))


@login_required
def ajax_get_statistic(request):
    try:
        date = datetime.datetime.strptime(request.GET.get('date', ''), "%Y-%m-%d")
    except:
        date = ''
    date_start = request.GET.get('date_start', '')
    date_end = request.GET.get('date_end', '')

    ctype = request.GET.get('type', '')
    res = get_statistic(customer_id=request.user.id, date=date, ctype=ctype, date_start=date_start, date_end=date_end)
    return HttpResponse(json.dumps(res, ensure_ascii=False), content_type="application/json")


@login_required
def ajax_get_remark_base(request):
    data = request.GET
    base_url = data.get('base_url', '')
    lists = []
    if base_url:
        if re.search(r'(\/\d+?\/)', base_url):
            base_url = re.sub(r'(\/\d+?\/)', '/modify/', base_url)
        base_url = 'web_customer' + base_url.strip('')
        lists = UrlRemark.objects.filter(url=base_url).values('remark')
    res = lists and lists[0] or {'remark': '暂无'}
    return HttpResponse(json.dumps(res, ensure_ascii=False), content_type="application/json")


@login_required
def ajax_save_remark_base(request):
    data = request.POST
    base_url = data.get('base_url', '')
    remark = data.get('remark', '')
    if base_url:
        if re.search(r'(\/\d+?\/)', base_url):
            base_url = re.sub(r'(\/\d+?\/)', '/modify/', base_url)
        base_url = 'web_customer' + base_url.strip('')
        obj, bool = UrlRemark.objects.get_or_create(url=base_url)
        obj.remark = remark
        obj.save()
    return HttpResponse(json.dumps({'msg': u"成功修改备注"}), content_type="application/json")
