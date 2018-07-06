# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _

from app.core.models import CustomerDomain, CustomerMailbox, CustomerDomainMailboxRel, CustomerTrackDomain
from app.address.models import MailList
from app.template.models import SendTemplate
from app.task.models import SendTaskReplyto
from app.trigger.models import Trigger, TriggerAction, TriggerHoliday
from app.trigger.utils import const
from app.trigger.utils.fields import DatalistCharField, CustomerChoiceField
from app.core.models import MailBox
from app.trigger.utils.widgets import DatalistTextInput
from lib.tools import valid_domain


class TriggerForm(forms.ModelForm):
    """ 触发器 form
    """
    class Meta:
        model = Trigger
        fields = [
            "customer", "name", "type", "maillist_type",
            "trigger_maillists", "expire_type", "start_time", "end_time", "status"
        ]

    customer = forms.CharField(label=_(u'客户'), required=False, widget=forms.HiddenInput())
    type = forms.ChoiceField(label=_("触发器类型"), required=True, choices=const.TRIGGER_TYPE, widget=forms.Select(attrs={
        "class": "form-control chufa-type",
    }))
    maillist_type = forms.ChoiceField(label=_('作用的地址分类'), required=True, choices=const.MAILLIST_TYPE,
                                      widget=forms.Select(attrs={
                                          "onchange": "onchangeMailType()",
                                      }))
    expire_type = forms.ChoiceField(label=_('有效期'), required=True, choices=const.EXPIRE_TYPE,
                                    widget=forms.Select(attrs={
                                        "onchange": "onchangePermanent()",
                                    }))

    trigger_maillists = forms.ModelMultipleChoiceField(
        label=_(u'地址分类'),
        queryset=None,
        required=False,
        widget=forms.SelectMultiple(attrs={
            "class": "select2 ",
            "autocomplete": "off",
            "data-placeholder": _(u"点击选择地址分类,可多选"),
        }), help_text=_(u"可选多个地址分类"))
    start_time = forms.DateField(label=_(u'开始时间'), required=False, widget=forms.TextInput(attrs={
        "class": "dateinput ",
        'readonly': 'readonly',
        "data-date-format": "yyyy-mm-dd",
    }))
    end_time = forms.DateField(label=_(u'结束时间'), required=False, widget=forms.TextInput(attrs={
        "class": "dateinput ",
        'readonly': 'readonly',
        "data-date-format": "yyyy-mm-dd",
    }))

    def __init__(self, customer, *args, **kwargs):
        super(TriggerForm, self).__init__(*args, **kwargs)
        self.customer = customer
        self.fields['trigger_maillists'].queryset = MailList.objects.filter(
            customer=self.customer, isvalid=True, is_smtp=False).order_by("-id")

    def clean_customer(self):
        return self.customer


    def clean_start_time(self):
        expire_type = self.cleaned_data.get('expire_type')
        start_time = self.cleaned_data.get('start_time')
        if expire_type == 'custom':
            if not start_time:
                raise forms.ValidationError(_(u"请选择开始时间"))
        else:
            start_time = None
        return start_time

    def clean_end_time(self):
        expire_type = self.cleaned_data.get('expire_type')
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')
        if expire_type == 'custom':
            if not end_time:
                raise forms.ValidationError(_(u"请选择结束时间"))
            if start_time >= end_time:
                raise forms.ValidationError(_(u"开始时间不能大于结束时间"))
        else:
            end_time = None
        return end_time

    def clean_trigger_maillists(self):
        maillist_type = self.cleaned_data.get('maillist_type')
        trigger_maillists = self.cleaned_data.get('trigger_maillists')
        if maillist_type == 'part':
            if not trigger_maillists:
                raise forms.ValidationError(_(u"请选择地址分类"))
        else:
            trigger_maillists = []
        return trigger_maillists


