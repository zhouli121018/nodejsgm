# coding=utf-8
from django import forms

class QueueSearchForm(forms.Form):
    key = forms.CharField(label=u'KEY', required=False)
    sender = forms.CharField(label=u'发件人', required=False)
    recipients = forms.CharField(label=u'收件人', required=False)
    senderip = forms.CharField(label=u'发件IP', required=False)
