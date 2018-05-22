#coding=utf-8
from django import forms

from django.utils.translation import ugettext_lazy as _

STATE_CHOICES = (
    ('', _(u'--')),
    ('analysis', _(u'系统分析中')),
    ('reject', _(u'系统已过滤')),
    ('dispatch', _(u'通道传输中')),
    ('c_reject', _(u'我已过滤')),
    ('rejects', _(u'所有已过滤')),
    ('send', _(u'正在出站')),
    ('retry', _(u'重试出站')),
    ('out_all', _(u'出站邮件')),
    ('fail_finished', _(u'出站失败')),
    ('finished', _(u'出站成功'))
)



class MailSearchForm(forms.Form):
    date = forms.DateField(label=_(u'指定日期'), required=False,
                                 widget=forms.DateInput(
                                     attrs={'class': 'dateinput', 'readonly': 'readonly', 'size': 10}))
    date_start = forms.DateField(label=_(u'开始日期'), required=False,
                                 widget=forms.DateInput(
                                     attrs={'class': 'dateinput', 'readonly': 'readonly', 'size': 10}))
    date_end = forms.CharField(label=_(u'结束日期'), required=False,
                           widget=forms.DateInput(attrs={'class': 'dateinput ', 'readonly': 'readonly', 'size': 10}))
    mail_from = forms.CharField(label=_(u'发件人'), max_length=100, required=False, widget=forms.TextInput(attrs={'size': 12}))
    mail_to = forms.CharField(label=_(u'收件人'), max_length=100, required=False, widget=forms.TextInput(attrs={'size': 12}))
    subject = forms.CharField(label=_(u'主题'), max_length=100, required=False)
    ip = forms.CharField(label=_(u'客户端IP'), max_length=50, required=False, widget=forms.TextInput(attrs={'size': 10}))
    state = forms.ChoiceField(label=_(u'状态'), required=False, choices=STATE_CHOICES)


class ActiveSenderForm(forms.Form):
    date = forms.CharField(label=_(u'日期'), required=False,
                           widget=forms.DateInput(attrs={'class': 'dateinput ', 'readonly': 'readonly', 'size': 20}))


class MailSummaryForm(forms.Form):
    date_start = forms.CharField(label=_(u'开始日期'), required=False,
                                 widget=forms.DateInput(attrs={'class': 'dateinput ', 'readonly': 'readonly', 'size': 20}))
    date_end = forms.CharField(label=_(u'结束日期'), required=False,
                               widget=forms.DateInput(attrs={'class': 'dateinput ', 'readonly': 'readonly', 'size': 20}))
