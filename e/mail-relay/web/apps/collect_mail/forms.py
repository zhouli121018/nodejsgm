# coding=utf-8
import re

from django import forms
from models import KeywordBlacklist, SubjectKeywordBlacklist, CheckSettings, Settings, CHECK_RESULT, MAIL_STATE, \
    REVIEW_RESULT, FAIL_OR_SUCCESS, HighRiskFlag, ERROR_TYPE, DSPAM_STUDY, MAIL_SERVERS, SenderCredit, SenderCreditSettings


class KeywordBlacklistForm(forms.ModelForm):
    def clean_keyword(self):

        data = self.cleaned_data['keyword']
        if KeywordBlacklist.objects.filter(keyword=data, disabled=False):
            raise forms.ValidationError(u"重复添加")
        try:
            re.compile(data)
        except:
            raise forms.ValidationError(u"正则表达式解析错误, 文档参考:http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html")

        return data

    class Meta:
        model = KeywordBlacklist
        exclude = ['created', 'hits']


class SubjectKeywordBlacklistForm(forms.ModelForm):
    def clean_keyword(self):

        data = self.cleaned_data['keyword']
        if SubjectKeywordBlacklist.objects.filter(keyword=data, disabled=False):
            raise forms.ValidationError(u"重复添加")
        try:
            re.compile(data)
        except:
            raise forms.ValidationError(u"正则表达式解析错误, 文档参考:http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html")

        return data

    class Meta:
        model = SubjectKeywordBlacklist
        exclude = ['created', 'hits']


class MailBaseSearchForm(forms.Form):
    date_start = forms.DateField(label=u'开始日期', required=False,
                                 widget=forms.DateInput(
                                     attrs={'class': 'dateinput', 'readonly': 'readonly', 'size': 12}))
    date = forms.DateField(label=u'结束日期', required=False,
                           widget=forms.DateInput(attrs={'class': 'dateinput', 'readonly': 'readonly', 'size': 10}))
    time_start = forms.TimeField(label=u'开始时间', required=False,
                                 widget=forms.DateInput(
                                     attrs={'class': 'dateinput2', 'readonly': 'readonly', 'size': 12}))
    time_end = forms.TimeField(label=u'结束时间', required=False,
                           widget=forms.DateInput(attrs={'class': 'dateinput2', 'readonly': 'readonly', 'size': 10}))
    mail_from = forms.CharField(label=u'发件人', max_length=100, required=False, widget=forms.TextInput(attrs={'size':12}))
    mail_to = forms.CharField(label=u'收件人', max_length=100, required=False, widget=forms.TextInput(attrs={'size':12}))
    subject = forms.CharField(label=u'主题', max_length=100, required=False, widget=forms.TextInput(attrs={'size':12}))
    customers = forms.CharField(label=u'客户', max_length=100, required=False, widget=forms.TextInput(attrs={'size':12}))
    check = forms.ChoiceField(label=u'检测状态', choices=CHECK_RESULT, required=False)
    show = forms.CharField(label=u'客户', max_length=100, required=False, widget=forms.HiddenInput())
    client_ip = forms.IPAddressField(label=u'客户端IP', max_length=50, required=False, widget=forms.TextInput(attrs={'size':12}))
    all_day = forms.CharField(label=u'全部日期', max_length=100, required=False, widget=forms.HiddenInput())
    server_id = forms.ChoiceField(label=u'服务器', choices=MAIL_SERVERS, required=False)


class MailSearchForm(MailBaseSearchForm):
    filter_word = forms.CharField(label=u'关键词过滤', max_length=100, required=False, widget=forms.TextInput(attrs={'size':12}))
    reviewer = forms.CharField(label=u'审核人', max_length=100, required=False, widget=forms.TextInput(attrs={'size':12}))
    state = forms.ChoiceField(label=u'状态', choices=MAIL_STATE, required=False)
    review = forms.ChoiceField(label=u'审核状态', choices=REVIEW_RESULT, required=False)
    send = forms.ChoiceField(label=u'发送状态', choices=FAIL_OR_SUCCESS, required=False)
    error_type = forms.ChoiceField(label=u'错误类型', choices=ERROR_TYPE, required=False)
    dspam_study = forms.ChoiceField(label=u'Dsapm学习', choices=DSPAM_STUDY, required=False)


class CheckSettingsForm(forms.ModelForm):
    class Meta:
        model = CheckSettings
        exclude = []


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        exclude = []


class DateSearchForm(forms.Form):
    date = forms.DateField(label=u'日期', required=False,
                           widget=forms.DateInput(attrs={'class': 'dateinput', 'readonly': 'readonly', 'size': 10}))


class HighRiskFlagForm(forms.ModelForm):
    class Meta:
        model = HighRiskFlag
        exclude = []

class SenderCreditSettingsForm(forms.ModelForm):
    class Meta:
        model = SenderCreditSettings
        exclude = []


class SenderCreditForm(forms.ModelForm):
    class Meta:
        model = SenderCredit
        exclude = ['sender', 'update_time']


class SenderCreditBaseSearchForm(forms.Form):
    sender = forms.CharField(label=u'发件人', required=False)
