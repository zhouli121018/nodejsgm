# -*- coding: utf-8 -*-

import re
import random
from django.conf import settings
from django.shortcuts import reverse
from django_redis import get_redis_connection
from app.core.models import SysPicDomain, CommonType, Prefs
from django.utils.translation import ugettext_lazy as _
from lib.tools import safe_format

## 图片url
def getPicUrl():
    lists = SysPicDomain.objects.filter(isvalid=True)
    domain = None
    if lists:
        obj = random.choice(lists)
        domain = obj.domain
    return domain if domain else random.choice(settings.TEMPLATE_PIC_URLS)

# 获取 地址变量
def getAddrVarFields(cr, customer_id):
    self_var_pattern = re.compile('var\d+')
    sql = "SELECT column_name FROM information_schema.COLUMNS WHERE table_name = 'ml_subscriber_{}' AND table_schema = 'mm-pool';".format(customer_id)
    cr.execute(sql)
    res = cr.fetchall()
    var_lists = sorted(filter(lambda s: self_var_pattern.match(s), [r[0] for r in res]), key=lambda k: int(k[3:]))
    return var_lists

# 获取 动态变量
def getVars(cr, customer_id, lang_code):
    varlists = getAddrVarFields(cr, customer_id)
    subject_vals = [
        ('{FULLNAME}', _(u'收件人姓名')),
        ('{RECIPIENTS}',  _(u'收件人地址')),
        ('{DATE}',  _(u'当前日期')),
        ('{RANDOM_NUMBER}',  _(u'随机10位数字')),
        ('{SEX}', _(u'性别')),
        ('{BIRTHDAY}', _(u'生日')),
        ('{PHONE}', _(u'手机')),
        ('{AREA}', _(u'地区')),
    ]
    if lang_code == 'en-us':
        title = u"Vriable"
        content_vals = [
            [ '{RECIPIENTS}', u"Recipient Aaddress", u"Recipient Aaddress"],
            [ '{FULLNAME}', u"Recipient", u"Recipient"],
            [ '{DATE}', u"Current date", u"Current date"],
            [ '{RANDOM_NUMBER}', u"Random 10 Digits", u"Random 10 Digits"],
            [ '{RANDOM_HTML}', u"Random 200 Chinese characters", u"Random 200 Chinese characters"],
            [ '{SEX}', u"Gender", u"Gender"],
            [ '{BIRTHDAY}', u"Birthday",u"Birthday"],
            [ '{PHONE}', u"Phone", u"Phone"],
            [ '{AREA}', u"Area", u"Area"],
        ]
        for index, var_x in enumerate(varlists, start=1):
            subject_vals.append(('{' + var_x.upper() +'}', u'var{}'.format(index)))
            content_vals.append( ['{' + var_x.upper() +'}', u'var{}'.format(index), u'var{}'.format(index)] )
    else:
        title = u"变量"
        content_vals = [
            [ '{RECIPIENTS}', u"收件人地址", u"收件人地址"],
            [ '{FULLNAME}', u"收件人姓名", u"收件人姓名"],
            [ '{DATE}', u"当前日期", u"当前日期"],
            [ '{RANDOM_NUMBER}', u"随机10位数", u"随机10位数"],
            [ '{RANDOM_HTML}', u"随机200中文字符（自动隐藏,Gmail无效）", u"随机200中文字符（自动隐藏,Gmail无效）"],
            [ '{SEX}', u"性别", u"性别"],
            [ '{BIRTHDAY}', u"生日",u"生日"],
            [ '{PHONE}', u"手机", u"手机"],
            [ '{AREA}', u"地区", u"收件人地址"],
        ]
        for index, var_x in enumerate(varlists, start=1):
            subject_vals.append(('{' + var_x.upper() +'}', u'变量{}'.format(index)))
            content_vals.append( ['{' + var_x.upper() +'}', u'变量{}'.format(index), u'变量{}'.format(index)] )
    return subject_vals, {
        "title": title,
        "data": content_vals,
    }

