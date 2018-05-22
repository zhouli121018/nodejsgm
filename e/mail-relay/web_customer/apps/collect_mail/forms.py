# coding=utf-8
import re
from django import forms
from apps.mail.models import SenderWhitelist, CustomerSenderBlacklist, CollectRecipientWhitelist, SpamRptBlacklist
from django.utils.translation import ugettext_lazy as _


class SenderWhitelistForm(forms.ModelForm):
    customer = forms.CharField(label=_(u'客户'), required=False,
                               widget=forms.HiddenInput())

    def __init__(self, customer, *args, **kwargs):
        super(SenderWhitelistForm, self).__init__(*args, **kwargs)
        self.customer = customer

    def clean_sender(self):
        data = self.cleaned_data['sender'].lower().strip()
        is_regex = self.data.get('is_regex', '')

        if SenderWhitelist.objects.exclude(id=self.instance.id).filter(sender=data, customer=self.customer):
            raise forms.ValidationError(_(u"重复添加"))

        if is_regex:
            try:
                re.compile(data)
            except:
                raise forms.ValidationError(u"正则表达式解析错误, 文档参考:http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html")
        return data

    def clean_customer(self):
        return self.customer

    class Meta:
        model = SenderWhitelist
        exclude = ['is_global']


class CustomerSenderBlacklistForm(forms.ModelForm):
    customer = forms.CharField(label=_(u'客户'), required=False, widget=forms.HiddenInput())

    def __init__(self, customer, *args, **kwargs):
        super(CustomerSenderBlacklistForm, self).__init__(*args, **kwargs)
        self.customer = customer

    def clean_sender(self):
        data = self.cleaned_data['sender'].lower()
        is_regex = self.data.get('is_regex', '')

        if CustomerSenderBlacklist.objects.exclude(id=self.instance.id).filter(sender=data, customer=self.customer):
            raise forms.ValidationError(_(u"重复添加"))

        if is_regex:
            try:
                re.compile(data)
            except:
                raise forms.ValidationError(u"正则表达式解析错误, 文档参考:http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html")
        return data

    def clean_customer(self):
        return self.customer

    class Meta:
        model = CustomerSenderBlacklist
        exclude = ['is_global']


class CollectRecipientWhitelistForm(forms.ModelForm):
    customer = forms.CharField(label=_(u'客户'), required=False,
                               widget=forms.HiddenInput())

    def __init__(self, customer, *args, **kwargs):
        super(CollectRecipientWhitelistForm, self).__init__(*args, **kwargs)
        self.customer = customer

    def clean_keyword(self):
        data = self.cleaned_data['keyword'].lower().strip()
        col_domains = self.customer.col_domain.filter(disabled=False).values_list('domain', flat=True)
        if data.split('@')[-1] not in col_domains:
            raise forms.ValidationError(_(u"添加失败，您需添加自己域名下的邮箱账号：(%(col_domains)s)") % {'col_domains': ', '.join(col_domains)})

        if SenderWhitelist.objects.exclude(id=self.instance.id).filter(sender=data, customer=self.customer):
            raise forms.ValidationError(_(u"重复添加"))

        return data

    def clean_customer(self):
        return self.customer

    class Meta:
        model = CollectRecipientWhitelist
        exclude = []

class SpamRptBlacklistForm(forms.ModelForm):
    customer = forms.CharField(label=_(u'客户'), required=False,
                               widget=forms.HiddenInput())

    def __init__(self, customer, *args, **kwargs):
        super(SpamRptBlacklistForm, self).__init__(*args, **kwargs)
        self.customer = customer

    def clean_recipient(self):
        data = self.cleaned_data['recipient']
        if SpamRptBlacklist.objects.exclude(id=self.instance.id).filter(recipient=data, customer=self.customer):
            raise forms.ValidationError(u"重复添加")

        return data

    def clean_customer(self):
        return self.customer

    class Meta:
        model = SpamRptBlacklist
        exclude = ['created', 'operate_time']