class TriggerActionForm(forms.ModelForm):
    """ 触发器动作 form
    """

    class Meta:
        model = TriggerAction
        fields = [
            "action_name", "template", "send_acct_domain", "send_acct_address",
            "replyto", "sendname", "condition", "con_url", "con_url_template", "con_holiday", "con_holiday_date",
            "action_time", 'action_schedule', 'time_type'
        ]

    customer = forms.CharField(label=_(u'客户'), required=False, widget=forms.HiddenInput())
    trigger = forms.CharField(label=_(u'触发器'), required=False, widget=forms.HiddenInput())
    condition = forms.ChoiceField(label=_("触发条件"), required=True, choices=const.TRIGGER_CONDITION,
                                  widget=forms.Select(attrs={
                                      "onchange": "onchangeCondition()",
                                  }))
    con_holiday_date = forms.DateField(label=_(u'节假日日期'), required=False, widget=forms.TextInput(attrs={
        'readonly': 'readonly',
        "data-date-format": "yyyy-mm-dd",
    }), help_text=u"指定触发的节假日日期")
    action_schedule = forms.ChoiceField(label=_('触发时间'), required=True, choices=const.ACTION_SCHEDULE,
                                        widget=forms.Select(attrs={
                                            "onchange": "onchangeSchedule()",
                                        }))
    action_time = forms.IntegerField(label=_(u'触发时间'), required=False, widget=forms.TextInput(attrs={
        "class": "form-style",
        "value": "16"
    }))
    forms.Textarea
    con_url_template = forms.ModelChoiceField(
        label=_(u'选择模板'),
        queryset=None,
        required=False,
        widget=forms.Select(attrs={
            "class": "select2 js-example-basic-multiple choose-url",
            "autocomplete": "off",
            "data-placeholder": _(u"点击从模板中指定链接"),
        }))

    template = forms.ModelChoiceField(
        label=_(u'选择模板'),
        queryset=None,
        required=True,
        widget=forms.Select(attrs={
            "class": "select2 js-example-basic-multiple ",
            "autocomplete": "off",
            "data-placeholder": _(u"点击选择或输入查询"),
        }))
    send_acct_domain = forms.ChoiceField(
        label=_(u"选择域名"),
        required=False,
        help_text=_(u" "),
        widget=forms.Select(attrs={
            "onchange": "onchangeDomain(this.value)",
        }))
    send_acct_address = CustomerChoiceField(
        label=_(u"选择发件人"), required=True,
        help_text=_(u" "),
        widget=forms.Select(attrs={
            "onchange": "onchangeAddress(this.value)",
        }))
    """
    track_status = forms.ChoiceField(
        label=_(u"邮件跟踪"), required=True,
        choices=const.TRACK_STATUS,
        initial=0,
        help_text=_(u" "),
        widget=forms.Select(attrs={
            "onchange": "onchangeTrack(this.value)",
        }))
    track_domain = DatalistCharField(
        label=_(u"跟踪统计域名"), required=False,
        # choices=None,
        help_text=_(u"推荐使用自有域名，将该域名的CNAME记录指向count.bestedm.org；默认使用随机域名(xxx.count.bestedm.org) xxx为随机字符串"),
        widget=DatalistTextInput(attrs={
            "maxlength": "100",
            # "onblur": "checkDomain(this)",
            # "autocomplete": "off",
        }))
    """

    def __init__(self, customer, *args, **kwargs):
        super(TriggerActionForm, self).__init__(*args, **kwargs)
        self.customer = customer
        self.fields['template'].queryset = SendTemplate.objects.filter(
            user=self.customer, isvalid=True, result__in=['green', 'yellow', 'red_pass']
        ).order_by("-id")
        self.fields['con_url_template'].queryset = SendTemplate.objects.filter(
            user=self.customer, isvalid=True, result__in=['green', 'yellow', 'red_pass']
        ).order_by("-id")

        # 获取域名
        dlists = [("all", _("所有域名"))]
        domain_list = CustomerMailbox.objects.filter(
            customer=self.customer, disabled='0').values_list('domain', flat=True).distinct()
        domain_lists = CustomerDomain.objects.filter(domain__in=list(domain_list),
                                                     customer_id__in=[0, self.customer.id]).values_list("domain",
                                                                                                        "domain")
        # 共享域名获取
        ctype = CustomerDomainMailboxRel.objects.get_content_type('domain')
        share_domain_ids = CustomerDomainMailboxRel.objects.filter(customer=self.customer,
                                                                   content_type=ctype).values_list('object_id',
                                                                                                   flat=True)
        share_domain_lists = CustomerDomain.objects.filter(customer=self.customer.parent,
                                                           id__in=share_domain_ids).values_list("domain", "domain")
        dlists.extend(list(domain_lists))
        dlists.extend(list(share_domain_lists))
        self.fields['send_acct_domain'].choices = dlists

        # 获取发件人
        dlists = [("all", _("所有发件人"))]
        domain = self.initial.get('send_acct_domain', 'all')
        self.fields['send_acct_address'].choices = dlists
        data = list(MailBox.objects.filter(
        customer=customer, domain=domain, disabled='0'
        ).exclude(mailbox__isnull=True).values_list('mailbox', flat=True))
        if not data:
            ctype = CustomerDomainMailboxRel.objects.get_content_type('mailbox')
            box_ids = CustomerDomainMailboxRel.objects.filter(customer=customer, content_type=ctype).values_list(
                'object_id', flat=True)
            data = list(CustomerMailbox.objects.filter(
                customer=customer.parent, domain=domain, disabled='0', id__in=box_ids
            ).exclude(mailbox__isnull=True).values_list('mailbox', flat=True))
        for d in data:
            dlists.append((d, d))
        self.fields['send_acct_address'].choices = dlists
        _choices = [('', u'请选择节假日期')]

        for id, name, date in TriggerHoliday.objects.filter(date__gte=datetime.datetime.today()).values_list('id', 'name', 'date'):
            _choices.append((id, '{}({})'.format(name, date)))
        for id, name, date in TriggerHoliday.objects.filter(date__lt=datetime.datetime.today()).values_list('id', 'name', 'date'):
            _choices.append((id, '{}({})'.format(name, date)))
        self.fields['con_holiday'].choices = _choices
        # self.fields['con_holiday'].widget = forms.Select(attrs={"class": "con_holiday" })


        replyto_obj = SendTaskReplyto.objects.filter(user=self.customer).first()
        self.fields['replyto'].initial = replyto_obj.send_replyto if replyto_obj else ""

        # 获取跟踪域名
        # tracklist = CustomerTrackDomain.objects.filter(customer=self.customer).order_by('-id').values_list("domain", "domain")
        # self.fields['track_domain'].choices = tracklist
        # self.fields['track_domain'].initial = tracklist[0][0] if tracklist and tracklist[0] else ""

    def clean_customer(self):
        return self.customer

    def clean_con_holiday(self):
        condition = self.cleaned_data.get('condition')
        con_holiday = self.cleaned_data.get('con_holiday')
        if condition == "holiday":
            if not con_holiday:
                raise forms.ValidationError(_(u"请选择日期"))
        else:
            con_holiday = None
        return con_holiday


"""
    def clean_track_domain(self):
        domain = self.cleaned_data.get('track_domain')
        if domain:
            if domain in ('comingchina.com', 'magvision.com', 'bestedm.org'):
                raise forms.ValidationError(_(u"不能添加本平台域名：comingchina.com，magvision.com，bestedm.org。"))
            r = re.compile(r'.*?(\.comingchina.com|\.magvision.com|\.bestedm.org)$')
            if r.search(domain):
                raise forms.ValidationError(_(u"不能添加本平台域名：comingchina.com，magvision.com，bestedm.org。"))
            r = ( valid_domain(domain, 'cname', record='count1.bestedm.org') or
                  valid_domain(domain, 'cname', record='count.bestedm.org') )
            if not r:
                raise forms.ValidationError(_(u"该域名未解析到系统域名"))
        return domain
"""
