# coding=utf-8
from django import forms
from models import MAIL_STATE, MAIL_ORIGIN

class MailBaseSearchForm(forms.Form):
    date = forms.DateField(label=u'日期', required=False,
                           widget=forms.DateInput(attrs={'class': 'dateinput', 'readonly': 'readonly', 'size': 10}))
    mail_from = forms.CharField(label=u'发件人', max_length=100, required=False, widget=forms.TextInput(attrs={'size':12}))
    mail_to = forms.CharField(label=u'收件人', max_length=100, required=False, widget=forms.TextInput(attrs={'size':12}))
    subject = forms.CharField(label=u'主题', max_length=100, required=False, widget=forms.TextInput(attrs={'size':12}))
    customers = forms.CharField(label=u'客户', max_length=100, required=False, widget=forms.TextInput(attrs={'size':12}))
    origin = forms.ChoiceField(label=u'来源', choices=MAIL_ORIGIN, required=False)
    show = forms.CharField(label=u'客户', max_length=100, required=False, widget=forms.HiddenInput())


class MailSearchForm(MailBaseSearchForm):
    reviewer = forms.CharField(label=u'审核人', max_length=100, required=False, widget=forms.TextInput(attrs={'size':12}))
    state = forms.ChoiceField(label=u'状态', choices=MAIL_STATE, required=False)