## 获取公共变量库
def getCommons(lang_code):
    data = []
    lists = CommonType.objects.filter(disabled=True)
    redis = get_redis_connection()
    if lang_code == 'en-us':
        for d in lists:
            count = redis.hget(settings.COMMON_VAR_COUNT_HASH, key=d.var_type)
            count = int(count) if count else 0
            title = u"Public Variable"
            data.append(
                ['{'+d.var_type.upper()+'}', u'{} ({})'.format(d.var_type, count), u'{} ({})'.format(d.var_type, count)]
            )
    else:
        for d in lists:
            count = redis.hget(settings.COMMON_VAR_COUNT_HASH, key=d.var_type)
            count = int(count) if count else 0
            title = u"公共变量"
            data.append(
                ['{'+d.var_type.upper()+'}', u'{} ({})'.format(d.name, count), u'{} ({})'.format(d.name, count)]
            )
    return {
        "title": title,
        "data": data,
    }

## 退订/订阅
def getUnsubscibes(lang_code, user_id, template_id):
    data = []
    namelist = ['notview_unsub_complaint_zh', 'notview_unsub_complaint_tw', 'notview_unsub_complaint_en',
                'notview_unsub_complaint_ko', 'notview_unsub_complaint_ja', 'notview_unsub_complaint_ru']
    servicelist = Prefs.objects.filter(name__in=namelist).values_list('name', 'value')
    service_vlas = dict(servicelist)
    uri = getPicUrl()
    unsb_url = reverse("ajax_unsubscribe_or_complaints")
    view_url = reverse("ajax_view_template")
    kwargs = {}
    CANNOTVIEW_LINK = u"%s%s?r={RECIPIENTS}&f={FULLNAME}&s={SEND_ID}&t=%d" % (uri, view_url, int(template_id))
    UNSUBSCRIBE_LINK = u"%s%s?mailist={MAILLIST_ID}&recipents={RECIPIENTS}&mode=0" % (uri, unsb_url)
    COMPLAINT_LINK = u"%s%s?mailist={MAILLIST_ID}&recipents={RECIPIENTS}&mode=2&template_id=%d&user_id=%d&send_id={SEND_ID}&subject={SUBJECT_STRING}" % (uri, unsb_url, int(template_id), int(user_id))
    kwargs.update(CANNOTVIEW_LINK=CANNOTVIEW_LINK, UNSUBSCRIBE_LINK=UNSUBSCRIBE_LINK, COMPLAINT_LINK=COMPLAINT_LINK)
    if lang_code == 'en-us':
        title = "Unsubscribe/Complaint"
    else:
        title = u"退订/投诉"
    for key in namelist:
        if key in service_vlas:
            value = safe_format(service_vlas[key], **kwargs)
            if key == "notview_unsub_complaint_zh":
                data.append([
                    value, u"退订/投诉（中文简体）", u"退订/投诉（中文简体）"
                ])
            if key == "notview_unsub_complaint_tw":
                data.append([
                    value, u"退订/投诉（中文繁体）", u"退订/投诉（中文繁体）"
                ])
            if key == "notview_unsub_complaint_en":
                data.append([
                    value, u"退订/投诉（英文）", u"退订/投诉（英文）"
                ])
            if key == "notview_unsub_complaint_ko":
                data.append([
                    value, u"退订/投诉（韩文）", u"退订/投诉（韩文）"
                ])
            if key == "notview_unsub_complaint_ja":
                data.append([
                    value, u"退订/投诉（日文）", u"退订/投诉（日文）"
                ])
            if key == "notview_unsub_complaint_ru":
                data.append([
                    value, u"退订/投诉（俄文）", u"退订/投诉（俄文）"
                ])
    return {
        "title": title,
        "data": data,
    }

def getShareLink(lang_code):
    if lang_code == 'en-us':
        title = "Share"
    else:
        title = u"社交媒体分享"
    uri = getPicUrl()
    url1 = "%s%s?r={RECIPIENTS}&f={FULLNAME}&s={SEND_ID}&t={TEMPLATE_ID}" % (uri, reverse("ck_share"))
    url2 = "{}/static/share/share.gif".format(uri)
    return {
        "title": title,
        "data": u'''<p style="text-align:center">
        <span style="display:inline;">点击图标轻松分享：
        <a href="{}" target="_blank"><img alt="" border="0" src="{}" style="outline: none;padding: 0px;margin: 0px;"/>
        </a></span></p>'''.format(url1, url2)
    }